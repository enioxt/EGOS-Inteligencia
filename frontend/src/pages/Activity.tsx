import { useEffect, useState } from "react";
import styles from "./Activity.module.css";

interface ActivityItem {
  id: string;
  type: string;
  title: string;
  description: string;
  source: string;
  result_count: number;
  cost_usd: number;
  model?: string;
  timestamp: string;
}

interface ActivityStats {
  total_events: number;
  session_events: number;
  by_type: Record<string, number>;
  by_source: Record<string, number>;
  by_model: Record<string, number>;
  total_cost_usd: number;
  total_results: number;
  unique_users: number;
  avg_cost_per_query: number;
  daily: Record<string, number>;
}

interface ActivityFeed {
  items: ActivityItem[];
  stats: ActivityStats;
}

const TYPE_ICONS: Record<string, string> = {
  chat: "💬",
  search: "🔍",
  report: "📄",
  entity_view: "👁️",
  tool_call: "🔧",
};

const TYPE_COLORS: Record<string, string> = {
  chat: "#4ade80",
  search: "#3b82f6",
  report: "#f59e0b",
  entity_view: "#8b5cf6",
  tool_call: "#ef4444",
};

const PAGE_SIZE = 15;

function DailyChart({ daily }: { daily: Record<string, number> }) {
  const entries = Object.entries(daily).sort(([a], [b]) => a.localeCompare(b));
  const maxVal = Math.max(...entries.map(([, v]) => v), 1);
  if (entries.length === 0) return null;
  return (
    <div className={styles.dailyChart}>
      <h3 className={styles.sectionTitle}>Atividade diária (7 dias)</h3>
      <div className={styles.bars}>
        {entries.map(([date, count]) => (
          <div key={date} className={styles.barCol}>
            <div
              className={styles.bar}
              style={{ height: `${Math.max((count / maxVal) * 100, 4)}%` }}
              title={`${date}: ${count} eventos`}
            />
            <span className={styles.barLabel}>{date.slice(5)}</span>
            <span className={styles.barValue}>{count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function Activity() {
  const [feed, setFeed] = useState<ActivityFeed | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [page, setPage] = useState(0);

  const fetchFeed = async () => {
    try {
      const url = filter
        ? `/api/v1/activity/feed?limit=200&type=${filter}`
        : `/api/v1/activity/feed?limit=200`;
      const resp = await fetch(url);
      if (resp.ok) setFeed(await resp.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeed();
    const interval = setInterval(fetchFeed, 15000);
    return () => clearInterval(interval);
  }, [filter]);

  useEffect(() => { setPage(0); }, [filter]);

  const totalItems = feed?.items.length ?? 0;
  const totalPages = Math.ceil(totalItems / PAGE_SIZE);
  const pagedItems = feed?.items.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE) ?? [];

  if (loading) return <div className={styles.loading}>Carregando atividades...</div>;
  if (!feed) return <div className={styles.loading}>Sem dados de atividade.</div>;

  const { stats } = feed;

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Feed de Atividades</h1>
      <p className={styles.subtitle}>
        Monitoramento em tempo real — contagem cumulativa (não reseta)
      </p>

      {/* Main stats */}
      <div className={styles.statsBar}>
        <div className={styles.stat}>
          <span className={styles.statValue}>{stats.total_events}</span>
          <span className={styles.statLabel}>Total (lifetime)</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statValue}>{stats.unique_users}</span>
          <span className={styles.statLabel}>Usuários únicos</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statValue}>{stats.total_results}</span>
          <span className={styles.statLabel}>Resultados</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statValue}>${stats.total_cost_usd.toFixed(4)}</span>
          <span className={styles.statLabel}>Custo total</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statValue}>${stats.avg_cost_per_query.toFixed(6)}</span>
          <span className={styles.statLabel}>Custo/query</span>
        </div>
      </div>

      {/* Type filter bar */}
      <div className={styles.statsBar}>
        {Object.entries(stats.by_type).map(([type, count]) => (
          <div
            key={type}
            className={styles.stat}
            onClick={() => setFilter(filter === type ? "" : type)}
            style={{ cursor: "pointer", borderColor: filter === type ? TYPE_COLORS[type] || "#4ade80" : "transparent" }}
          >
            <span className={styles.statValue}>
              {TYPE_ICONS[type] || "📊"} {count}
            </span>
            <span className={styles.statLabel}>{type}</span>
          </div>
        ))}
      </div>

      {/* Daily chart */}
      <DailyChart daily={stats.daily ?? {}} />

      {/* Model usage + Top sources side by side */}
      <div className={styles.detailsGrid}>
        {Object.keys(stats.by_model ?? {}).length > 0 && (
          <div className={styles.detailBox}>
            <h3 className={styles.sectionTitle}>Modelos de IA</h3>
            {Object.entries(stats.by_model).map(([model, count]) => (
              <div key={model} className={styles.detailRow}>
                <span className={styles.detailLabel}>{model.split("/").pop()}</span>
                <span className={styles.detailValue}>{count}</span>
              </div>
            ))}
          </div>
        )}
        {Object.keys(stats.by_source ?? {}).length > 0 && (
          <div className={styles.detailBox}>
            <h3 className={styles.sectionTitle}>Top fontes de dados</h3>
            {Object.entries(stats.by_source).slice(0, 10).map(([source, count]) => (
              <div key={source} className={styles.detailRow}>
                <span className={styles.detailLabel}>{source}</span>
                <span className={styles.detailValue}>{count}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Timeline */}
      <h3 className={styles.sectionTitle} style={{ marginTop: "1.5rem" }}>
        Eventos recentes ({stats.session_events} nesta sessão)
      </h3>
      <div className={styles.timeline}>
        {pagedItems.map((item) => (
          <div key={item.id} className={styles.event}>
            <div
              className={styles.eventDot}
              style={{ backgroundColor: TYPE_COLORS[item.type] || "#666" }}
            />
            <div className={styles.eventContent}>
              <div className={styles.eventHeader}>
                <span className={styles.eventType}>
                  {TYPE_ICONS[item.type] || "📊"} {item.type}
                </span>
                <span className={styles.eventTime}>
                  {new Date(item.timestamp).toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" })}
                </span>
              </div>
              <div className={styles.eventTitle}>
                {item.title || (
                  item.type === "chat" ? "Consulta ao agente" :
                  item.type === "search" ? "Busca realizada" :
                  item.type === "entity_view" ? "Entidade visualizada" :
                  item.type === "report" ? "Relatório gerado" :
                  item.type === "tool_call" ? "Ferramenta utilizada" :
                  "Ação registrada"
                )}
              </div>
              <div className={styles.eventMeta}>
                {item.source && <span>Fonte: {item.source}</span>}
                {item.result_count > 0 && <span>{item.result_count} resultados</span>}
                {item.cost_usd > 0 && <span>${item.cost_usd.toFixed(4)}</span>}
                {item.model && <span>{item.model.split("/").pop()}</span>}
              </div>
            </div>
          </div>
        ))}
        {feed.items.length === 0 && (
          <div className={styles.empty}>
            Nenhuma atividade registrada. Faça uma busca no chatbot para começar.
          </div>
        )}
      </div>

      {totalPages > 1 && (
        <div className={styles.pagination}>
          <button
            className={styles.pageBtn}
            disabled={page === 0}
            onClick={() => setPage(p => Math.max(0, p - 1))}
          >
            ← Anterior
          </button>
          <span className={styles.pageInfo}>
            Página {page + 1} de {totalPages} ({totalItems} eventos)
          </span>
          <button
            className={styles.pageBtn}
            disabled={page >= totalPages - 1}
            onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
          >
            Próxima →
          </button>
        </div>
      )}
    </div>
  );
}
