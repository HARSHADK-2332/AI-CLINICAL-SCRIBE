from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import DemoRequest
from backend.schemas import DemoRequestCreate, DemoRequestResponse

router = APIRouter(prefix="/api/demo-requests", tags=["Demo Requests"])


@router.post("", response_model=DemoRequestResponse, status_code=status.HTTP_201_CREATED)
def submit_demo_request(
    req: DemoRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Submits and stores a commercial demo request into SQLite.
    Validates work email, organization, and professional role without third-party dependencies.
    """
    demo_entry = DemoRequest(
        name=req.name,
        email=req.email,
        organization=req.organization,
        role=req.role,
        message=req.message or ""
    )
    db.add(demo_entry)
    db.commit()
    db.refresh(demo_entry)

    return DemoRequestResponse(
        id=demo_entry.id,
        status="received",
        message="Demo request submitted successfully. A care specialist will follow up shortly."
    )
