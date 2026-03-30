import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import type { Investigation } from "@/api/client";
import { listSharedInvestigations } from "@/api/client";

import styles from "./SharedInvestigations.module.css";

export function SharedInvestigations() {
  const { t } = useTranslation();
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    setLoading(true);
    listSharedInvestigations()
      .then((response) => {
        setInvestigations(response.investigations);
        setError(false);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p>{t("common.loading")}</p>;
  }

  if (error) {
    return <p className={styles.error}>{t("investigation.sharedListError")}</p>;
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <span className={styles.badge}>{t("investigation.sharedGallery")}</span>
        <h1 className={styles.title}>{t("investigation.sharedGalleryTitle")}</h1>
        <p className={styles.description}>{t("investigation.sharedGalleryDescription")}</p>
      </div>

      {investigations.length === 0 ? (
        <p className={styles.empty}>{t("investigation.noSharedInvestigations")}</p>
      ) : (
        <div className={styles.grid}>
          {investigations.map((investigation) => (
            <Link
              key={investigation.id}
              to={`/shared/${investigation.share_token}`}
              className={styles.card}
            >
              <h2 className={styles.cardTitle}>{investigation.title}</h2>
              {investigation.description && (
                <p className={styles.cardDescription}>{investigation.description}</p>
              )}
              <div className={styles.cardMeta}>
                <span>
                  {(investigation.entity_ids ?? []).length} {t("investigation.entities")}
                </span>
                <span>{new Date(investigation.updated_at).toLocaleDateString()}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
