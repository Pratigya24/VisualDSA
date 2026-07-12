import { Plus } from "lucide-react";

import type { Note } from "@/features/notes/types";
import { useNotesUIStore } from "@/features/notes/store/notes-ui-store";
import { Button } from "@/shared/components/button";
import { Input } from "@/shared/components/input";
import { cn } from "@/shared/utils/cn";

interface NoteListPanelProps {
  notes: Note[];
  search: string;
  onSearchChange: (value: string) => void;
}

export function NoteListPanel({ notes, search, onSearchChange }: NoteListPanelProps) {
  const selectedNoteId = useNotesUIStore((state) => state.selectedNoteId);
  const selectNote = useNotesUIStore((state) => state.selectNote);
  const startComposing = useNotesUIStore((state) => state.startComposing);

  return (
    <div className="flex h-full w-72 shrink-0 flex-col border-r border-canvas-border">
      <div className="space-y-2 border-b border-canvas-border p-3">
        <Button size="sm" className="w-full" onClick={startComposing}>
          <Plus className="h-4 w-4" aria-hidden />
          New note
        </Button>
        <Input
          placeholder="Search notes…"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          aria-label="Search notes"
        />
      </div>
      <ul className="flex-1 overflow-y-auto">
        {notes.length === 0 && (
          <li className="p-4 text-center text-sm text-ink-muted">No notes yet.</li>
        )}
        {notes.map((note) => (
          <li key={note.id}>
            <button
              type="button"
              onClick={() => selectNote(note.id)}
              className={cn(
                "block w-full border-b border-canvas-border px-3 py-3 text-left transition-colors hover:bg-canvas-overlay",
                selectedNoteId === note.id && "bg-canvas-overlay",
              )}
            >
              <p className="truncate text-sm font-medium text-ink">{note.title || "Untitled"}</p>
              <p className="mt-0.5 truncate text-xs text-ink-faint">
                {new Date(note.updatedAt).toLocaleDateString()}
              </p>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
