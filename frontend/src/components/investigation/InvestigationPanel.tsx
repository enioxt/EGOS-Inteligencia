import { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { useInvestigationStore } from "@/stores/investigation";

import styles from "./InvestigationPanel.module.css";

function isJsonImportFile(file: File) {
  const filename = file.name.toLowerCase();
  const type = file.type.toLowerCase();
  return (
    filename.endsWith(".json")
    || type === "application/json"
    || type === "text/json"
  );
}

async function readFileText(file: File) {
  if (typeof file.text === "function") {
    return file.text();
  }

  return await new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result ?? ""));
    reader.onerror = () => reject(reader.error ?? new Error("failed to read file"));
    reader.readAsText(file);
  });
}

export function InvestigationPanel() {
  const { t } = useTranslation();
  const {
    investigations,
    activeInvestigationId,
    loading,
    fetchInvestigations,
    createInvestigation,
    importInvestigation,
    setActiveInvestigation,
  } = useInvestigationStore();

  const [creating, setCreating] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [importStatus, setImportStatus] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    fetchInvestigations();
  }, [fetchInvestigations]);

  const handleCreate = useCallback(async () => {
    if (!newTitle.trim()) return;
    const inv = await createInvestigation(newTitle.trim());
    setActiveInvestigation(inv.id);
    setNewTitle("");
    setCreating(false);
  }, [newTitle, createInvestigation, setActiveInvestigation]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") handleCreate();
      if (e.key === "Escape") setCreating(false);
    },
    [handleCreate],
  );

  const handleImportClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleImportFile = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      if (!isJsonImportFile(file)) {
        setImportStatus(t("investigation.importJsonOnly"));
        e.target.value = "";
        return;
      }

      try {
        JSON.parse(await readFileText(file));
      } catch {
        setImportStatus(t("investigation.importInvalidJson"));
        e.target.value = "";
        return;
      }

      setImporting(true);
      setImportStatus(null);
      try {
        const result = await importInvestigation(file);
        setActiveInvestigation(result.investigation.id);
        setImportStatus(t("investigation.importSuccess"));
      } catch {
        setImportStatus(t("investigation.importError"));
      } finally {
        setImporting(false);
        e.target.value = "";
      }
    },
    [importInvestigation, setActiveInvestigation, t],
  );

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <h2 className={styles.title}>{t("investigation.title")}</h2>
        <div className={styles.actions}>
          <button
            className={styles.newButton}
            onClick={handleImportClick}
            type="button"
            disabled={importing}
          >
            {importing ? t("common.loading") : t("investigation.import")}
          </button>
          <button
            className={styles.newButton}
            onClick={() => setCreating(true)}
            type="button"
          >
            + {t("investigation.newInvestigation")}
          </button>
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="application/json,.json"
        onChange={handleImportFile}
        className={styles.hiddenInput}
      />

      {importStatus && <p className={styles.status}>{importStatus}</p>}

      {creating && (
        <input
          type="text"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={() => { if (!newTitle.trim()) setCreating(false); }}
          placeholder={t("investigation.newInvestigation")}
          autoFocus
          className={styles.item}
        />
      )}

      {loading && <p className={styles.empty}>{t("common.loading")}</p>}

      <div className={styles.list}>
        {!loading && investigations.length === 0 && (
          <p className={styles.empty}>{t("investigation.noInvestigations")}</p>
        )}
        {investigations.map((inv) => (
          <button
            key={inv.id}
            className={`${styles.item} ${activeInvestigationId === inv.id ? styles.active : ""}`}
            onClick={() => setActiveInvestigation(inv.id)}
            type="button"
          >
            <span className={styles.itemTitle}>{inv.title}</span>
            <div className={styles.itemMeta}>
              <span>{(inv.entity_ids ?? []).length} {t("common.connections")}</span>
              <span>{new Date(inv.created_at).toLocaleDateString()}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
