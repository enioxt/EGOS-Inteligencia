import { useCallback, useEffect, useState } from "react";

import styles from "./EagleEye.module.css";

interface GazetteResult {
    territory_name: string;
    state_code: string;
    date: string;
    excerpts?: string[];
    txt_url?: string;
    is_extra_edition: boolean;
}

interface ScanResponse {
    total_gazettes: number;
    gazettes: GazetteResult[];
}

const KEYWORDS = [
    { label: "Licitações", query: "licitação | pregão eletrônico | tomada de preço" },
    { label: "Sanções", query: "inidoneidade | suspensão | CEIS | CNEP | sanção" },
    { label: "Nomeações", query: "nomeação | exoneração | posse | designar" },
    { label: "Contratos", query: "contrato | aditivo | dispensa de licitação" },
    { label: "Emendas", query: "emenda parlamentar | transferência especial" },
];

const API_BASE = "https://api.queridodiario.ok.org.br";

export function EagleEye() {
    const [results, setResults] = useState<GazetteResult[]>([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(false);
    const [activeKeyword, setActiveKeyword] = useState(KEYWORDS[0]!);
    const [cityFilter, setCityFilter] = useState("");
    const [dateRange, setDateRange] = useState(30);
    const [error, setError] = useState<string | null>(null);

    const fetchGazettes = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const params = new URLSearchParams();
            params.set("querystring", activeKeyword.query);
            params.set("sort_by", "descending_date");
            params.set("size", "20");
            params.set("excerpt_size", "500");
            params.set("number_of_excerpts", "2");

            const since = new Date(Date.now() - dateRange * 24 * 60 * 60 * 1000);
            params.set("published_since", since.toISOString().split("T")[0]!);

            if (cityFilter.trim()) {
                // First resolve city to territory_id
                const cityRes = await fetch(`${API_BASE}/cities?city_name=${encodeURIComponent(cityFilter)}`);
                if (cityRes.ok) {
                    const cityData = await cityRes.json();
                    if (cityData.cities?.length > 0) {
                        params.append("territory_ids", cityData.cities[0].territory_id);
                    }
                }
            }

            const url = `${API_BASE}/gazettes?${params}`;
            const res = await fetch(url);

            if (!res.ok) throw new Error(`API Error: ${res.status}`);

            const data: ScanResponse = await res.json();
            setResults(data.gazettes || []);
            setTotal(data.total_gazettes || 0);
        } catch (err: any) {
            setError(err.message || "Erro ao buscar dados");
            setResults([]);
            setTotal(0);
        } finally {
            setLoading(false);
        }
    }, [activeKeyword, cityFilter, dateRange]);

    useEffect(() => {
        fetchGazettes();
    }, [fetchGazettes]);

    const highlightExcerpt = (text: string) => {
        // Bold the search terms
        const terms = (activeKeyword.query || "").split(" | ");
        let highlighted = text;
        for (const term of terms) {
            const regex = new RegExp(`(${term})`, "gi");
            highlighted = highlighted.replace(regex, "<mark>$1</mark>");
        }
        return highlighted;
    };

    const getUrgencyBadge = (text: string) => {
        const lower = text.toLowerCase();
        if (lower.includes("inidoneidade") || lower.includes("sanção") || lower.includes("ceis")) {
            return <span className={styles.badgeCritical}>🔴 Sanção</span>;
        }
        if (lower.includes("licitação") || lower.includes("pregão")) {
            return <span className={styles.badgeOpportunity}>🟢 Oportunidade</span>;
        }
        if (lower.includes("nomeação") || lower.includes("exoneração")) {
            return <span className={styles.badgeInfo}>🔵 Movimentação</span>;
        }
        return <span className={styles.badgeNeutral}>⚪ Publicação</span>;
    };

    return (
        <div className={styles.container}>
            {/* Header */}
            <div className={styles.header}>
                <div className={styles.headerLeft}>
                    <h1 className={styles.title}>
                        🦅 Eagle Eye
                    </h1>
                    <p className={styles.subtitle}>
                        Monitor de Diários Oficiais — Cobertura Nacional (5.569 municípios)
                    </p>
                </div>
                <div className={styles.headerStats}>
                    <div className={styles.statCard}>
                        <span className={styles.statValue}>{total.toLocaleString("pt-BR")}</span>
                        <span className={styles.statLabel}>Resultados</span>
                    </div>
                    <div className={styles.statCard}>
                        <span className={styles.statValue}>5.569</span>
                        <span className={styles.statLabel}>Cidades</span>
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className={styles.filters}>
                <div className={styles.keywordTabs}>
                    {KEYWORDS.map((kw) => (
                        <button
                            key={kw.label}
                            className={`${styles.keywordTab} ${activeKeyword.label === kw.label ? styles.keywordTabActive : ""}`}
                            onClick={() => setActiveKeyword(kw)}
                        >
                            {kw.label}
                        </button>
                    ))}
                </div>

                <div className={styles.filterRow}>
                    <input
                        type="text"
                        placeholder="Filtrar por cidade..."
                        value={cityFilter}
                        onChange={(e) => setCityFilter(e.target.value)}
                        className={styles.cityInput}
                    />
                    <select
                        value={dateRange}
                        onChange={(e) => setDateRange(Number(e.target.value))}
                        className={styles.dateSelect}
                    >
                        <option value={7}>Últimos 7 dias</option>
                        <option value={30}>Últimos 30 dias</option>
                        <option value={90}>Últimos 90 dias</option>
                        <option value={365}>Último ano</option>
                    </select>
                    <button onClick={fetchGazettes} className={styles.searchBtn} disabled={loading}>
                        {loading ? "Buscando..." : "🔍 Buscar"}
                    </button>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div className={styles.error}>
                    ⚠️ {error}
                </div>
            )}

            {/* Results */}
            <div className={styles.results}>
                {loading ? (
                    <div className={styles.loadingState}>
                        <div className={styles.spinner} />
                        <p>Consultando 5.569 municípios via Querido Diário...</p>
                    </div>
                ) : results.length === 0 ? (
                    <div className={styles.emptyState}>
                        <p>Nenhum resultado encontrado para "{activeKeyword.label}"</p>
                    </div>
                ) : (
                    results.map((gazette, i) => (
                        <div key={`${gazette.date}-${gazette.territory_name}-${i}`} className={styles.gazetteCard}>
                            <div className={styles.gazetteHeader}>
                                <div className={styles.gazetteInfo}>
                                    <span className={styles.gazetteTerrritory}>
                                        🏙️ {gazette.territory_name} ({gazette.state_code})
                                    </span>
                                    <span className={styles.gazetteDate}>
                                        📅 {new Date(gazette.date).toLocaleDateString("pt-BR")}
                                    </span>
                                    {gazette.is_extra_edition && (
                                        <span className={styles.badgeExtra}>Edição Extra</span>
                                    )}
                                </div>
                                <div className={styles.gazetteBadges}>
                                    {gazette.excerpts?.map((ex) => getUrgencyBadge(ex))}
                                </div>
                            </div>

                            {gazette.excerpts?.map((excerpt, j) => (
                                <div
                                    key={j}
                                    className={styles.excerpt}
                                    dangerouslySetInnerHTML={{ __html: highlightExcerpt(excerpt) }}
                                />
                            ))}

                            {gazette.txt_url && (
                                <a
                                    href={gazette.txt_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className={styles.sourceLink}
                                >
                                    📄 Ver texto completo do Diário Oficial
                                </a>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
