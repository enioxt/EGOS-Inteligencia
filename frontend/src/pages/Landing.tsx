import { type ReactNode, useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router";

import { type StatsResponse, getStats } from "@/api/client";
import { FeatureCard } from "@/components/landing/FeatureCard";
import {
  GraphIcon,
  InvestigationIcon,
  PatternIcon,
} from "@/components/landing/FeatureIcons";
import { HeroSearch } from "@/components/landing/HeroSearch";
import { PartnershipCTA } from "@/components/landing/PartnershipCTA";
import { JourneyPanel } from "@/components/journey/JourneyPanel";
import { ReportsShowcase } from "@/components/landing/ReportsShowcase";
import { ETLProgress } from "@/components/landing/ETLProgress";
import { SourceRegistry } from "@/components/landing/SourceRegistry";
import { UpdatesTimeline } from "@/components/landing/UpdatesTimeline";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { IS_PATTERNS_ENABLED, IS_PUBLIC_MODE } from "@/config/runtime";

import { NetworkAnimation } from "@/components/landing/NetworkAnimation";
import { StatsBar } from "@/components/landing/StatsBar";

import styles from "./Landing.module.css";

function useReveal() {
  const setRef = useCallback((node: HTMLElement | null) => {
    if (!node) return;
    const cls = styles.revealed ?? "revealed";
    const hasMatchMedia = typeof window.matchMedia === "function";
    const prefersReduced = hasMatchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced || typeof IntersectionObserver === "undefined") {
      node.classList.add(cls);
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (entry?.isIntersecting) {
          node.classList.add(cls);
          observer.disconnect();
        }
      },
      { threshold: 0.15 },
    );
    observer.observe(node);
  }, []);
  return setRef;
}

interface FeatureDef {
  key: string;
  icon: ReactNode;
  iconBg: string;
}

const FEATURES: FeatureDef[] = [
  { key: "graph", icon: <GraphIcon />, iconBg: "var(--cyan-dim)" },
  { key: "patterns", icon: <PatternIcon />, iconBg: "var(--accent-dim)" },
  { key: "investigations", icon: <InvestigationIcon />, iconBg: "rgba(78, 168, 222, 0.12)" },
];

const STATS_CACHE_KEY = "bracc_stats_cache";

export function Landing() {
  const { t } = useTranslation();
  const chatRef = useRef<HTMLDivElement>(null);

  const featuresRef = useReveal();
  const howRef = useReveal();
  const trustRef = useReveal();

  const handleSendToChat = useCallback((query: string) => {
    if (chatRef.current) {
      chatRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
      // Dispatch custom event for ChatInterface to pick up
      window.dispatchEvent(new CustomEvent("egos-send-to-chat", { detail: { query } }));
    }
  }, []);

  const [stats, setStats] = useState<StatsResponse | null>(() => {
    try {
      const raw = localStorage.getItem(STATS_CACHE_KEY);
      return raw ? (JSON.parse(raw) as StatsResponse) : null;
    } catch {
      return null;
    }
  });

  useEffect(() => {
    getStats()
      .then((data) => {
        setStats(data);
        localStorage.setItem(STATS_CACHE_KEY, JSON.stringify(data));
      })
      .catch(() => {});
  }, []);

  const visibleFeatures = IS_PATTERNS_ENABLED
    ? FEATURES
    : FEATURES.filter((feature) => feature.key !== "patterns");

  return (
    <>
      <section className={styles.hero}>
        <NetworkAnimation />

        <div className={styles.heroContent}>
          <div className={styles.heroLeft}>
            <span className={styles.badge}>{t("landing.badge")}</span>

            <h1 className={styles.title}>{t("landing.hero")}</h1>

            <p className={styles.subtitle}>{t("landing.heroSubtitle")}</p>

            <HeroSearch onSendToChat={handleSendToChat} />

            <p className={styles.disclaimer}>{t("app.disclaimer")}</p>
          </div>

          <div className={styles.heroRight} ref={chatRef}>
            <ChatInterface embedded />
          </div>
        </div>
      </section>

      <StatsBar />

      <section className={styles.features}>
        <div ref={featuresRef} className={`${styles.featuresInner} ${styles.reveal}`}>
          <span className={styles.sectionLabel}>
            {t("landing.features.sectionLabel")}
          </span>
          <h2 className={styles.sectionHeading}>
            {t("landing.features.sectionHeading")}
          </h2>
          <div className={styles.featuresGrid}>
            {visibleFeatures.map(({ key, icon, iconBg }) => (
              <FeatureCard
                key={key}
                icon={icon}
                iconBg={iconBg}
                title={t(`landing.features.${key}`)}
                description={t(`landing.features.${key}Desc`)}
              />
            ))}
          </div>
        </div>
      </section>

      <section className={styles.howItWorks}>
        <div ref={howRef} className={`${styles.howItWorksInner} ${styles.reveal}`}>
          <span className={styles.sectionLabel}>
            {t("landing.howItWorks.sectionLabel")}
          </span>
          <h2 className={styles.sectionHeading}>
            {t("landing.howItWorks.sectionHeading")}
          </h2>
          <div className={styles.stepsGrid}>
            {[1, 2, 3].map((n) => (
              <div key={n} className={styles.step}>
                <span className={styles.stepNumber}>{n}</span>
                <span className={styles.stepTitle}>
                  {t(`landing.howItWorks.step${n}`)}
                </span>
                <span className={styles.stepDesc}>
                  {t(`landing.howItWorks.step${n}Desc`)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div ref={trustRef} className={`${styles.trust} ${styles.reveal}`}>
        <div className={styles.trustItem}>
          <span className={styles.trustValue}>{t("landing.trust.openSourceValue")}</span>
          <span className={styles.trustLabel}>{t("landing.trust.openSource")}</span>
        </div>
        <div className={styles.trustItem}>
          <span className={styles.trustValue}>{t("landing.trust.neutralValue")}</span>
          <span className={styles.trustLabel}>{t("landing.trust.neutral")}</span>
        </div>
        <div className={styles.trustItem}>
          <span className={styles.trustValue}>{stats?.data_sources ?? "—"}</span>
          <span className={styles.trustLabel}>{t("landing.trust.auditable")}</span>
        </div>
      </div>

      <ReportsShowcase />

      <ETLProgress />

      <SourceRegistry />

      <UpdatesTimeline />

      <JourneyPanel />

      <PartnershipCTA />

      <footer className={styles.footer}>
        <div className={styles.footerInner}>
          <div className={styles.footerTop}>
            <Link to={IS_PUBLIC_MODE ? "/app/search" : "/login"} className={styles.footerLink}>
              {t("landing.footer.platform")}
            </Link>
            <a href="https://github.com/enioxt/EGOS-Inteligencia" target="_blank" rel="noopener noreferrer" className={styles.footerLink}>
              GitHub
            </a>
            <span className={styles.footerLink}>
              {t("landing.footer.methodology")}
            </span>
            <span className={styles.footerLink}>
              {t("landing.footer.license")}
            </span>
          </div>
          <div className={styles.footerDivider} />
          <span className={styles.footerBrand}>{t("landing.footer.brand")}</span>
          <p className={styles.footerDisclaimer}>{t("app.disclaimer")}</p>
        </div>
      </footer>
    </>
  );
}
