"""FastAPI endpoint for the post-checkup AI.

To enable it, add to main.py:
    from PostCheckup_AI.router import router as post_checkup_router
    app.include_router(post_checkup_router)
"""

from fastapi import APIRouter, HTTPException, status

from PostCheckup_AI.sample_data import SAMPLE_NOTES
from PostCheckup_AI.summarizer import PostCheckupAI

router = APIRouter(prefix="/post-checkup", tags=["Post checkup"])


@router.get("/{visit_id}/summary")
def get_summary(visit_id: str):
    """Returns the original doctor summary, the easy summary and the action plan."""
    # TODO: replace the sample data with the real doctor-note table.
    note = SAMPLE_NOTES.get(visit_id)
    if note is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No doctor note found for this visit.")
    try:
        ai = PostCheckupAI(note)
    except RuntimeError as error:  # missing GEMINI_API_KEY
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(error))
    return ai.build_report().to_dict()
