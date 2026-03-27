import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { Investigation } from "@/api/client";

import "../../i18n";

// Mock the store before importing the component
const mockStore: {
  investigations: Investigation[];
  activeInvestigationId: string | null;
  loading: boolean;
  fetchInvestigations: ReturnType<typeof vi.fn>;
  createInvestigation: ReturnType<typeof vi.fn>;
  importInvestigation: ReturnType<typeof vi.fn>;
  setActiveInvestigation: ReturnType<typeof vi.fn>;
} = {
  investigations: [],
  activeInvestigationId: null,
  loading: false,
  fetchInvestigations: vi.fn(),
  createInvestigation: vi.fn(),
  importInvestigation: vi.fn(),
  setActiveInvestigation: vi.fn(),
};

vi.mock("@/stores/investigation", () => ({
  useInvestigationStore: () => mockStore,
}));

import { InvestigationPanel } from "./InvestigationPanel";

describe("InvestigationPanel", () => {
  beforeEach(() => {
    mockStore.investigations = [];
    mockStore.activeInvestigationId = null;
    mockStore.loading = false;
    mockStore.fetchInvestigations.mockReset();
    mockStore.createInvestigation.mockReset();
    mockStore.importInvestigation.mockReset();
    mockStore.setActiveInvestigation.mockReset();
  });

  it("renders 'New Investigation' button", () => {
    render(<InvestigationPanel />);
    expect(screen.getByText(/Nova pesquisa/i)).toBeDefined();
  });

  it("renders investigation title when provided", () => {
    mockStore.investigations = [
      {
        id: "inv-1",
        title: "Test Investigation",
        description: "desc",
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
        entity_ids: ["e1", "e2"],
        share_token: null,
      },
    ];

    render(<InvestigationPanel />);
    expect(screen.getByText("Test Investigation")).toBeDefined();
  });

  it("shows empty message when no investigations", () => {
    mockStore.investigations = [];

    render(<InvestigationPanel />);
    expect(screen.getByText(/Nenhuma pesquisa/i)).toBeDefined();
  });

  it("calls fetchInvestigations on mount", () => {
    render(<InvestigationPanel />);
    expect(mockStore.fetchInvestigations).toHaveBeenCalled();
  });

  it("imports a research bundle from json", async () => {
    const user = userEvent.setup();
    mockStore.importInvestigation.mockResolvedValue({
      investigation: {
        id: "inv-imported",
        title: "Importada",
        description: "desc",
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
        entity_ids: [],
        share_token: null,
      },
      imported_entities: 0,
      skipped_entity_ids: [],
      imported_annotations: 0,
      imported_tags: 0,
    });

    render(<InvestigationPanel />);

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(['{"ok":true}'], "investigation.json", { type: "application/json" });

    await user.upload(input, file);

    await waitFor(() => {
      expect(mockStore.importInvestigation).toHaveBeenCalledWith(file);
    });
    await waitFor(() => {
      expect(mockStore.setActiveInvestigation).toHaveBeenCalledWith("inv-imported");
    });
  });

  it("rejects non-json files before upload", async () => {
    const user = userEvent.setup({ applyAccept: false });

    render(<InvestigationPanel />);

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(["%PDF-1.4"], "investigation.pdf", { type: "application/pdf" });

    await user.upload(input, file);

    expect(mockStore.importInvestigation).not.toHaveBeenCalled();
    expect(
      await screen.findByText("Use um arquivo JSON exportado da pesquisa."),
    ).toBeInTheDocument();
  });

  it("rejects malformed json before upload", async () => {
    const user = userEvent.setup();

    render(<InvestigationPanel />);

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(["{"], "investigation.json", { type: "application/json" });

    await user.upload(input, file);

    expect(mockStore.importInvestigation).not.toHaveBeenCalled();
    expect(
      await screen.findByText("O arquivo JSON da pesquisa é inválido."),
    ).toBeInTheDocument();
  });
});
