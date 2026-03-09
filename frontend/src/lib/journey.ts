/**
 * Journey — Local research history with persistence
 * Saves searches, entity views, and investigations to localStorage.
 * Exportable as JSON/Markdown, shareable via URL, persists to backend on login.
 */

export interface JourneyEntry {
  id: string;
  type: "search" | "entity" | "pattern" | "investigation" | "chat";
  title: string;
  description?: string;
  entityId?: string;
  entityType?: string;
  query?: string;
  url: string;
  timestamp: number;
  metadata?: Record<string, unknown>;
}

export interface JourneyData {
  version: 1;
  entries: JourneyEntry[];
  createdAt: number;
  lastUpdated: number;
}

const STORAGE_KEY = "egos_journey";
const MAX_ENTRIES = 500;

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

export function getJourney(): JourneyData {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const data = JSON.parse(raw) as JourneyData;
      if (data.version === 1 && Array.isArray(data.entries)) return data;
    }
  } catch { /* malformed data, reset */ }
  return { version: 1, entries: [], createdAt: Date.now(), lastUpdated: Date.now() };
}

function saveJourney(data: JourneyData): void {
  data.lastUpdated = Date.now();
  if (data.entries.length > MAX_ENTRIES) {
    data.entries = data.entries.slice(-MAX_ENTRIES);
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

export function addJourneyEntry(entry: Omit<JourneyEntry, "id" | "timestamp">): JourneyEntry {
  const journey = getJourney();
  const recent = journey.entries.at(-1);
  if (recent && recent.url === entry.url && Date.now() - recent.timestamp < 60000) {
    return recent;
  }
  const full: JourneyEntry = { ...entry, id: generateId(), timestamp: Date.now() };
  journey.entries.push(full);
  saveJourney(journey);
  window.dispatchEvent(new CustomEvent("journey-updated", { detail: full }));
  return full;
}

export function removeJourneyEntry(id: string): void {
  const journey = getJourney();
  journey.entries = journey.entries.filter((e) => e.id !== id);
  saveJourney(journey);
  window.dispatchEvent(new CustomEvent("journey-updated"));
}

export function clearJourney(): void {
  localStorage.removeItem(STORAGE_KEY);
  window.dispatchEvent(new CustomEvent("journey-updated"));
}

export function exportJourneyJSON(): string {
  return JSON.stringify(getJourney(), null, 2);
}

export function exportJourneyMarkdown(): string {
  const journey = getJourney();
  if (journey.entries.length === 0) return "# Jornada de Pesquisa\n\nNenhuma pesquisa registrada.";
  const lines = ["# Jornada de Pesquisa EGOS Inteligencia", ""];
  lines.push("" + journey.entries.length + " registros | Exportado em " + new Date().toLocaleString("pt-BR"));
  lines.push("");
  const grouped = new Map<string, JourneyEntry[]>();
  for (const e of journey.entries) {
    const day = new Date(e.timestamp).toLocaleDateString("pt-BR");
    if (!grouped.has(day)) grouped.set(day, []);
    const arr = grouped.get(day); if (arr) arr.push(e);
  }
  for (const [day, entries] of grouped) {
    lines.push("## " + day);
    lines.push("");
    for (const e of entries) {
      const time = new Date(e.timestamp).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
      const icons: Record<string, string> = { search: "BUSCA", entity: "ENTIDADE", chat: "CHAT", pattern: "PADRAO", investigation: "INVESTIGACAO" };
      lines.push("- **" + time + "** [" + (icons[e.type] || e.type) + "] " + e.title);
      if (e.description) lines.push("  > " + e.description);
    }
    lines.push("");
  }
  return lines.join("\n");
}

export function getJourneyStats() {
  const journey = getJourney();
  return {
    total: journey.entries.length,
    searches: journey.entries.filter((e) => e.type === "search").length,
    entities: journey.entries.filter((e) => e.type === "entity").length,
    chats: journey.entries.filter((e) => e.type === "chat").length,
    lastActive: journey.entries.length > 0
      ? new Date(journey.entries.at(-1)!.timestamp).toLocaleString("pt-BR")
      : "Nunca",
  };
}
