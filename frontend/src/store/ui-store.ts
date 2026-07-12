import { create } from "zustand";

/**
 * App-shell UI state only.
 *
 * Per the State Management Strategy (architecture §13): this store holds
 * ephemeral, client-only state that has no server representation. Anything
 * that originates from the API belongs in a TanStack Query cache inside the
 * owning feature module, never here. Feature-specific UI state (e.g. the
 * visualizer's current scrub index) belongs in that feature's own Zustand
 * slice under `features/<feature>/store/`, not in this root store — this
 * store is reserved for state shared by the app shell itself (sidebar,
 * command palette, global toasts).
 */
interface UIState {
  isSidebarCollapsed: boolean;
  isCommandPaletteOpen: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  openCommandPalette: () => void;
  closeCommandPalette: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  isSidebarCollapsed: false,
  isCommandPaletteOpen: false,
  toggleSidebar: () =>
    set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed })),
  setSidebarCollapsed: (collapsed) => set({ isSidebarCollapsed: collapsed }),
  openCommandPalette: () => set({ isCommandPaletteOpen: true }),
  closeCommandPalette: () => set({ isCommandPaletteOpen: false }),
}));
