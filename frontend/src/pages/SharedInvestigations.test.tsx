import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import "@/i18n";

vi.mock("@/api/client", () => ({
  listSharedInvestigations: vi.fn(),
}));

import { listSharedInvestigations } from "@/api/client";
import { SharedInvestigations } from "./SharedInvestigations";

const mockListSharedInvestigations = vi.mocked(listSharedInvestigations);

describe("SharedInvestigations", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders shared investigations from the public gallery", async () => {
    mockListSharedInvestigations.mockResolvedValue({
      investigations: [
        {
          id: "inv-1",
          title: "Pesquisa pública",
          description: "Resumo",
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-02T00:00:00Z",
          entity_ids: ["e1", "e2"],
          share_token: "token-1",
        },
      ],
      total: 1,
    });

    render(
      <MemoryRouter>
        <SharedInvestigations />
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText("Pesquisa pública")).toBeInTheDocument();
    });

    expect(screen.getByText("Resumo")).toBeInTheDocument();
  });
});
