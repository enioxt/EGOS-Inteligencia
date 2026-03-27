import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { apiFetch } from "./client";

describe("apiFetch", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    localStorage.clear();
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("does not set content-type on bodiless requests", async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await apiFetch("/api/v1/shared");

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = new Headers(init.headers);

    expect(headers.has("Content-Type")).toBe(false);
  });

  it("sets content-type for json bodies", async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await apiFetch("/api/v1/investigations/", {
      method: "POST",
      body: JSON.stringify({ title: "Test" }),
    });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = new Headers(init.headers);

    expect(headers.get("Content-Type")).toBe("application/json");
  });
});
