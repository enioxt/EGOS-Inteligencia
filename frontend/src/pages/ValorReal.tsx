import React from 'react';
import { Calculator, DollarSign, Clock, ShieldAlert, HeartPulse, HardDrive } from 'lucide-react';
import { useValorReal } from '../hooks/use-valor-real';
import styles from './ValorReal.module.css';

const formatMoney = (val: number) =>
    val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

export const ValorReal: React.FC = () => {
    const { inputs, setInput, results } = useValorReal();

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1>Calculadora de Valor Real (PJ)</h1>
                <p>
                    O mito do Faturamento Bruto: Descubra o real valor da sua hora trabalhada como Pessoa Jurídica após descontar os custos estruturais mascarados.
                </p>
            </div>

            <div className={styles.grid}>
                {/* Lado Esquerdo - Inputs */}
                <div className={styles.card}>
                    <h2><DollarSign size={20} /> Entradas & Receitas</h2>

                    <div className={styles.inputGroup}>
                        <label>Faturamento Bruto Mensal</label>
                        <div className={styles.inputWrapper}>
                            <span className={styles.inputPrefix}>R$</span>
                            <input
                                type="number"
                                className={`${styles.input} ${styles.withPrefix}`}
                                value={inputs.faturamentoBruto}
                                onChange={(e) => setInput('faturamentoBruto', Number(e.target.value))}
                            />
                        </div>
                    </div>

                    <div className={styles.inputGroup}>
                        <label>Horas Trabalhadas por Semana</label>
                        <div className={styles.inputWrapper}>
                            <input
                                type="number"
                                className={`${styles.input} ${styles.withSuffix}`}
                                value={inputs.horasPorSemana}
                                onChange={(e) => setInput('horasPorSemana', Number(e.target.value))}
                            />
                            <span className={styles.inputSuffix}>h/sem</span>
                        </div>
                    </div>

                    <h2 style={{ marginTop: '2rem' }}><HardDrive size={20} /> Custos PJ (Obrigatórios)</h2>

                    <div className={styles.inputGroup}>
                        <label>Imposto Mensal (Simples Nacional / Presumido)</label>
                        <div className={styles.inputWrapper}>
                            <input
                                type="number"
                                className={`${styles.input} ${styles.withSuffix}`}
                                value={inputs.impostoSimples}
                                onChange={(e) => setInput('impostoSimples', Number(e.target.value))}
                            />
                            <span className={styles.inputSuffix}>%</span>
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div className={styles.inputGroup}>
                            <label>Contador</label>
                            <div className={styles.inputWrapper}>
                                <span className={styles.inputPrefix}>R$</span>
                                <input
                                    type="number"
                                    className={`${styles.input} ${styles.withPrefix}`}
                                    value={inputs.contadorMensal}
                                    onChange={(e) => setInput('contadorMensal', Number(e.target.value))}
                                />
                            </div>
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Equip. / Software</label>
                            <div className={styles.inputWrapper}>
                                <span className={styles.inputPrefix}>R$</span>
                                <input
                                    type="number"
                                    className={`${styles.input} ${styles.withPrefix}`}
                                    value={inputs.equipamentoManutencao}
                                    onChange={(e) => setInput('equipamentoManutencao', Number(e.target.value))}
                                />
                            </div>
                        </div>
                    </div>

                    <h2 style={{ marginTop: '2rem' }}><HeartPulse size={20} /> Custos Ocultos (Benefícios Ausentes)</h2>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                        Gastos essenciais que no regime CLT seriam cobertos pelo empregador.
                    </p>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div className={styles.inputGroup}>
                            <label>Plano de Saúde</label>
                            <div className={styles.inputWrapper}>
                                <span className={styles.inputPrefix}>R$</span>
                                <input
                                    type="number"
                                    className={`${styles.input} ${styles.withPrefix}`}
                                    value={inputs.planoSaude}
                                    onChange={(e) => setInput('planoSaude', Number(e.target.value))}
                                />
                            </div>
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Alimentação / VR Mensal</label>
                            <div className={styles.inputWrapper}>
                                <span className={styles.inputPrefix}>R$</span>
                                <input
                                    type="number"
                                    className={`${styles.input} ${styles.withPrefix}`}
                                    value={inputs.alimentacaoVR}
                                    onChange={(e) => setInput('alimentacaoVR', Number(e.target.value))}
                                />
                            </div>
                        </div>
                    </div>

                    <div className={styles.inputGroup}>
                        <label>INSS (Contribuição sobre Pró-Labore/MEI)</label>
                        <div className={styles.inputWrapper}>
                            <span className={styles.inputPrefix}>R$</span>
                            <input
                                type="number"
                                className={`${styles.input} ${styles.withPrefix}`}
                                value={inputs.inssContribuicao}
                                onChange={(e) => setInput('inssContribuicao', Number(e.target.value))}
                            />
                        </div>
                    </div>

                </div>

                {/* Lado Direito - Resultados */}
                <div className={styles.card}>
                    <h2><Calculator size={20} /> O Raio-X do seu Valor</h2>

                    <div className={styles.resultRow}>
                        <span className={styles.resultLabel}>Faturamento Bruto</span>
                        <span className={styles.resultValue}>{formatMoney(inputs.faturamentoBruto)}</span>
                    </div>

                    <div className={styles.resultRow}>
                        <span className={styles.resultLabel}>Impostos e Custos Operacionais</span>
                        <span className={`${styles.resultValue} ${styles.negative}`}>
                            - {formatMoney(results.impostoMensal + results.custosOperacionais)}
                        </span>
                    </div>

                    <div className={styles.resultRow}>
                        <span className={styles.resultLabel}>Custo de Benefícios (Saúde, VR, INSS)</span>
                        <span className={`${styles.resultValue} ${styles.negative}`}>
                            - {formatMoney(results.custosBeneficios)}
                        </span>
                    </div>

                    <div className={styles.resultRow} style={{ marginTop: '1rem', borderTop: '1px dashed rgba(255,255,255,0.2)' }}>
                        <span className={styles.resultLabel}>Sobra Aparente (Na Conta)</span>
                        <span className={`${styles.resultValue} ${styles.positive}`}>
                            {formatMoney(results.liquidoMensalAparente)}
                        </span>
                    </div>

                    <div className={styles.alertBox}>
                        <ShieldAlert size={24} />
                        <p>
                            <strong>A Armadilha do PJ:</strong> Você não recebe Férias nem 13º salário.
                            Para poder parar de trabalhar 30 dias por ano sem passar fome, você precisa poupar
                            sozinho uma quantia sagrada todo mês.
                        </p>
                    </div>

                    <div className={styles.resultRow}>
                        <span className={styles.resultLabel}>Fundo de Férias e 13º (Reserva Mensal)</span>
                        <span className={`${styles.resultValue} ${styles.negative}`}>
                            - {formatMoney(results.provisaoFerias13)}
                        </span>
                    </div>

                    <div className={styles.highlightBox}>
                        <h3>O Seu Líquido Real</h3>
                        <div className={styles.highlightValue}>{formatMoney(results.liquidoRealContabil)}</div>
                        <p className={styles.highlightSub}>
                            Este é o valor comparável. Equivale a um salário CLT de aproximadamente <strong>{formatMoney(results.salarioCltEquivalente)}</strong> bruto.
                        </p>
                    </div>

                    <h2 style={{ marginTop: '2.5rem' }}><Clock size={20} /> O Mito do Valor Hora</h2>

                    <div className={styles.resultRow}>
                        <span className={styles.resultLabel}>Valor Hora Aparente (Bruto)</span>
                        <span className={`${styles.resultValue} ${styles.neutral}`}>
                            {formatMoney(results.valorHoraAparente)} /h
                        </span>
                    </div>

                    <div className={styles.resultRow}>
                        <span className={styles.resultLabel}>Valor Hora <strong>REAL</strong></span>
                        <span className={`${styles.resultValue} ${styles.positive}`}>
                            {formatMoney(results.valorHoraReal)} /h
                        </span>
                    </div>

                </div>
            </div>
        </div>
    );
};
