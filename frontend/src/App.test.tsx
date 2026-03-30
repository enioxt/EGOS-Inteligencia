import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { describe, expect, it, vi } from "vitest";

import "./i18n";

const authState = {
  token: null as string | null,
  user: null,
  restore: () => Promise.resolve(),
};

vi.mock("./pages/SharedInvestigations", () => ({
  SharedInvestigations: () => <div>Shared gallery stub</div>,
}));

// Mock auth store — unauthenticated by default
vi.mock("./stores/auth", () => ({
  useAuthStore: Object.assign(
    (selector?: (state: Record<string, unknown>) => unknown) => {
      return selector ? selector(authState) : authState;
    },
    {
      getState: () => authState,
    },
  ),
}));

import { App } from "./App";

describe("App", () => {
  it("keeps /shared reachable for authenticated users", () => {
    authState.token = "token";

    render(
      <MemoryRouter initialEntries={["/shared"]}>
        <App />
      </MemoryRouter>,
    );

    expect(screen.getByText("Shared gallery stub")).toBeInTheDocument();
    authState.token = null;
  });

  it("renders the landing page with title", () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getAllByText("EGOS Inteligência")).not.toHaveLength(0);
  });

  it("renders login page at /login", () => {
    render(
      <MemoryRouter initialEntries={["/login"]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByLabelText(/e-mail/i)).toBeInTheDocument();
  });
});
