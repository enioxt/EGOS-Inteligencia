import { useState } from "react";
import { useTranslation } from "react-i18next";

import { searchEntities, type SearchResult } from "@/api/client";
import { Spinner } from "@/components/common/Spinner";
import { SearchBar, type SearchParams } from "@/components/search/SearchBar";
import { SearchResults } from "@/components/search/SearchResults";
import { addJourneyEntry } from "@/lib/journey";

import styles from "./Search.module.css";

export function Search() {
  const { t } = useTranslation();
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (params: SearchParams) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await searchEntities(params.query, params.type);
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
      <SearchBar onSearch={handleSearch} isLoading={isLoading} />
      {error && <p className={styles.error}>{error}</p>}
      {isLoading && (
        <div className={styles.loading}>
          <Spinner />
        </div>
      )}
      {hasSearched && !isLoading && !error && <SearchResults results={results} />}
    </div>
  );
}
