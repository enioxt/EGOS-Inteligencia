import styles from "./Methodology.module.css";

export function Methodology() {
  return (
    <div className={styles.container}>
      <iframe
        src="/reports/transparencia-metodologia.html"
        className={styles.frame}
        title="Transparência e Metodologia"
      />
    </div>
  );
}
