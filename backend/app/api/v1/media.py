"""
Media Static File Router
"""
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.dependencies.music import get_storage_service
from app.services.music.storage import StorageService

router = APIRouter(prefix="/media", tags=["Media"])


@router.get("/{file_path:path}")
async def serve_media_file(
    file_path: str,
    storage: StorageService = Depends(get_storage_service),
) -> FileResponse:
    full_path = storage.resolve_path(file_path)
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="Media file not found.")

    return FileResponse(full_path)
