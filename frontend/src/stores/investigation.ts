import { create } from "zustand";

import type {
  Annotation,
  Investigation,
  InvestigationImportResult,
  Tag,
} from "@/api/client";
import * as api from "@/api/client";

interface InvestigationState {
  // State
  activeInvestigationId: string | null;
  investigations: Investigation[];
  annotations: Annotation[];
  tags: Tag[];
  loading: boolean;
  error: string | null;

  // Actions
  setActiveInvestigation: (id: string | null) => void;
  fetchInvestigations: () => Promise<void>;
  createInvestigation: (title: string, description?: string) => Promise<Investigation>;
  importInvestigation: (file: File) => Promise<InvestigationImportResult>;
  forkInvestigation: (token: string, title?: string) => Promise<InvestigationImportResult>;
  deleteInvestigation: (id: string) => Promise<void>;
  updateInvestigation: (id: string, data: { title?: string; description?: string }) => Promise<void>;
  addEntity: (investigationId: string, entityId: string) => Promise<void>;
  removeEntity: (investigationId: string, entityId: string) => Promise<void>;
  fetchAnnotations: (investigationId: string) => Promise<void>;
  addAnnotation: (investigationId: string, entityId: string, text: string) => Promise<void>;
  deleteAnnotation: (investigationId: string, annotationId: string) => Promise<void>;
  fetchTags: (investigationId: string) => Promise<void>;
  addTag: (investigationId: string, name: string, color?: string) => Promise<void>;
  deleteTag: (investigationId: string, tagId: string) => Promise<void>;
}

export const useInvestigationStore = create<InvestigationState>((set, get) => ({
  activeInvestigationId: null,
  investigations: [],
  annotations: [],
  tags: [],
  loading: false,
  error: null,

  setActiveInvestigation: (id) => set({ activeInvestigationId: id }),

  fetchInvestigations: async () => {
    set({ loading: true, error: null });
    try {
      const res = await api.listInvestigations();
      set({ investigations: res.investigations, loading: false });
    } catch {
      set({ error: "investigation.loadError", loading: false });
    }
  },

  createInvestigation: async (title, description) => {
    const inv = await api.createInvestigation(title, description);
    set((s) => ({ investigations: [inv, ...s.investigations] }));
    return inv;
  },

  importInvestigation: async (file) => {
    const result = await api.importInvestigation(file);
    set((s) => ({ investigations: [result.investigation, ...s.investigations] }));
    return result;
  },

  forkInvestigation: async (token, title) => {
    const result = await api.forkSharedInvestigation(token, title);
    set((s) => ({ investigations: [result.investigation, ...s.investigations] }));
    return result;
  },

  deleteInvestigation: async (id) => {
    await api.deleteInvestigation(id);
    const state = get();
    set({
      investigations: state.investigations.filter((i) => i.id !== id),
      activeInvestigationId:
        state.activeInvestigationId === id ? null : state.activeInvestigationId,
    });
  },

  updateInvestigation: async (id, data) => {
    const updated = await api.updateInvestigation(id, data);
    set((s) => ({
      investigations: s.investigations.map((i) => (i.id === id ? updated : i)),
    }));
  },

  addEntity: async (investigationId, entityId) => {
    await api.addEntityToInvestigation(investigationId, entityId);
    const updated = await api.getInvestigation(investigationId);
    set((s) => ({
      investigations: s.investigations.map((i) =>
        i.id === investigationId ? updated : i,
      ),
    }));
  },

  removeEntity: async (investigationId, entityId) => {
    await api.removeEntityFromInvestigation(investigationId, entityId);
    const updated = await api.getInvestigation(investigationId);
    set((s) => ({
      investigations: s.investigations.map((i) =>
        i.id === investigationId ? updated : i,
      ),
    }));
  },

  fetchAnnotations: async (investigationId) => {
    try {
      const annotations = await api.listAnnotations(investigationId);
      set({ annotations });
    } catch {
      set({ annotations: [] });
    }
  },

  addAnnotation: async (investigationId, entityId, text) => {
    const annotation = await api.createAnnotation(investigationId, entityId, text);
    set((s) => ({ annotations: [...s.annotations, annotation] }));
  },

  deleteAnnotation: async (investigationId, annotationId) => {
    await api.deleteAnnotation(investigationId, annotationId);
    set((s) => ({ annotations: s.annotations.filter((a) => a.id !== annotationId) }));
  },

  fetchTags: async (investigationId) => {
    try {
      const tags = await api.listTags(investigationId);
      set({ tags });
    } catch {
      set({ tags: [] });
    }
  },

  addTag: async (investigationId, name, color) => {
    const tag = await api.createTag(investigationId, name, color);
    set((s) => ({ tags: [...s.tags, tag] }));
  },

  deleteTag: async (investigationId, tagId) => {
    await api.deleteTag(investigationId, tagId);
    set((s) => ({ tags: s.tags.filter((t) => t.id !== tagId) }));
  },
}));
