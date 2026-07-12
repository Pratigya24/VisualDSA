import { apiClient } from "@/services/api-client";
import type { Note } from "@/features/notes/types";

interface NoteDTO {
  id: string;
  title: string;
  content_md: string;
  algorithm_id: string | null;
  created_at: string;
  updated_at: string;
}

function toNote(dto: NoteDTO): Note {
  return {
    id: dto.id,
    title: dto.title,
    contentMd: dto.content_md,
    algorithmId: dto.algorithm_id,
    createdAt: dto.created_at,
    updatedAt: dto.updated_at,
  };
}

export async function listNotes(search?: string): Promise<Note[]> {
  const response = await apiClient.get<NoteDTO[]>("/notes", { params: { search } });
  return response.data.map(toNote);
}

export async function createNote(payload: { title: string; contentMd: string }): Promise<Note> {
  const response = await apiClient.post<NoteDTO>("/notes", {
    title: payload.title,
    content_md: payload.contentMd,
  });
  return toNote(response.data);
}

export async function updateNote(
  id: string,
  payload: { title: string; contentMd: string },
): Promise<Note> {
  const response = await apiClient.patch<NoteDTO>(`/notes/${id}`, {
    title: payload.title,
    content_md: payload.contentMd,
  });
  return toNote(response.data);
}

export async function deleteNote(id: string): Promise<void> {
  await apiClient.delete(`/notes/${id}`);
}
