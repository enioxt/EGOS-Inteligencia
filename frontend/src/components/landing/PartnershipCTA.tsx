interface InfraCost {
  monthly_usd: number;
  details: string;
}

const INFRA_COST_KEY = "bracc_infra_cost";
const DEFAULT_COST: InfraCost = { monthly_usd: 36, details: "VPS + domínio" };

function useInfraCost(): InfraCost {
  try {
    const raw = typeof window !== "undefined" ? localStorage.getItem(INFRA_COST_KEY) : null;
    if (raw) return JSON.parse(raw) as InfraCost;
  } catch { /* fallback */ }
  return DEFAULT_COST;
}

export function PartnershipCTA() {
  const cost = useInfraCost();

  return (
    <section style={{
      padding: "clamp(3rem, 6vw, 4.5rem) 0",
      background: "linear-gradient(135deg, rgba(30,58,95,0.3) 0%, rgba(30,27,75,0.3) 100%)",
      borderTop: "1px solid rgba(59,130,246,0.15)",
    }}>
      <div style={{
        width: "min(64rem, calc(100% - 4rem))", margin: "0 auto", textAlign: "center" as const,
      }}>
        <h2 style={{
          fontFamily: "var(--font-display)", fontStyle: "italic", fontWeight: 400,
          fontSize: "clamp(1.8rem, 4vw, 2.8rem)", lineHeight: 1,
          color: "#f0f3f1", marginBottom: "1rem",
        }}>
          Aberto a Parcerias
        </h2>
        <p style={{
          maxWidth: "38rem", margin: "0 auto 2rem", fontSize: "1rem",
          lineHeight: 1.6, color: "rgba(232,237,233,0.7)",
        }}>
          Pesquisadores, jornalistas, desenvolvedores, instituições, governos e universidades
          podem contribuir integrando novas bases de dados, criando pesquisas e expandindo o sistema.
          Quanto mais bases conectadas, mais poderoso o cruzamento.
        </p>
        <div style={{ display: "flex", gap: "0.8rem", justifyContent: "center", flexWrap: "wrap" as const }}>
          <a href="https://github.com/enioxt/EGOS-Inteligencia" target="_blank" rel="noopener noreferrer" style={{
            display: "inline-flex", alignItems: "center", padding: "0.75rem 1.8rem",
            background: "rgba(59,130,246,0.9)", color: "white", borderRadius: "0.6rem",
            textDecoration: "none", fontWeight: 600, fontSize: "0.9rem",
          }}>
            GitHub — Código e Roadmap
          </a>
          <a href="https://t.me/EthikIntelligence" target="_blank" rel="noopener noreferrer" style={{
            display: "inline-flex", alignItems: "center", padding: "0.75rem 1.8rem",
            background: "transparent", color: "rgba(232,237,233,0.9)",
            border: "1px solid rgba(255,255,255,0.2)", borderRadius: "0.6rem",
            textDecoration: "none", fontWeight: 600, fontSize: "0.9rem",
          }}>
            Telegram
          </a>
        </div>
        <p style={{
          marginTop: "1.5rem", fontSize: "0.78rem",
          color: "rgba(148,163,154,0.7)", fontFamily: "var(--font-mono)",
        }}>
          100% open-source · Infraestrutura: ${cost.monthly_usd}/mês autofinanciado · Sem investidores, sem publicidade
        </p>
      </div>
    </section>
  );
}
