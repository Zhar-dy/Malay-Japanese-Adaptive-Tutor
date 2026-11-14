"""API tests with Ollama and the grammar index faked: no model or index needed."""
from contextlib import closing
import dataclasses
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from urllib import error

from fastapi.testclient import TestClient

from backend.app import main

FAKE_INFO = {
    "config": {"model": "embeddinggemma:300m", "format": "embeddinggemma-retrieval-v1"},
    "complete": True,
    "dimensions": 3,
}


def fake_entry(name, level, vector):
    return {
        "id": f"openjlpt:grammar:{name}",
        "text": f"Grammar: {name}",
        "metadata": {"jlpt_level": level, "pattern": name, "source_url": "https://example.com"},
        "vector": vector,
    }


# Tiny 3-number vectors instead of 768. The fake question vector is [1, 0, 0],
# so "wa" (same direction) must always rank first.
FAKE_ENTRIES = [
    fake_entry("wa", "N5", [1.0, 0.0, 0.0]),
    fake_entry("o", "N5", [0.6, 0.8, 0.0]),
    fake_entry("kara", "N4", [0.0, 0.0, 1.0]),
]


class ApiTest(unittest.TestCase):
    def setUp(self):
        # Write logs to a temporary folder, never to the real data/app/tutor.sqlite3.
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(self.tmp.cleanup)
        self.db_path = Path(self.tmp.name) / "tutor.sqlite3"
        self.settings = dataclasses.replace(main.settings, app_db_path=self.db_path)

        # Every request the app sends to Ollama is recorded here instead of being sent.
        self.ollama_calls = []
        patches = [
            mock.patch.object(main, "settings", self.settings),
            mock.patch("backend.app.rag_adapter.load_index", return_value=(FAKE_INFO, FAKE_ENTRIES)),
            mock.patch("backend.app.rag_adapter.embed_question", return_value=[1.0, 0.0, 0.0]),
            mock.patch("backend.app.ollama_client.call", side_effect=self.fake_ollama),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

        # Entering the client runs lifespan (index load + init_db), like a real server start.
        self.client = TestClient(main.app)
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def fake_ollama(self, base_url, endpoint, payload=None, timeout=300):
        self.ollama_calls.append((endpoint, payload))
        if endpoint == "tags":
            return {"models": [
                {"name": self.settings.llm_model, "model": self.settings.llm_model, "digest": "llm-digest"},
                {"name": "embeddinggemma:300m", "model": "embeddinggemma:300m", "digest": "embed-digest"},
            ]}
        if endpoint == "chat":
            return {
                "model": self.settings.llm_model,
                "message": {"role": "assistant", "content": "Partikel wa menandakan topik [S1]."},
                "done_reason": "stop",
                "eval_count": 12,
            }
        raise AssertionError(f"Unexpected Ollama endpoint: {endpoint}")

    # ---------- /api/health ----------

    def test_health_is_ok_with_fake_ollama_and_index(self):
        data = self.client.get("/api/health").json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["index"]["entries"], 3)
        self.assertTrue(data["ollama"]["models"][self.settings.llm_model]["installed"])

    # ---------- /api/search ----------

    def test_search_ranks_closest_entry_first(self):
        response = self.client.post("/api/search", json={"query": "wa?", "level": "N5", "top_k": 2})
        self.assertEqual(response.status_code, 200)
        hits = response.json()["hits"]
        self.assertEqual([h["chunk_id"] for h in hits], ["openjlpt:grammar:wa", "openjlpt:grammar:o"])
        self.assertEqual(hits[0]["ref"], "S1")
        self.assertNotIn("vector", hits[0])  # vectors must never reach the browser

    def test_search_at_or_below_includes_easier_levels(self):
        response = self.client.post(
            "/api/search", json={"query": "x", "level": "N4", "level_mode": "at_or_below"})
        data = response.json()
        self.assertEqual(data["level_filter"], ["N5", "N4"])
        self.assertEqual(len(data["hits"]), 3)

    def test_search_rejects_bad_input(self):
        for body in ({"query": "x", "level": "N9"},
                     {"query": "x", "top_k": 21},
                     {"query": "   "}):
            with self.subTest(body=body):
                self.assertEqual(self.client.post("/api/search", json=body).status_code, 422)

    def test_search_with_no_matching_level_is_404(self):
        response = self.client.post("/api/search", json={"query": "x", "level": "N1"})
        self.assertEqual(response.status_code, 404)

    def test_ollama_down_gives_503(self):
        with mock.patch("backend.app.rag_adapter.embed_question",
                        side_effect=error.URLError("connection refused")):
            response = self.client.post("/api/search", json={"query": "x"})
        self.assertEqual(response.status_code, 503)

    # ---------- /api/ask ----------

    def test_ask_sends_think_at_top_level_to_api_chat(self):
        response = self.client.post("/api/ask", json={"question": "Apakah wa?", "level": "N5"})
        self.assertEqual(response.status_code, 200)

        chat_payloads = [payload for endpoint, payload in self.ollama_calls if endpoint == "chat"]
        self.assertEqual(len(chat_payloads), 1)  # exactly one LLM call, to /api/chat
        payload = chat_payloads[0]
        self.assertIs(payload["think"], False)         # rule 2: top level
        self.assertNotIn("think", payload["options"])  # ... and NOT inside options
        self.assertEqual(payload["keep_alive"], self.settings.llm_keep_alive)
        self.assertEqual(payload["options"]["num_predict"], 512)

    def test_ask_returns_answer_sources_and_no_warnings(self):
        data = self.client.post("/api/ask", json={"question": "Apakah wa?", "level": "N5"}).json()
        self.assertIn("[S1]", data["answer"])
        self.assertEqual(data["sources"][0]["chunk_id"], "openjlpt:grammar:wa")
        self.assertEqual(data["warnings"], [])
        self.assertEqual(data["model_digest"], "llm-digest")
        self.assertTrue(data["item_id"])

    def test_ask_is_logged_to_sqlite(self):
        item_id = self.client.post("/api/ask", json={"question": "Apakah wa?"}).json()["item_id"]
        with closing(sqlite3.connect(self.db_path)) as db:
            rows = db.execute("SELECT event, learner_text FROM turns WHERE item_id = ?",
                              (item_id,)).fetchall()
        self.assertEqual(rows, [("ask", "Apakah wa?")])

    def test_ask_allows_at_most_3_sources(self):
        response = self.client.post("/api/ask", json={"question": "x", "top_k": 4})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()