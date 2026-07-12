import { useState } from "react";

import { NoteEditor } from "@/features/notes/components/note-editor";
import { NoteListPanel } from "@/features/notes/components/note-list-panel";
import { useNotes } from "@/features/notes/hooks/use-notes";
import { useNotesUIStore } from "@/features/notes/store/notes-ui-store";

export function NotesPage() {
  const [search, setSearch] = useState("");
  const { data: notes, isLoading, isError, refetch } = useNotes(search);
  const selectedNoteId = useNotesUIStore((state) => state.selectedNoteId);
  const isComposingNew = useNotesUIStore((state) => state.isComposingNew);

  const selectedNote = notes?.find((note) => note.id === selectedNoteId);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center" aria-hidden>
        <div className="h-6 w-6 animate-pulse-trace rounded-full bg-trace" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3">
        <p className="text-sm text-signal-danger">Couldn&apos;t load your notes.</p>
        <button type="button" onClick={() => refetch()} className="text-sm font-medium text-trace hover:underline">
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      <NoteListPanel notes={notes ?? []} search={search} onSearchChange={setSearch} />
      <NoteEditor note={selectedNote} isComposingNew={isComposingNew} />
    </div>
  );
}
