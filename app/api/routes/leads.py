import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError

from app.api.dependencies import get_current_user, get_lead_service
from app.schemas.lead import LeadCreate, LeadListResponse, LeadResponse, LeadStatusUpdate
from app.services.lead_service import LeadService

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def _validate_resume(file: UploadFile) -> None:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    if file.size is not None and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )


# ---------------------------------------------------------------------------
# PUBLIC
# ---------------------------------------------------------------------------


@router.post(
    "/",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new lead",
    description="Public endpoint. Accepts prospect information and a resume file.",
)
async def create_lead(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    service: LeadService = Depends(get_lead_service),
) -> LeadResponse:
    _validate_resume(resume)
    try:
        data = LeadCreate(first_name=first_name, last_name=last_name, email=email)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors())
    lead = await service.submit_lead(data, resume)
    return LeadResponse.model_validate(lead)


# ---------------------------------------------------------------------------
# INTERNAL (authenticated)
# ---------------------------------------------------------------------------


@router.get(
    "/",
    response_model=LeadListResponse,
    summary="List all leads",
    description="Returns a paginated list of leads. Requires authentication.",
)
async def list_leads(
    skip: int = 0,
    limit: int = 50,
    _user: dict = Depends(get_current_user),
    service: LeadService = Depends(get_lead_service),
) -> LeadListResponse:
    leads, total = await service.list_leads(skip=skip, limit=limit)
    return LeadListResponse(
        items=[LeadResponse.model_validate(l) for l in leads],
        count=total,
    )


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
    summary="Get a single lead",
    description="Returns lead details by ID. Requires authentication.",
)
async def get_lead(
    lead_id: uuid.UUID,
    _user: dict = Depends(get_current_user),
    service: LeadService = Depends(get_lead_service),
) -> LeadResponse:
    lead = await service.get_lead(lead_id)
    return LeadResponse.model_validate(lead)


@router.patch(
    "/{lead_id}/status",
    response_model=LeadResponse,
    summary="Update lead status",
    description="Mark a lead as REACHED_OUT. Returns 409 if already in that state. Requires authentication.",
)
async def update_lead_status(
    lead_id: uuid.UUID,
    body: LeadStatusUpdate,
    _user: dict = Depends(get_current_user),
    service: LeadService = Depends(get_lead_service),
) -> LeadResponse:
    lead = await service.mark_reached_out(lead_id)
    return LeadResponse.model_validate(lead)
