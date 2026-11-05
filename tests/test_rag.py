"""Unit tests for the OpenJLPT grammar RAG pipeline."""
import json
from pathlib import Path
import sqlite3
import sys
import unittest

# Ensure scripts/rag can be imported at runtime
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "rag"))

from search_grammar_index import rank_entries
from ask_grammar_tutor import citation_warnings, parse_ollama_tutor_response


class TestGrammarRAG(unittest.TestCase):

    def test_01_sqlite_index_integrity(self):
        """Verify the SQLite index exists and contains 526 grammar records."""
        db_path = ROOT / "data" / "indexes" / "grammar.sqlite3"
        self.assertTrue(db_path.exists(), f"Index file missing at {db_path}")

        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            # Table name is 'chunks'
            count = cur.execute("SELECT count(*) FROM chunks").fetchone()[0]
            self.assertEqual(count, 526, f"Expected 526 grammar entries, found {count}")

            # Verify metadata
            metadata = {k: json.loads(v) for k, v in cur.execute("SELECT key, value FROM metadata").fetchall()}
            self.assertTrue(metadata.get("complete"), "Index is not marked complete")
            self.assertEqual(metadata.get("dimensions"), 768)
            self.assertEqual(metadata["config"]["model"], "embeddinggemma:300m")

    def test_02_cosine_ranking(self):
        """Verify cosine similarity ranking logic on known orthogonal/identical vectors."""
        entries = [
            {"id": "doc1", "vector": [1.0, 0.0], "metadata": {"jlpt_level": "N5"}, "text": "A"},
            {"id": "doc2", "vector": [0.0, 1.0], "metadata": {"jlpt_level": "N5"}, "text": "B"},
            {"id": "doc3", "vector": [0.7071, 0.7071], "metadata": {"jlpt_level": "N5"}, "text": "C"},
        ]
        # Query aligned with doc1
        hits = rank_entries([1.0, 0.0], entries, top_k=2)
        self.assertEqual(hits[0]["id"], "doc1")
        self.assertAlmostEqual(hits[0]["score"], 1.0, places=4)
        self.assertEqual(hits[1]["id"], "doc3")

    def test_03_citation_warnings(self):
        """Verify citation validator catches missing, valid, and out-of-range markers."""
        # Valid citations
        warnings = citation_warnings("Penjelasan partikel [S1] dan [S2].", source_count=2)
        self.assertEqual(len(warnings), 0)

        # Missing citations
        warnings_missing = citation_warnings("Penjelasan tanpa sebarang rujukan.", source_count=2)
        self.assertTrue(any("No [S1]-style" in w for w in warnings_missing))

        # Out-of-bounds citations (e.g. references S4 when only 3 sources provided)
        warnings_oob = citation_warnings("Rujukan tidak sah [S4].", source_count=3)
        self.assertTrue(any("not supplied" in w for w in warnings_oob))

    def test_04_defensive_think_parser(self):
        """Verify parser removes inline <think> tags and handles unclosed tags."""
        # Case A: Complete inline thinking block
        payload_closed = {
            "message": {
                "content": "<think>\nDeliberating in English...\n</think>\nJawapan tutor [S1].",
                "thinking": ""
            },
            "done_reason": "stop"
        }
        res = parse_ollama_tutor_response(payload_closed)
        self.assertEqual(res["answer"], "Jawapan tutor [S1].")
        self.assertEqual(res["thinking"], "Deliberating in English...")
        self.assertFalse(res["truncated"])

        # Case B: Unclosed think block (hit token limit mid-thought)
        payload_unclosed = {
            "message": {
                "content": "<think>\nCutting off before finishing reasoning",
                "thinking": ""
            },
            "done_reason": "length"
        }
        res_unclosed = parse_ollama_tutor_response(payload_unclosed)
        self.assertEqual(res_unclosed["answer"], "")
        self.assertTrue(res_unclosed["truncated"])


if __name__ == "__main__":
    unittest.main()