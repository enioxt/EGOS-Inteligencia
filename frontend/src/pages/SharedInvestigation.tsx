import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate, useParams } from "react-router";

import type { SharedInvestigation as SharedInvestigationData } from "@/api/client";
import { IS_PUBLIC_MODE } from "@/config/runtime";
import { getSharedInvestigation } from "@/api/client";
import { useAuthStore } from "@/stores/auth";
import { useInvestigationStore } from "@/stores/investigation";

import styles from "./SharedInvestigation.module.css";

function maskCpf(value: string) {
  const digits = value.replace(/\D/g, "");
  if (digits.length !== 11) {
    return value;
  }
  return `***.***.***.${digits.slice(-2)}`;
}

export function SharedInvestigation() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const authToken = useAuthStore((s) => s.token);
  const forkInvestigation = useInvestigationStore((s) => s.forkInvestigation);
  const [investigation, setInvestigation] = useState<SharedInvestigationData | null>(null);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [forking, setForking] = useState(false);
  const [forkError, setForkError] = useState(false);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    getSharedInvestigation(token)
      .then(setInvestigation)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [token]);

  const handleFork = async () => {
    if (!token) return;
    setForking(true);
    setForkError(false);
    try {
      const result = await forkInvestigation(token);
      navigate(`/app/pesquisas/${result.investigation.id}`);
    } catch {
      setForkError(true);
    } finally {
      setForking(false);
    }
  };

  if (loading) {
    return <p>{t("common.loading")}</p>;
  }

  if (error || !investigation) {
    return <p className={styles.error}>{t("investigation.sharedNotFound")}</p>;
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <span className={styles.badge}>{t("investigation.sharedView")}</span>
        <h1 className={styles.title}>{investigation.title}</h1>
        {investigation.description && (
          <p className={styles.description}>{investigation.description}</p>
        )}
        <p className={styles.meta}>
          {t("investigation.created")}: {new Date(investigation.created_at).toLocaleString()}
        </p>
        <div className={styles.actions}>
          <Link to="/shared" className={styles.linkButton}>
            {t("investigation.sharedGallery")}
          </Link>
          {!IS_PUBLIC_MODE && authToken && (
            <button
              className={styles.primaryButton}
              onClick={handleFork}
              type="button"
              disabled={forking}
            >
              {forking ? t("common.loading") : t("investigation.fork")}
            </button>
          )}
          {!IS_PUBLIC_MODE && !authToken && (
            <Link to="/login" className={styles.primaryButton}>
              {t("investigation.loginToContinue")}
            </Link>
          )}
        </div>
        {forkError && <p className={styles.error}>{t("investigation.forkError")}</p>}
      </div>

      {(investigation.entity_ids ?? []).length > 0 && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>{t("investigation.entities")}</h2>
          <div className={styles.entityList}>
            {(investigation.entity_ids ?? []).map((eid) => (
              <span key={eid} className={styles.entityChip}>{maskCpf(eid)}</span>
            ))}
          </div>
        </div>
      )}

      {investigation.annotations.length > 0 && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>{t("investigation.annotations")}</h2>
          <div className={styles.annotationList}>
            {investigation.annotations.map((annotation) => (
              <article key={annotation.id} className={styles.annotationCard}>
                <p className={styles.annotationText}>{annotation.text}</p>
                <span className={styles.annotationMeta}>{maskCpf(annotation.entity_id)}</span>
              </article>
            ))}
          </div>
        </div>
      )}

      {investigation.tags.length > 0 && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>{t("investigation.tags")}</h2>
          <div className={styles.entityList}>
            {investigation.tags.map((tag) => (
              <span key={tag.id} className={styles.tagChip}>
                {tag.name}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
