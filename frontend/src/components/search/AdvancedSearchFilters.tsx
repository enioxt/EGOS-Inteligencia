import React, { useState } from "react";
import { Search, MapPin, AlertTriangle, Building, Briefcase } from "lucide-react";
import styles from "./AdvancedSearchFilters.module.css";

export interface OSINTFilters {
    isPep: boolean;
    hasSanctions: boolean;
    hasContracts: boolean;
    city?: string;
    state?: string;
}

interface AdvancedSearchFiltersProps {
    filters: OSINTFilters;
    onFilterChange: (filters: OSINTFilters) => void;
}

export function AdvancedSearchFilters({ filters, onFilterChange }: AdvancedSearchFiltersProps) {
    const [isOpen, setIsOpen] = useState(false);

    const toggleFilter = (key: keyof OSINTFilters, value: boolean) => {
        onFilterChange({ ...filters, [key]: value });
    };

    const handleCityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onFilterChange({ ...filters, city: e.target.value });
    };

    const handleStateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        onFilterChange({ ...filters, state: e.target.value });
    };

    return (
        <div className={styles.container}>
            <button
                className={styles.toggleBtn}
                onClick={() => setIsOpen(!isOpen)}
                type="button"
            >
                <Search className="w-4 h-4" />
                Filtros OSINT Avançados
                <span className={styles.badge}>
                    {(filters.isPep ? 1 : 0) + (filters.hasSanctions ? 1 : 0) + (filters.hasContracts ? 1 : 0) + (filters.city ? 1 : 0)}
                </span>
            </button>

            {isOpen && (
                <div className={styles.filterBox}>
                    <div className={styles.pills}>
                        <button
                            type="button"
                            className={`${styles.pill} ${filters.isPep ? styles.activePep : ''}`}
                            onClick={() => toggleFilter('isPep', !filters.isPep)}
                        >
                            <Briefcase className="w-3 h-3" /> PEP (Exposta Politicamente)
                        </button>
                        <button
                            type="button"
                            className={`${styles.pill} ${filters.hasSanctions ? styles.activeSanction : ''}`}
                            onClick={() => toggleFilter('hasSanctions', !filters.hasSanctions)}
                        >
                            <AlertTriangle className="w-3 h-3" /> Com Sanções (CEIS/CNEP)
                        </button>
                        <button
                            type="button"
                            className={`${styles.pill} ${filters.hasContracts ? styles.activeContract : ''}`}
                            onClick={() => toggleFilter('hasContracts', !filters.hasContracts)}
                        >
                            <Building className="w-3 h-3" /> Recebeu Recurso Público
                        </button>
                    </div>

                    <div className={styles.locationControls}>
                        <MapPin className="w-4 h-4 text-muted" />
                        <select
                            className={styles.select}
                            value={filters.state || ""}
                            onChange={handleStateChange}
                        >
                            <option value="">Qualquer UF</option>
                            {['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'].map(uf => (
                                <option key={uf} value={uf}>{uf}</option>
                            ))}
                        </select>
                        <input
                            type="text"
                            className={styles.input}
                            placeholder="Cidade (opcional)"
                            value={filters.city || ""}
                            onChange={handleCityChange}
                        />
                    </div>
                </div>
            )}
        </div>
    );
}
