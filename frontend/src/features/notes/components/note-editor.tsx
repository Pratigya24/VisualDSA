import { Trash2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { useNotesUIStore } from "@/features/notes/store/notes-ui-store";
import type { Note } from "@/features/notes/types";
import { useCreateNote, useDeleteNote, useUpdateNote } from "@/features/notes/hooks/use-notes";
import { Button } from "@/shared/components/button";

const AUTOSAVE_DELAY_MS = 800;

interface NoteEditorProps {
  note: Note | undefined;
  isComposingNew: boolean;
}

export function NoteEditor({ note, isComposingNew }: NoteEditorProps) {
  const [title, setTitle] = useState(note?.title ?? "");
  const [contentMd, setContentMd] = useState(note?.contentMd ?? "");
  const [savedAt, setSavedAt] = useState<Date | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const createNote = useCreateNote();
  const updateNote = useUpdateNote();
  const deleteNote = useDeleteNote();
  const selectNote = useNotesUIStore((state) => state.selectNote);

  useEffect(() => {
    setTitle(note?.title ?? "");
    setContentMd(note?.contentMd ?? "");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [note?.id]);

  useEffect(() => {
    if (isComposingNew && !title && !contentMd) return;

    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      if (isComposingNew) {
        createNote.mutate(
          { title: title || "Untitled", contentMd },
          {
            onSuccess: (created) => {
              selectNote(created.id);
              setSavedAt(new Date());
            },
          },
        );
      } else if (note && (title !== note.title || contentMd !== note.contentMd)) {
        updateNote.mutate(
          { id: note.id, title: title || "Untitled", contentMd },
          { onSuccess: () => setSavedAt(new Date()) },
        );
      }
    }, AUTOSAVE_DELAY_MS);

    return () => clearTimeout(timeoutRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [title, contentMd]);

  if (!note && !isComposingNew) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-ink-muted">
        Select a note, or create a new one.
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col">
      <div className="flex items-center justify-between border-b border-canvas-border px-4 py-2">
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Untitled"
          aria-label="Note title"
          className="flex-1 bg-transparent font-display text-lg font-semibold text-ink outline-none placeholder:text-ink-faint"
        />
        <div className="flex items-center gap-3">
          <span className="text-xs text-ink-faint">
            {createNote.isPending || updateNote.isPending
              ? "Saving…"
              : savedAt
                ? `Saved ${savedAt.toLocaleTimeString()}`
                : ""}
          </span>
          {note && (
            <Button
              variant="ghost"
              size="icon"
              aria-label="Delete note"
              onClick={() => {
                deleteNote.mutate(note.id);
                selectNote(null);
              }}
            >
              <Trash2 className="h-4 w-4 text-signal-danger" aria-hidden />
            </Button>
          )}
        </div>
      </div>
      <textarea
        value={contentMd}
        onChange={(event) => setContentMd(event.target.value)}
        placeholder="Write in markdown…"
        aria-label="Note content"
        className="flex-1 resize-none bg-transparent p-4 font-mono text-sm text-ink outline-none placeholder:text-ink-faint"
      />
    </div>
  );
}
