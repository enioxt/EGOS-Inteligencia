import { useTranslation } from "react-i18next";
import { Link, Outlet } from "react-router";

import { IS_PUBLIC_MODE } from "@/config/runtime";
import { useAuthStore } from "@/stores/auth";

import styles from "./PublicShell.module.css";

export function PublicShell() {
  const { t, i18n } = useTranslation();
  const token = useAuthStore((s) => s.token);

  const toggleLang = () => {
    const next = i18n.language === "pt-BR" ? "en" : "pt-BR";
    i18n.changeLanguage(next);
  };

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <Link to="/" className={styles.logo}>
          {t("app.title")}
        </Link>

        <nav className={styles.nav}>
          <Link to="/app/search" className={styles.navLink}>
            {i18n.language === "pt-BR" ? "Pesquisar" : "Search"}
          </Link>
          <Link to="/app/reports" className={styles.navLink}>
            {i18n.language === "pt-BR" ? "Relatórios" : "Reports"}
          </Link>
          <Link to="/app/analytics" className={styles.navLink}>
            {i18n.language === "pt-BR" ? "Estatísticas" : "Analytics"}
          </Link>
          <a
            href="https://github.com/enioxt/EGOS-Inteligencia"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.navLink}
          >
            GitHub
          </a>
        </nav>

        <div className={styles.actions}>
          {IS_PUBLIC_MODE ? (
            <Link to="/app" className={styles.registerLink}>
              {i18n.language === "pt-BR" ? "Abrir Plataforma" : "Open Platform"}
            </Link>
          ) : !token && (
            <>
              <Link to="/login" className={styles.authLink}>
                {t("nav.login")}
              </Link>
              <Link to="/register" className={styles.registerLink}>
                {t("nav.register")}
              </Link>
            </>
          )}
          <button
            onClick={toggleLang}
            className={styles.langToggle}
            type="button"
          >
            {i18n.language === "pt-BR" ? "EN" : "PT"}
          </button>
        </div>
      </header>
      <main className={styles.content}>
        <Outlet />
      </main>
    </div>
  );
}
