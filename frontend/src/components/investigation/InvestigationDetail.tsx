import { useCallback, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { exportInvestigation, exportInvestigationPDF, generateShareLink } from "@/api/client";
import { useInvestigationStore } from "@/stores/investigation";

import styles from "./InvestigationDetail.module.css";

export function InvestigationDetail() {
  const { t } = useTranslation();
  const {
    investigations,
    activeInvestigationId,
    updateInvestigation,
    deleteInvestigation,
    addEntity,
    removeEntity,
    setActiveInvestigation,
  } = useInvestigationStore();

  const [entityInput, setEntityInput] = useState("");
  const [toast, setToast] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const investigation = useMemo(
    () => investigations.find((i) => i.id === activeInvestigationId),
    [investigations, activeInvestigationId],
  );

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 2000);
  }, []);

  const handleTitleBlur = useCallback(
    (e: React.FocusEvent<HTMLInputElement>) => {
      if (!investigation) return;
      const val = e.target.value.trim();
      if (val && val !== investigation.title) {
        updateInvestigation(investigation.id, { title: val });
      }
    },
    [investigation, updateInvestigation],
  );

  const handleDescBlur = useCallback(
    (e: React.FocusEvent<HTMLTextAreaElement>) => {
      if (!investigation) return;
      const val = e.target.value;
      if (val !== investigation.description) {
        updateInvestigation(investigation.id, { description: val });
      }
    },
    [investigation, updateInvestigation],
  );

  const handleAddEntity = useCallback(async () => {
    if (!investigation || !entityInput.trim()) return;
    await addEntity(investigation.id, entityInput.trim());
    setEntityInput("");
  }, [investigation, entityInput, addEntity]);

  const handleRemoveEntity = useCallback(
    async (entityId: string) => {
      if (!investigation) return;
      await removeEntity(investigation.id, entityId);
    },
    [investigation, removeEntity],
  );

  const handleShare = useCallback(async () => {
    if (!investigation) return;
    const { share_token } = await generateShareLink(investigation.id);
    const url = `${window.location.origin}/shared/${share_token}`;
    await navigator.clipboard.writeText(url);
    showToast(t("investigation.shareCopied"));
  }, [investigation, showToast, t]);

  const handleExport = useCallback(async () => {
    if (!investigation) return;
    const blob = await exportInvestigation(investigation.id);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${investigation.title}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [investigation]);

  const handleExportPDF = useCallback(async () => {
    if (!investigation) return;
    const lang = document.documentElement.lang === "en" ? "en" : "pt";
    const blob = await exportInvestigationPDF(investigation.id, lang);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${investigation.title}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  }, [investigation]);

  const handleDelete = useCallback(async () => {
    if (!investigation) return;
    if (!confirmDelete) {
      setConfirmDelete(true);
      return;
    }
    await deleteInvestigation(investigation.id);
    setActiveInvestigation(null);
    setConfirmDelete(false);
  }, [investigation, confirmDelete, deleteInvestigation, setActiveInvestigation]);

  if (!investigation) {
    return <p className={styles.hint}>{t("investigation.noSelection")}</p>;
  }

  return (
    <div className={styles.detail}>
      <div className={styles.titleRow}>
        <input
          className={styles.titleInput}
          defaultValue={investigation.title}
          onBlur={handleTitleBlur}
          key={investigation.id}
        />
      </div>

      <textarea
        className={styles.descInput}
        defaultValue={investigation.description}
        onBlur={handleDescBlur}
        placeholder={t("investigation.description")}
        key={`desc-${investigation.id}`}
      />

      <div className={styles.actions}>
        <button className={styles.actionButton} onClick={handleShare} type="button">
          {t("investigation.share")}
        </button>
        <button className={styles.actionButton} onClick={handleExport} type="button">
          {t("investigation.export")}
        </button>
        <button className={styles.actionButton} onClick={handleExportPDF} type="button">
          {t("investigation.exportPDF")}
        </button>
        <button className={styles.deleteButton} onClick={handleDelete} type="button">
          {confirmDelete ? t("investigation.deleteConfirm") : "X"}
        </button>
      </div>

      {toast && <span className={styles.toast}>{toast}</span>}

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>{t("investigation.entities")}</h3>
        <div className={styles.entityRow}>
          <input
            className={styles.entityInput}
            value={entityInput}
            onChange={(e) => setEntityInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") handleAddEntity(); }}
            placeholder={t("investigation.addEntity")}
          />
          <button className={styles.actionButton} onClick={handleAddEntity} type="button">
            +
          </button>
        </div>
        <div className={styles.entityList}>
          {(investigation.entity_ids ?? []).map((eid) => (
            <span key={eid} className={styles.entityChip}>
              {eid}
              <button
                className={styles.removeButton}
                onClick={() => handleRemoveEntity(eid)}
                type="button"
                aria-label={t("investigation.removeEntity")}
              >
                x
              </button>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
