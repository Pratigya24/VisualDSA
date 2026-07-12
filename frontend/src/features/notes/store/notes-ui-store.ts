import { create } from "zustand";

interface NotesUIState {
  selectedNoteId: string | null;
  isComposingNew: boolean;
  selectNote: (id: string | null) => void;
  startComposing: () => void;
}

export const useNotesUIStore = create<NotesUIState>((set) => ({
  selectedNoteId: null,
  isComposingNew: false,
  selectNote: (id) => set({ selectedNoteId: id, isComposingNew: false }),
  startComposing: () => set({ selectedNoteId: null, isComposingNew: true }),
}));
