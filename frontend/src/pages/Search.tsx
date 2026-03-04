import { useState } from "react";
import { useTranslation } from "react-i18next";

import { searchEntities, type SearchResult, type OSINTFilters } from "@/api/client";
import { Spinner } from "@/components/common/Spinner";
import { SearchBar, type SearchParams } from "@/components/search/SearchBar";
import { GroupedSearchResults } from "@/components/search/GroupedSearchResults";
import { AdvancedSearchFilters } from "@/components/search/AdvancedSearchFilters";
import { addJourneyEntry } from "@/lib/journey";

import styles from "./Search.module.css";

export function Search() {
  const { t } = useTranslation();
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<OSINTFilters>({
    isPep: false,
    hasSanctions: false,
    hasContracts: false,
  });

  const handleSearch = async (params: SearchParams) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await searchEntities(params.query, params.type, 1, 20, filters);
      addJourneyEntry({ type: "search", title: params.query.slice(0, 80), query: params.query, url: "/app/search", description: response.results.length + " resultados" });
      setResults(response.results);
      setHasSearched(true);
    } catch {
      setError(t("search.error"));
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div style={{ maxWidth: "800px", margin: "0 auto", width: "100%" }}>
        <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem", color: "var(--text-primary)" }}>Central de Pesquisa Inteligente</h1>
        <SearchBar onSearch={handleSearch} isLoading={isLoading} />
        <AdvancedSearchFilters filters={filters} onFilterChange={setFilters} />

        {error && <p className={styles.error}>{error}</p>}
        {isLoading && (
          <div className={styles.loading}>
            <Spinner />
          </div>
        )}
        {hasSearched && !isLoading && !error && <GroupedSearchResults results={results} />}
      </div>
    </div>
  );
}
