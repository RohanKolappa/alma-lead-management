from __future__ import annotations

import logging
import uuid

from fastapi import HTTPException, UploadFile

from app.config import settings
from app.core.email import (
    EmailBackend,
    attorney_notification_email,
    prospect_confirmation_email,
)
from app.core.storage import StorageBackend
from app.models.lead import Lead, LeadStatus
from app.repositories.lead_repository import LeadRepository
from app.schemas.lead import LeadCreate

logger = logging.getLogger(__name__)


class LeadService:
    def __init__(
        self,
        repo: LeadRepository,
        storage: StorageBackend,
        email: EmailBackend,
    ):
        self.repo = repo
        self.storage = storage
        self.email = email

    async def submit_lead(self, data: LeadCreate, resume: UploadFile) -> Lead:
        resume_path = await self.storage.save(resume, resume.filename or "upload.pdf")

        lead = await self.repo.create(
            lead_data=data.model_dump(),
            resume_path=resume_path,
        )

        try:
            subj, body = prospect_confirmation_email(lead.first_name)
            await self.email.send(to=lead.email, subject=subj, body=body)
        except Exception:
            logger.exception("Failed to send confirmation email to %s", lead.email)

        try:
            subj, body = attorney_notification_email(
                lead.first_name, lead.last_name, lead.email,
            )
            await self.email.send(to=settings.ATTORNEY_EMAIL, subject=subj, body=body)
        except Exception:
            logger.exception("Failed to send attorney notification for lead %s", lead.id)

        return lead

    async def get_lead(self, lead_id: uuid.UUID) -> Lead:
        lead = await self.repo.get_by_id(lead_id)
        if lead is None:
            raise HTTPException(status_code=404, detail="Lead not found")
        return lead

    async def list_leads(self, skip: int = 0, limit: int = 50) -> tuple[list[Lead], int]:
        return await self.repo.get_all(skip=skip, limit=limit)

    async def mark_reached_out(self, lead_id: uuid.UUID) -> Lead:
        lead = await self.repo.get_by_id(lead_id)
        if lead is None:
            raise HTTPException(status_code=404, detail="Lead not found")
        if lead.status == LeadStatus.REACHED_OUT:
            raise HTTPException(status_code=409, detail="Lead already marked as REACHED_OUT")

        lead = await self.repo.update_status(lead_id, LeadStatus.REACHED_OUT)
        return lead
