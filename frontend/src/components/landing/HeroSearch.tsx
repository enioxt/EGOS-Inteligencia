import { useCallback, useRef, useState } from "react";

import { type SearchResult, searchEntities } from "@/api/client";
import { addJourneyEntry } from "@/lib/journey";

import styles from "../../pages/Landing.module.css";

const SEARCH_SUGGESTIONS = [
  { label: "Empresas sancionadas", query: "sancionada", icon: "\u{1F3E2}" },
  { label: "Pol\u00edticos de SP", query: "S\u00e3o Paulo", icon: "\u{1F3DB}\uFE0F" },
  { label: "Lista suja trabalho escravo", query: "trabalho escravo", icon: "\u{26D3}\uFE0F" },
  { label: "Emendas parlamentares", query: "emenda parlamentar", icon: "\u{1F4B0}" },
  { label: "Licita\u00e7\u00f5es RJ", query: "Rio de Janeiro licita\u00e7\u00e3o", icon: "\u{1F4CB}" },
  { label: "Mandados de pris\u00e3o", query: "mandado pris\u00e3o", icon: "\u{1F6A8}" },
];

export function HeroSearch({ onSendToChat }: { onSendToChat: (query: string) => void }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const doSearch = useCallback(async (q: string) => {
    const trimmed = q.trim();
    if (!trimmed) return;
    setSearching(true);
    setHasSearched(true);
    try {
      addJourneyEntry({ type: "search", title: trimmed.slice(0, 80), query: trimmed, url: "/", description: "Landing search" });
      const res = await searchEntities(trimmed, undefined, 1, 6);
      setResults(res.results);
    } catch {
      setResults([]);
    } finally {
      setSearching(false);
    }
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    doSearch(query);
  };

  const handleSuggestion = (suggestion: string) => {
    setQuery(suggestion);
    doSearch(suggestion);
  };

  return (
    <div className={styles.heroSearch}>
      <form className={styles.heroSearchForm} onSubmit={handleSubmit}>
        <span className={styles.heroSearchIcon}>{"\uD83D\uDD0D"}</span>
        <input
          ref={inputRef}
          type="text"
          className={styles.heroSearchInput}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="CNPJ, nome, empresa, cidade ou tema..."
          autoComplete="off"
        />
        <button type="submit" className={styles.heroSearchBtn} disabled={searching}>
          {searching ? "Buscando..." : "Pesquisar"}
        </button>
      </form>

      {!hasSearched && (
        <div className={styles.heroSuggestions}>
          {SEARCH_SUGGESTIONS.map((s) => (
            <button
              key={s.query}
              className={styles.heroSuggestionChip}
              onClick={() => handleSuggestion(s.query)}
              type="button"
            >
              <span>{s.icon}</span> {s.label}
            </button>
          ))}
        </div>
      )}

      {hasSearched && results.length > 0 && (
        <div className={styles.heroResults}>
          {results.map((r) => (
            <a
              key={r.id}
              href={`/app/analysis/${r.id}`}
              target="_blank"
              rel="noopener noreferrer"
              className={styles.heroResultItem}
            >
              <span className={styles.heroResultType}>{r.type}</span>
              <span className={styles.heroResultName}>{r.name}</span>
              {r.document && <span className={styles.heroResultDoc}>{r.document}</span>}
            </a>
          ))}
          <button
            type="button"
            className={styles.heroSendToChat}
            onClick={() => onSendToChat(query)}
          >
            {"\uD83E\uDD16"} Aprofundar com IA
          </button>
        </div>
      )}

      {hasSearched && results.length === 0 && !searching && (
        <div className={styles.heroNoResults}>
          <span>Nenhum resultado para "{query}"</span>
          <button
            type="button"
            className={styles.heroSendToChat}
            onClick={() => onSendToChat(query)}
          >
            {"\uD83E\uDD16"} Perguntar \u00e0 IA sobre isso
          </button>
        </div>
      )}
    </div>
  );
}
