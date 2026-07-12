from typing import Annotated

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, get_note_service
from app.models.user import User
from app.schemas.note import NoteCreateRequest, NoteResponse, NoteUpdateRequest
from app.services.note_service import NoteService

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[NoteResponse])
async def list_notes(
    current_user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends(get_note_service)],
    search: Annotated[str | None, Query(max_length=100)] = None,
) -> list[NoteResponse]:
    return await note_service.list_for_user(current_user.id, search=search)


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: NoteCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> NoteResponse:
    return await note_service.create(current_user.id, payload)


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    payload: NoteUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> NoteResponse:
    return await note_service.update(current_user.id, PydanticObjectId(note_id), payload)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    note_service: Annotated[NoteService, Depends(get_note_service)],
) -> None:
    await note_service.delete(current_user.id, PydanticObjectId(note_id))
