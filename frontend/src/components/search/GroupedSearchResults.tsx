import React, { useState, useMemo } from "react";
import { Link } from "react-router";
import { useTranslation } from "react-i18next";
import {
    Users, Building2, MapPin, Target,
    ChevronDown, ChevronRight, ChevronUp, MoreHorizontal
} from "lucide-react";

import type { SearchResult } from "@/api/client";
import { SourceBadge } from "@/components/common/SourceBadge";

interface GroupedSearchResultsProps {
    results: SearchResult[];
}

const ENTITIES_LIMIT = 10;

interface EntityGroup {
    key: string;
    label: string;
    labelPlural: string;
    icon: React.ReactNode;
    bgColor: string;
    textColor: string;
    results: SearchResult[];
    priority: number;
}

export function GroupedSearchResults({ results }: GroupedSearchResultsProps) {
    const { t } = useTranslation();
    const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(["Pessoa", "Empresa"]));
    const [expandedLimits, setExpandedLimits] = useState<Set<string>>(new Set());

    const groups = useMemo(() => {
        const resultGroups: EntityGroup[] = [
            {
                key: "Pessoa",
                label: "Pessoa",
                labelPlural: "Pessoas",
                icon: <Users className="w-4 h-4" />,
                bgColor: "rgba(59, 130, 246, 0.1)", // blue-500/10
                textColor: "rgb(96, 165, 250)", // blue-400
                results: [],
                priority: 1,
            },
            {
                key: "Empresa",
                label: "Empresa",
                labelPlural: "Empresas",
                icon: <Building2 className="w-4 h-4" />,
                bgColor: "rgba(249, 115, 22, 0.1)", // orange-500/10
                textColor: "rgb(251, 146, 60)", // orange-400
                results: [],
                priority: 2,
            },
            {
                key: "Órgão Público",
                label: "Órgão Público",
                labelPlural: "Órgãos Públicos",
                icon: <Building2 className="w-4 h-4" />,
                bgColor: "rgba(168, 85, 247, 0.1)", // purple-500/10
                textColor: "rgb(192, 132, 252)", // purple-400
                results: [],
                priority: 3,
            },
            {
                key: "Local",
                label: "Local",
                labelPlural: "Locais",
                icon: <MapPin className="w-4 h-4" />,
                bgColor: "rgba(16, 185, 129, 0.1)", // emerald-500/10
                textColor: "rgb(52, 211, 153)", // emerald-400
                results: [],
                priority: 4,
            },
            {
                key: "Outros",
                label: "Outro",
                labelPlural: "Outros",
                icon: <Target className="w-4 h-4" />,
                bgColor: "rgba(100, 116, 139, 0.1)", // slate-500/10
                textColor: "rgb(148, 163, 184)", // slate-400
                results: [],
                priority: 5,
            },
        ];

        results.forEach((res) => {
            let groupKey = "Outros";
            if (res.type === "Person") groupKey = "Pessoa";
            else if (res.type === "Company") groupKey = "Empresa";
            else if (res.type === "PublicAgency") groupKey = "Órgão Público";
            else if (res.type === "Location") groupKey = "Local";

            resultGroups.find((g) => g.key === groupKey)?.results.push(res);
        });

        return resultGroups.filter((g) => g.results.length > 0).sort((a, b) => a.priority - b.priority);
    }, [results]);

    const toggleGroup = (key: string) => {
        const newExpanded = new Set(expandedGroups);
        if (newExpanded.has(key)) newExpanded.delete(key);
        else newExpanded.add(key);
        setExpandedGroups(newExpanded);
    };

    if (results.length === 0) {
        return (
            <div style={{ textAlign: "center", padding: "2rem" }}>
                <p style={{ color: "var(--text-secondary)" }}>{t("search.noResults")}</p>
                <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>{t("search.emptyHint")}</p>
            </div>
        );
    }

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem", marginTop: "1rem" }}>
            {groups.map((group) => (
                <div key={group.key} style={{ border: "1px solid var(--border-color)", borderRadius: "8px", overflow: "hidden" }}>
                    <button
                        onClick={() => toggleGroup(group.key)}
                        style={{
                            width: "100%",
                            padding: "0.75rem 1rem",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            backgroundColor: group.bgColor,
                            border: "none",
                            cursor: "pointer",
                            textAlign: "left",
                        }}
                    >
                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                            <span style={{ color: group.textColor, display: "flex" }}>{group.icon}</span>
                            <span style={{ fontWeight: 500, color: group.textColor }}>
                                {group.results.length} {group.results.length === 1 ? group.label : group.labelPlural}
                            </span>
                        </div>
                        {expandedGroups.has(group.key) ? (
                            <ChevronDown className="w-4 h-4" style={{ color: "var(--text-muted)" }} />
                        ) : (
                            <ChevronRight className="w-4 h-4" style={{ color: "var(--text-muted)" }} />
                        )}
                    </button>

                    {expandedGroups.has(group.key) && (
                        <div style={{ display: "flex", flexDirection: "column", backgroundColor: "var(--bg-surface)" }}>
                            {(expandedLimits.has(group.key) ? group.results : group.results.slice(0, ENTITIES_LIMIT)).map((result) => (
                                <Link
                                    key={result.id}
                                    to={`/app/analysis/${result.id}`}
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "space-between",
                                        padding: "0.75rem 1rem",
                                        borderBottom: "1px solid var(--border-color)",
                                        textDecoration: "none",
                                        color: "inherit",
                                    }}
                                    className="hover-bg-subtle"
                                >
                                    <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem", flex: 1 }}>
                                        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                                            <span style={{ fontWeight: 500, color: "var(--text-primary)" }}>{result.name}</span>
                                            {result.sources?.some(s => s.database.toLowerCase().includes("pep")) && (
                                                <span style={{
                                                    fontSize: "0.7rem",
                                                    padding: "0.1rem 0.4rem",
                                                    borderRadius: "4px",
                                                    backgroundColor: "rgba(234, 179, 8, 0.1)",
                                                    color: "rgb(234, 179, 8)",
                                                    border: "1px solid rgba(234, 179, 8, 0.2)"
                                                }}>
                                                    🚨 PEP
                                                </span>
                                            )}
                                            {result.sources?.some(s => s.database.toLowerCase().includes("ceis") || s.database.toLowerCase().includes("cnep")) && (
                                                <span style={{
                                                    fontSize: "0.7rem",
                                                    padding: "0.1rem 0.4rem",
                                                    borderRadius: "4px",
                                                    backgroundColor: "rgba(239, 68, 68, 0.1)",
                                                    color: "rgb(239, 68, 68)",
                                                    border: "1px solid rgba(239, 68, 68, 0.2)"
                                                }}>
                                                    ⚠️ Sancionado
                                                </span>
                                            )}
                                        </div>
                                        {result.document && (
                                            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                                                {result.document}
                                            </span>
                                        )}
                                    </div>
                                    <div style={{ display: "flex", gap: "0.25rem", flexWrap: "wrap", justifyContent: "flex-end", maxWidth: "40%" }}>
                                        {(result.sources ?? []).map((source) => (
                                            <SourceBadge key={source.database} source={source.database} />
                                        ))}
                                    </div>
                                </Link>
                            ))}

                            {group.results.length > ENTITIES_LIMIT && !expandedLimits.has(group.key) && (
                                <button
                                    onClick={() => setExpandedLimits((prev) => new Set([...prev, group.key]))}
                                    style={{
                                        width: "100%", padding: "0.75rem", display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem",
                                        fontSize: "0.875rem", color: "var(--accent-primary)", backgroundColor: "transparent", border: "none", cursor: "pointer"
                                    }}
                                >
                                    <MoreHorizontal className="w-4 h-4" />
                                    Ver mais {group.results.length - ENTITIES_LIMIT} {group.labelPlural.toLowerCase()}
                                </button>
                            )}
                            {expandedLimits.has(group.key) && group.results.length > ENTITIES_LIMIT && (
                                <button
                                    onClick={() => setExpandedLimits((prev) => { const next = new Set(prev); next.delete(group.key); return next; })}
                                    style={{
                                        width: "100%", padding: "0.75rem", display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem",
                                        fontSize: "0.875rem", color: "var(--text-muted)", backgroundColor: "transparent", border: "none", cursor: "pointer"
                                    }}
                                >
                                    <ChevronUp className="w-4 h-4" /> Ver menos
                                </button>
                            )}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}
