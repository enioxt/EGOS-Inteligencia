import { useState, useMemo } from 'react';

export interface ValorRealInputs {
    // Receitas
    faturamentoBruto: number; // Mensal (R$)
    horasPorSemana: number; // Ex: 40

    // Custos Diretos PJ
    impostoSimples: number; // Porcentagem (Ex: 6%)
    contadorMensal: number; // Em R$
    equipamentoManutencao: number; // Em R$ mensal provisionado

    // Custos Ocultos (Benefícios que o PJ precisa pagar do próprio bolso)
    planoSaude: number; // Em R$
    alimentacaoVR: number; // Em R$ mensal
    inssContribuicao: number; // Porcentagem do pró-labore ou valor fixo (usaremos valor fixo R$)

    // Férias e 13º provisionados (PJ não ganha se não trabalhar)
    diasFolgaAno: number; // Quantos dias úteis pretende tirar de férias/recesso (Ex: 22 = 1 mês)
}

export interface ValorRealResults {
    // Receitas
    faturamentoAnual: number;

    // Deduções Mensais Reais
    impostoMensal: number;
    custosOperacionais: number; // Contador + Equipamento
    custosBeneficios: number; // Saúde + VR + INSS

    // Total de saídas mensais garantidas
    totalDespesasMensais: number;

    // Líquido em Caixa Mensal Ideal (se trabalhou 100% do tempo)
    liquidoMensalAparente: number;

    // O "Rombo" do PJ (Provisionamento)
    // Como PJ não recebe férias pagas e 13º, precisamos descontar o "fundo de reserva"
    // Faturamento Anual Real = Faturamento Bruto Anual - (Dias não trabalhados * Valor do dia)
    // Alternativa mais simples: dividir as receitas anuais reais por 12 meses.

    provisaoFerias13: number; // Quanto guardar por mês para simular Férias Remuneradas + 13º

    // O verdadeiro líquido comparável a um salário CLT
    liquidoRealContabil: number;

    // Métricas de Valor
    valorHoraAparente: number; // BrutoMensal / (SemanasMes * HorasSemana)
    valorHoraReal: number; // LiquidoReal / (SemanasMes * HorasSemana)

    // Qual CLT equivaleria a este PJ? (Aproximação somando benefícios e retenções no bolso)
    salarioCltEquivalente: number;
}

const WEEKS_PER_MONTH = 4.33; // Média real de semanas por mês

const DEFAULT_INPUTS: ValorRealInputs = {
    faturamentoBruto: 8000,
    horasPorSemana: 40,

    impostoSimples: 6,
    contadorMensal: 150,
    equipamentoManutencao: 200,

    planoSaude: 400,
    alimentacaoVR: 600,
    inssContribuicao: 150, // DAS/MEI ou contribuição mínima

    diasFolgaAno: 22, // 1 mês de férias padrão
};

export function useValorReal(initialData?: Partial<ValorRealInputs>) {
    const [inputs, setInputs] = useState<ValorRealInputs>({
        ...DEFAULT_INPUTS,
        ...initialData,
    });

    const results = useMemo<ValorRealResults>(() => {
        // 1. Receitas
        const faturamentoAnual = inputs.faturamentoBruto * 12;

        // 2. Despesas Mensais Diretas
        const impostoMensal = inputs.faturamentoBruto * (inputs.impostoSimples / 100);
        const custosOperacionais = inputs.contadorMensal + inputs.equipamentoManutencao;
        const custosBeneficios = inputs.planoSaude + inputs.alimentacaoVR + inputs.inssContribuicao;

        const totalDespesasMensais = impostoMensal + custosOperacionais + custosBeneficios;

        // 3. Líquido Mensal Aparente (O que sobra na conta bancária no mês sem poupar nada)
        const liquidoMensalAparente = inputs.faturamentoBruto - totalDespesasMensais;

        // 4. Provisionamento Oculto (A armadilha do PJ)
        // Se o PJ quer 1 mês de férias (22 dias úteis) + simular um 13º salário, 
        // ele precisa faturar 13.33 meses de dinheiro em 11 meses de trabalho, ou guardar parte de cada mês.
        // Provisão Mensal = (Líquido Esperado de 1 Mês de Férias + Líquido Esperado de 13º) / 12
        const totalProvisionamentoAno = (liquidoMensalAparente * 2); // 1 Férias + 1 Décimo Terceiro (simplificação)
        const provisaoFerias13 = totalProvisionamentoAno / 12;

        // 5. Verdadeiro Líquido Disponível por Mês
        const liquidoRealContabil = liquidoMensalAparente - provisaoFerias13;

        // 6. Valor Hora
        const horasMensaisTrabalhadas = inputs.horasPorSemana * WEEKS_PER_MONTH;
        const valorHoraAparente = inputs.faturamentoBruto / horasMensaisTrabalhadas;
        const valorHoraReal = liquidoRealContabil / horasMensaisTrabalhadas;

        // 7. Equivalência CLT (Reversa simples: Líquido Real + INSS CLT + IRRF Médio + Férias/13 embutidos)
        // Para um líquido X, o CLT geralmente ganha Y bruto. Margem média de 25% de descontos no CLT na faixa 5-10k.
        const salarioCltEquivalente = liquidoRealContabil / 0.75;

        return {
            faturamentoAnual,
            impostoMensal,
            custosOperacionais,
            custosBeneficios,
            totalDespesasMensais,
            liquidoMensalAparente,
            provisaoFerias13,
            liquidoRealContabil,
            valorHoraAparente,
            valorHoraReal,
            salarioCltEquivalente
        };
    }, [inputs]);

    const setInput = (key: keyof ValorRealInputs, value: number) => {
        setInputs(prev => ({ ...prev, [key]: value }));
    };

    return { inputs, setInput, results };
}
