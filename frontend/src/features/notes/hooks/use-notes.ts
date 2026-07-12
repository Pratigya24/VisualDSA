import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createNote, deleteNote, listNotes, updateNote } from "@/features/notes/api/notes-api";

export function useNotes(search?: string) {
  return useQuery({
    queryKey: ["notes", search ?? ""],
    queryFn: () => listNotes(search),
    placeholderData: (previous) => previous,
  });
}

export function useCreateNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createNote,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notes"] }),
  });
}

export function useUpdateNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, title, contentMd }: { id: string; title: string; contentMd: string }) =>
      updateNote(id, { title, contentMd }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notes"] }),
  });
}

export function useDeleteNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteNote,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["notes"] }),
  });
}
