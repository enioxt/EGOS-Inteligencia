import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router";

import { type Investigation, listInvestigations, searchEntities, type SearchResult, getStats, type StatsResponse } from "@/api/client";
import { Skeleton } from "@/components/common/Skeleton";
import { useToastStore } from "@/stores/toast";
import { addJourneyEntry } from "@/lib/journey";
import { JourneyPanel } from "@/components/journey/JourneyPanel";

import styles from "./Dashboard.module.css";

export function Dashboard() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const addToast = useToastStore((s) => s.addToast);

  const [recentInvestigations, setRecentInvestigations] = useState<Investigation[]>([]);
  const [loadingInvestigations, setLoadingInvestigations] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);

  const [stats, setStats] = useState<StatsResponse | null>(null);

  useEffect(() => {
    getStats().then(setStats).catch(() => { });
    listInvestigations(1, 3)
      .then((res) => setRecentInvestigations(res.investigations))
      .catch(() => { })
      .finally(() => setLoadingInvestigations(false));
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = searchQuery.trim();
    if (!q) return;
    setSearching(true);
    try {
      addJourneyEntry({ type: "search", title: q.slice(0, 80), query: q, url: "/app/dashboard", description: "Dashboard search" });
      const res = await searchEntities(q, undefined, 1, 5);
      setSearchResults(res.results);
    } catch {
      setSearchResults([]);
      addToast("error", t("search.error"));
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>{t("dashboard.welcome")}</h1>

      <section className={styles.searchSection}>
        <h2 className={styles.sectionTitle}>{t("dashboard.quickSearch")}</h2>
        <form className={styles.searchForm} onSubmit={handleSearch}>
          <input
            type="text"
            className={styles.searchInput}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t("search.placeholder")}
          />
          <button type="submit" className={styles.searchBtn} disabled={searching}>
            {t("search.button")}
          </button>
        </form>
        {searchResults.length > 0 && (
          <ul className={styles.quickResults}>
            {searchResults.map((r) => (
              <li key={r.id}>
                <Link to={`/app/analysis/${r.id}`} className={styles.quickResultLink}>
                  <span className={styles.quickResultType}>
                    {t(`entity.${r.type}`, r.type)}
                  </span>
                  <span className={styles.quickResultName}>{r.name}</span>
                  {r.document && (
                    <span className={styles.quickResultDoc}>{r.document}</span>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className={styles.onboardingSection}>
        <h2 className={styles.sectionTitle}>Dicas de Uso (OSINT)</h2>
        <div className={styles.onboardingCards}>
          <div className={styles.onboardingCard}>
            <h3>Busca de Políticos (PEP)</h3>
            <p>Ative o filtro PEP na Central de Pesquisa Inteligente para focar em investigados expostos.</p>
          </div>
          <div className={styles.onboardingCard}>
            <h3>Empresas Sancionadas</h3>
            <p>Ative o filtro "Com Sanções (CEIS/CNEP)" para encontrar empresas inidôneas.</p>
          </div>
          <div className={styles.onboardingCard}>
            <h3>Recursos Públicos</h3>
            <p>Busque por cidades específicas para investigar contratos municipais e fornecedores locais.</p>
          </div>
        </div>
      </section>

      {stats && (
        <section className={styles.statsSection}>
          <h2 className={styles.sectionTitle}>Motor de Dados do EGOS Inteligência</h2>
          <div className={styles.statsGrid}>
            <div className={styles.statCard}>
              <span className={styles.statValue}>{stats.total_nodes.toLocaleString("pt-BR")}</span>
              <span className={styles.statLabel}>Entidades Monitoradas</span>
            </div>
            <div className={styles.statCard}>
              <span className={styles.statValue}>{stats.person_count.toLocaleString("pt-BR")}</span>
              <span className={styles.statLabel}>Pessoas</span>
            </div>
            <div className={styles.statCard}>
              <span className={styles.statValue}>{stats.company_count.toLocaleString("pt-BR")}</span>
              <span className={styles.statLabel}>Empresas</span>
            </div>
            <div className={styles.statCard}>
              <span className={styles.statValue}>{stats.contract_count.toLocaleString("pt-BR")}</span>
              <span className={styles.statLabel}>Contratos Públicos</span>
            </div>
            <div className={styles.statCard}>
              <span className={styles.statValue}>{stats.sanction_count.toLocaleString("pt-BR")}</span>
              <span className={styles.statLabel}>Sanções (CEIS/CNEP)</span>
            </div>
          </div>
        </section>
      )}

      <section className={styles.investigationsSection}>
        <h2 className={styles.sectionTitle}>{t("dashboard.recentInvestigations")}</h2>
        {loadingInvestigations ? (
          <div className={styles.skeletons}>
            <Skeleton variant="rect" height="72px" />
            <Skeleton variant="rect" height="72px" />
            <Skeleton variant="rect" height="72px" />
          </div>
        ) : recentInvestigations.length === 0 ? (
          <p className={styles.empty}>{t("dashboard.noRecent")}</p>
        ) : (
          <div className={styles.investigationCards}>
            {recentInvestigations.map((inv) => (
              <button
                key={inv.id}
                className={styles.investigationCard}
                onClick={() => navigate(`/app/pesquisas/${inv.id}`)}
              >
                <span className={styles.invTitle}>{inv.title}</span>
                <span className={styles.invMeta}>
                  {(inv.entity_ids ?? []).length} {t("common.connections")} &middot; {new Date(inv.updated_at).toLocaleDateString()}
                </span>
              </button>
            ))}
          </div>
        )}
      </section>
      <JourneyPanel />
    </div>
  );
}
