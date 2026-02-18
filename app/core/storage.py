"""File storage abstraction.

StorageBackend defines the interface for persisting uploaded files.
LocalStorageBackend writes to the local filesystem — swap in an S3 or GCS
implementation by providing any class that satisfies the Protocol.
"""

import uuid
from pathlib import Path
from typing import Protocol, runtime_checkable

import aiofiles
from fastapi import UploadFile


@runtime_checkable
class StorageBackend(Protocol):
    """Protocol for file storage implementations."""

    async def save(self, file: UploadFile, filename: str) -> str:
        """Persist *file* and return its relative stored path."""
        ...

    async def get_path(self, filename: str) -> Path:
        """Return the absolute filesystem path for a stored file."""
        ...

    async def delete(self, filename: str) -> None:
        """Remove a previously stored file."""
        ...


class LocalStorageBackend:
    """Stores uploads on the local filesystem under *upload_dir*."""

    def __init__(self, upload_dir: str) -> None:
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile, filename: str) -> str:
        ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4().hex}{ext}"
        dest = self.upload_dir / unique_name

        async with aiofiles.open(dest, "wb") as f:
            while chunk := await file.read(1024 * 64):
                await f.write(chunk)

        return unique_name

    async def get_path(self, filename: str) -> Path:
        return self.upload_dir / filename

    async def delete(self, filename: str) -> None:
        path = self.upload_dir / filename
        path.unlink(missing_ok=True)
