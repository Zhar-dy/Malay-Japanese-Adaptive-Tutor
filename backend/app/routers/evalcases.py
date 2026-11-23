"""GET /api/eval/cases: the 10 evaluation cases (for Lecturer Evaluation Mode)."""
from fastapi import APIRouter, HTTPException, Request

from backend.app.services import cases

router = APIRouter(prefix="/api/eval")


@router.get("/cases")
def list_cases(request: Request):
    return request.app.state.cases


@router.get("/cases/{case_id}")
def get_one_case(case_id: str, request: Request):
    case = cases.get_case(request.app.state.cases, case_id)
    if case is None:
        raise HTTPException(404, f"Unknown case: {case_id}")
    return case