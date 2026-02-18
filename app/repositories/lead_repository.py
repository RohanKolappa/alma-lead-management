from __future__ import annotations

import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead, LeadStatus


class LeadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, lead_data: dict, resume_path: str) -> Lead:
        lead = Lead(**lead_data, resume_path=resume_path)
        self.db.add(lead)
        await self.db.commit()
        await self.db.refresh(lead)
        return lead

    async def get_by_id(self, lead_id: uuid.UUID) -> Lead | None:
        result = await self.db.execute(select(Lead).where(Lead.id == lead_id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 50) -> tuple[list[Lead], int]:
        count_result = await self.db.execute(select(func.count()).select_from(Lead))
        total = count_result.scalar_one()

        rows_result = await self.db.execute(
            select(Lead).order_by(Lead.created_at.desc()).offset(skip).limit(limit)
        )
        leads = list(rows_result.scalars().all())

        return leads, total

    async def update_status(self, lead_id: uuid.UUID, status: LeadStatus) -> Lead | None:
        lead = await self.get_by_id(lead_id)
        if lead is None:
            return None
        lead.status = status
        await self.db.commit()
        await self.db.refresh(lead)
        return lead
