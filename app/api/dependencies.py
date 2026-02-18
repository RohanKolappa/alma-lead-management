from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.email import ConsoleEmailBackend, EmailBackend
from app.core.storage import LocalStorageBackend, StorageBackend
from app.database import async_session_factory
from app.repositories.lead_repository import LeadRepository
from app.services.auth_service import verify_token
from app.services.lead_service import LeadService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


def get_storage() -> StorageBackend:
    return LocalStorageBackend(settings.UPLOAD_DIR)


def get_email() -> EmailBackend:
    return ConsoleEmailBackend()


async def get_lead_service(
    db: AsyncSession = Depends(get_db),
    storage: StorageBackend = Depends(get_storage),
    email: EmailBackend = Depends(get_email),
) -> LeadService:
    repo = LeadRepository(db)
    return LeadService(repo=repo, storage=storage, email=email)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    return verify_token(token)
