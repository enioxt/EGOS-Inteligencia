import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import "@/i18n";

vi.mock("@/api/client", () => ({
  getSharedInvestigation: vi.fn(),
}));

vi.mock("@/stores/auth", () => ({
  useAuthStore: (selector: (state: { token: string | null }) => unknown) =>
    selector({ token: "token" }),
}));

const mockForkInvestigation = vi.fn();

vi.mock("@/stores/investigation", () => ({
  useInvestigationStore: (selector: (state: { forkInvestigation: typeof mockForkInvestigation }) => unknown) =>
    selector({ forkInvestigation: mockForkInvestigation }),
}));

import { getSharedInvestigation } from "@/api/client";
import { SharedInvestigation } from "./SharedInvestigation";

const mockGetSharedInvestigation = vi.mocked(getSharedInvestigation);

function renderSharedInvestigation(token = "abc-123") {
  return render(
    <MemoryRouter initialEntries={[`/shared/${token}`]}>
      <Routes>
        <Route path="/shared/:token" element={<SharedInvestigation />} />
        <Route path="/app/pesquisas/:investigationId" element={<div>Fork target</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("SharedInvestigation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading state initially", () => {
    mockGetSharedInvestigation.mockReturnValue(new Promise(() => {}));
    renderSharedInvestigation();

    expect(screen.getByText("Carregando...")).toBeInTheDocument();
  });

  it("shows investigation data after successful fetch", async () => {
    mockGetSharedInvestigation.mockResolvedValue({
      id: "inv-1",
      title: "Investiga\u00E7\u00E3o Teste",
      description: "Uma descri\u00E7\u00E3o",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
      entity_ids: ["12345678901", "e2"],
      share_token: "abc-123",
      annotations: [
        {
          id: "ann-1",
          entity_id: "12345678901",
          investigation_id: "inv-1",
          text: "Anota\u00E7\u00E3o relevante",
          created_at: "2026-01-01T00:00:00Z",
        },
      ],
      tags: [
        {
          id: "tag-1",
          investigation_id: "inv-1",
          name: "Urgente",
          color: "#E07A2F",
        },
      ],
    });

    renderSharedInvestigation();

    await waitFor(() => {
      expect(screen.getByText("Investiga\u00E7\u00E3o Teste")).toBeInTheDocument();
    });

    expect(screen.getByText("Uma descri\u00E7\u00E3o")).toBeInTheDocument();
    expect(screen.getAllByText("***.***.***.01")).toHaveLength(2);
    expect(screen.getByText("e2")).toBeInTheDocument();
    expect(screen.getByText("Anota\u00E7\u00E3o relevante")).toBeInTheDocument();
    expect(screen.getByText("Urgente")).toBeInTheDocument();
  });

  it("shows error message when fetch fails", async () => {
    mockGetSharedInvestigation.mockRejectedValue(new Error("Not found"));

    renderSharedInvestigation();

    await waitFor(() => {
      expect(
        screen.getByText("Pesquisa compartilhada n\u00E3o encontrada."),
      ).toBeInTheDocument();
    });
  });

  it("forks a shared investigation for authenticated users", async () => {
    const user = userEvent.setup();
    mockGetSharedInvestigation.mockResolvedValue({
      id: "inv-1",
      title: "Investiga\u00E7\u00E3o Teste",
      description: "Uma descri\u00E7\u00E3o",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
      entity_ids: ["e1"],
      share_token: "abc-123",
      annotations: [],
      tags: [],
    });
    mockForkInvestigation.mockResolvedValue({
      investigation: {
        id: "forked",
        title: "Copy",
        description: "",
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

    renderSharedInvestigation();

    const button = await screen.findByRole("button", { name: /Continuar desta pesquisa/i });
    await user.click(button);

    await waitFor(() => {
      expect(mockForkInvestigation).toHaveBeenCalledWith("abc-123");
    });
  });
});
