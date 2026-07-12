from datetime import datetime, timezone

from beanie import PydanticObjectId

from app.models.note import Note


class NoteRepository:
    async def list_for_user(self, user_id: PydanticObjectId, *, search: str | None = None) -> list[Note]:
        query: dict = {"user_id": user_id}
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"content_md": {"$regex": search, "$options": "i"}},
            ]
        return await Note.find(query).sort(-Note.updated_at).to_list()

    async def get(self, user_id: PydanticObjectId, note_id: PydanticObjectId) -> Note | None:
        note = await Note.get(note_id)
        if note is None or note.user_id != user_id:
            return None
        return note

    async def create(self, note: Note) -> Note:
        await note.insert()
        return note

    async def update(self, note: Note, *, title: str, content_md: str) -> Note:
        note.title = title
        note.content_md = content_md
        note.updated_at = datetime.now(timezone.utc)
        await note.save()
        return note

    async def delete(self, note: Note) -> None:
        await note.delete()
