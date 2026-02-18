from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator, model_validator

from app.models.lead import LeadStatus


class LeadCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class LeadResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    resume_url: str
    status: LeadStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="wrap")
    @classmethod
    def _from_orm(cls, data, handler):
        if hasattr(data, "resume_path"):
            data = dict(
                id=data.id,
                first_name=data.first_name,
                last_name=data.last_name,
                email=data.email,
                resume_url=f"/uploads/{data.resume_path}",
                status=data.status,
                created_at=data.created_at,
                updated_at=data.updated_at,
            )
        return handler(data)


class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    count: int


class LeadStatusUpdate(BaseModel):
    status: LeadStatus

    @field_validator("status")
    @classmethod
    def status_must_be_reached_out(cls, v: LeadStatus) -> LeadStatus:
        if v != LeadStatus.REACHED_OUT:
            raise ValueError("Status can only be updated to REACHED_OUT")
        return v
