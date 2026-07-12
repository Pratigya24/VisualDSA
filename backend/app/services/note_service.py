from beanie import PydanticObjectId

from app.core.exceptions import NotFoundError
from app.models.analytics_event import AnalyticsEventType
from app.models.note import Note
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.note_repository import NoteRepository
from app.schemas.note import NoteCreateRequest, NoteResponse, NoteUpdateRequest


def _to_response(note: Note) -> NoteResponse:
    return NoteResponse(
        id=str(note.id),
        title=note.title,
        content_md=note.content_md,
        algorithm_id=str(note.algorithm_id) if note.algorithm_id else None,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


class NoteService:
    def __init__(self, note_repository: NoteRepository, analytics_repository: AnalyticsRepository) -> None:
        self._notes = note_repository
        self._analytics = analytics_repository

    async def list_for_user(self, user_id: PydanticObjectId, *, search: str | None) -> list[NoteResponse]:
        notes = await self._notes.list_for_user(user_id, search=search)
        return [_to_response(note) for note in notes]

    async def create(self, user_id: PydanticObjectId, payload: NoteCreateRequest) -> NoteResponse:
        note = Note(
            user_id=user_id,
            algorithm_id=PydanticObjectId(payload.algorithm_id) if payload.algorithm_id else None,
            title=payload.title,
            content_md=payload.content_md,
        )
        await self._notes.create(note)
        await self._analytics.record(user_id, AnalyticsEventType.NOTE_CREATED, {"note_id": str(note.id)})
        return _to_response(note)

    async def update(
        self, user_id: PydanticObjectId, note_id: PydanticObjectId, payload: NoteUpdateRequest
    ) -> NoteResponse:
        note = await self._notes.get(user_id, note_id)
        if note is None:
            raise NotFoundError("Note not found.")
        note = await self._notes.update(note, title=payload.title, content_md=payload.content_md)
        return _to_response(note)

    async def delete(self, user_id: PydanticObjectId, note_id: PydanticObjectId) -> None:
        note = await self._notes.get(user_id, note_id)
        if note is None:
            raise NotFoundError("Note not found.")
        await self._notes.delete(note)
