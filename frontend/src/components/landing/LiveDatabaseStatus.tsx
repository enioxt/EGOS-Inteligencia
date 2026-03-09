import type { StatsResponse } from "@/api/client";

function formatCount(n: number): string {
  if (n >= 1_000_000) return `${(Math.round(n / 100_000) / 10).toFixed(1)}M`;
  if (n >= 1_000) return `${(Math.round(n / 100) / 10).toFixed(1)}K`;
  return String(n);
}

const DB_ROW_DEFS = [
  { label: "Empresas (CNPJ)", key: "company_count" as const, loadingThreshold: 1000 },
  { label: "Sanções (CEIS/CNEP/OpenSanctions)", key: "sanction_count" as const, loadingThreshold: 0 },
  { label: "Pessoas / Sócios", key: "person_count" as const, loadingThreshold: 100 },
  { label: "Contratos Públicos", key: "contract_count" as const, loadingThreshold: 0 },
  { label: "Financiamentos (BNDES)", key: "finance_count" as const, loadingThreshold: 0 },
  { label: "Saúde (DATASUS)", key: "health_count" as const, loadingThreshold: 0 },
  { label: "Embargos (IBAMA)", key: "embargo_count" as const, loadingThreshold: 0 },
];

export function LiveDatabaseStatus({ stats }: { stats: StatsResponse | null }) {
  if (!stats) return null;

  const rows = DB_ROW_DEFS
    .map((def) => ({
      label: def.label,
      count: stats[def.key] as number,
      loading: (stats[def.key] as number) < def.loadingThreshold,
    }))
    .filter((r) => r.count > 0 || r.loading);

  return (
    <section style={{
      padding: "clamp(3rem, 6vw, 5rem) 0",
      background: "linear-gradient(180deg, #090b0b 0%, #0a0b0c 100%)",
      borderTop: "1px solid rgba(255,255,255,0.06)",
    }}>
      <div style={{ width: "min(72rem, calc(100% - 4rem))", margin: "0 auto" }}>
        <div style={{
          display: "flex", alignItems: "center", gap: "0.6rem",
          marginBottom: "0.8rem",
          fontFamily: "var(--font-mono)", fontSize: "0.68rem", fontWeight: 500,
          letterSpacing: "0.12em", textTransform: "uppercase" as const,
          color: "rgba(148,163,154,0.9)",
        }}>
          <span style={{ width: "1.5rem", height: "1px", background: "rgba(0,229,195,0.72)" }} />
          STATUS EM TEMPO REAL
        </div>
        <h2 style={{
          fontFamily: "var(--font-display)", fontStyle: "italic", fontWeight: 400,
          fontSize: "clamp(1.6rem, 3.5vw, 2.4rem)", lineHeight: 1,
          letterSpacing: "-0.018em", color: "#f0f3f1",
          marginBottom: "clamp(1.5rem, 3vw, 2rem)",
        }}>
          Base de Dados
        </h2>
        <div style={{
          display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(16rem, 1fr))",
          gap: "0.6rem",
        }}>
          {rows.map((row) => (
            <div key={row.label} style={{
              display: "flex", justifyContent: "space-between", alignItems: "center",
              padding: "0.85rem 1.1rem",
              background: "#111416", border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "0.6rem",
            }}>
              <span style={{ fontSize: "0.85rem", color: "rgba(232,237,233,0.8)" }}>
                {row.label}
              </span>
              <span style={{
                fontFamily: "var(--font-mono)", fontSize: "0.85rem", fontWeight: 600,
                color: row.loading ? "rgba(234,179,8,0.9)" : "rgba(0,229,195,0.9)",
                display: "flex", alignItems: "center", gap: "0.4rem",
              }}>
                {row.loading && (
                  <span style={{
                    width: 6, height: 6, borderRadius: "50%",
                    background: "rgba(234,179,8,0.9)",
                    animation: "pulse 1.5s ease-in-out infinite",
                  }} />
                )}
                {row.count > 0 ? formatCount(row.count) : "Carregando..."}
              </span>
            </div>
          ))}
        </div>
        <p style={{
          marginTop: "1rem", fontSize: "0.78rem",
          color: "rgba(148,163,154,0.7)", fontFamily: "var(--font-mono)",
        }}>
          Total: {formatCount(stats.total_nodes)} entidades · {formatCount(stats.total_relationships)} conexões · Atualizado a cada visita
        </p>
      </div>
      <style>{`@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }`}</style>
    </section>
  );
}
