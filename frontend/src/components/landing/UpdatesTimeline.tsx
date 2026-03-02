import { useEffect, useState } from "react";

interface UpdateEntry {
  date: string;
  title: string;
  summary: string;
  sections?: { title: string; icon: string; content: string }[];
  links?: Record<string, string>;
  metrics?: Record<string, string | number>;
  tags?: string[];
}

const TAG_COLORS: Record<string, string> = {
  feature: "#22c55e",
  infrastructure: "#3b82f6",
  data: "#a855f7",
  ai: "#f59e0b",
  governance: "#ef4444",
  bugfix: "#f97316",
};

export function UpdatesTimeline() {
  const [updates, setUpdates] = useState<UpdateEntry[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    const files = ["2026-03-02"];
    Promise.all(
      files.map((f) =>
        fetch(`/updates/${f}.json`)
          .then((r) => (r.ok ? r.json() : null))
          .catch(() => null)
      )
    ).then((results) => {
      setUpdates(results.filter(Boolean).sort((a: UpdateEntry, b: UpdateEntry) => b.date.localeCompare(a.date)));
    });
  }, []);

  if (updates.length === 0) return null;

  return (
    <section
      style={{
        padding: "3rem 1.5rem",
        maxWidth: 900,
        margin: "0 auto",
      }}
    >
      <span
        style={{
          display: "block",
          fontSize: "0.75rem",
          textTransform: "uppercase",
          letterSpacing: "0.1em",
          color: "#94a3b8",
          marginBottom: "0.5rem",
        }}
      >
        Atualizacoes
      </span>
      <h2
        style={{
          fontSize: "1.5rem",
          fontWeight: 700,
          color: "#f1f5f9",
          marginBottom: "1.5rem",
        }}
      >
        Linha do Tempo
      </h2>

      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {updates.map((u) => (
          <div
            key={u.date}
            style={{
              background: "rgba(30,41,59,0.7)",
              border: "1px solid rgba(71,85,105,0.4)",
              borderRadius: 12,
              padding: "1.25rem",
              cursor: "pointer",
              transition: "border-color 0.2s",
            }}
            onClick={() => setExpanded(expanded === u.date ? null : u.date)}
            onMouseEnter={(e) => (e.currentTarget.style.borderColor = "#3b82f6")}
            onMouseLeave={(e) => (e.currentTarget.style.borderColor = "rgba(71,85,105,0.4)")}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <span style={{ fontSize: "0.75rem", color: "#64748b" }}>{u.date}</span>
                <h3 style={{ fontSize: "1rem", fontWeight: 600, color: "#e2e8f0", margin: "0.25rem 0" }}>
                  {u.title}
                </h3>
              </div>
              <span style={{ color: "#64748b", fontSize: "1.25rem" }}>
                {expanded === u.date ? "\u25B2" : "\u25BC"}
              </span>
            </div>

            {u.tags && (
              <div style={{ display: "flex", gap: "0.375rem", flexWrap: "wrap", marginTop: "0.5rem" }}>
                {u.tags.map((tag) => (
                  <span
                    key={tag}
                    style={{
                      fontSize: "0.625rem",
                      padding: "0.125rem 0.5rem",
                      borderRadius: 999,
                      background: `${TAG_COLORS[tag] || "#475569"}20`,
                      color: TAG_COLORS[tag] || "#94a3b8",
                      border: `1px solid ${TAG_COLORS[tag] || "#475569"}40`,
                    }}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}

            <p style={{ fontSize: "0.875rem", color: "#94a3b8", margin: "0.5rem 0 0" }}>
              {u.summary}
            </p>

            {expanded === u.date && u.sections && (
              <div style={{ marginTop: "1rem", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                {u.sections.map((s) => (
                  <div
                    key={s.title}
                    style={{
                      background: "rgba(15,23,42,0.5)",
                      borderRadius: 8,
                      padding: "0.75rem 1rem",
                    }}
                  >
                    <h4 style={{ fontSize: "0.875rem", fontWeight: 600, color: "#e2e8f0", marginBottom: "0.25rem" }}>
                      {s.title}
                    </h4>
                    <p style={{ fontSize: "0.8125rem", color: "#94a3b8", lineHeight: 1.5, margin: 0 }}>
                      {s.content}
                    </p>
                  </div>
                ))}

                {u.links && (
                  <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "0.5rem" }}>
                    {u.links.report && (
                      <a
                        href={u.links.report}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          fontSize: "0.75rem",
                          padding: "0.375rem 0.75rem",
                          borderRadius: 6,
                          background: "#1e40af",
                          color: "#fff",
                          textDecoration: "none",
                        }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        Ver Relatorio
                      </a>
                    )}
                    {u.links.github && (
                      <a
                        href={u.links.github}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          fontSize: "0.75rem",
                          padding: "0.375rem 0.75rem",
                          borderRadius: 6,
                          background: "rgba(71,85,105,0.3)",
                          color: "#94a3b8",
                          textDecoration: "none",
                          border: "1px solid rgba(71,85,105,0.4)",
                        }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        GitHub
                      </a>
                    )}
                    {u.links.faq && (
                      <a
                        href={u.links.faq}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          fontSize: "0.75rem",
                          padding: "0.375rem 0.75rem",
                          borderRadius: 6,
                          background: "rgba(71,85,105,0.3)",
                          color: "#94a3b8",
                          textDecoration: "none",
                          border: "1px solid rgba(71,85,105,0.4)",
                        }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        FAQ
                      </a>
                    )}
                    {u.links.telegram_bot && (
                      <a
                        href={u.links.telegram_bot}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          fontSize: "0.75rem",
                          padding: "0.375rem 0.75rem",
                          borderRadius: 6,
                          background: "rgba(71,85,105,0.3)",
                          color: "#94a3b8",
                          textDecoration: "none",
                          border: "1px solid rgba(71,85,105,0.4)",
                        }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        Telegram Bot
                      </a>
                    )}
                  </div>
                )}

                {u.metrics && (
                  <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginTop: "0.5rem" }}>
                    {Object.entries(u.metrics).map(([k, v]) => (
                      <div key={k} style={{ textAlign: "center" }}>
                        <span style={{ fontSize: "1.125rem", fontWeight: 700, color: "#e2e8f0" }}>
                          {typeof v === "number" ? v.toLocaleString("pt-BR") : v}
                        </span>
                        <span style={{ display: "block", fontSize: "0.625rem", color: "#64748b", textTransform: "uppercase" }}>
                          {k.replace(/_/g, " ")}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
