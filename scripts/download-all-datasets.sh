#!/usr/bin/env bash
# ============================================================
# BR/ACC — Download ALL Datasets with aria2c (pause/resume)
# ============================================================
# Usage:
#   chmod +x scripts/download-all-datasets.sh
#   ./scripts/download-all-datasets.sh
#
# aria2c suporta:
#   - Pausar com Ctrl+C e continuar rodando de novo
#   - Retry automático em caso de falha
#   - Download paralelo com múltiplas conexões
#   - Resume automático (arquivo .aria2 salva progresso)
#
# Para baixar apenas um grupo:
#   ./scripts/download-all-datasets.sh --group cnpj
#   ./scripts/download-all-datasets.sh --group sanctions
#   ./scripts/download-all-datasets.sh --group tse
# ============================================================

set -euo pipefail

# --- Config ---
DATA_DIR="${DATA_DIR:-$HOME/Downloads/bracc-data}"
ARIA2_OPTS="-c -x4 --retry-wait=5 --max-tries=10 --timeout=300 --auto-file-renaming=false"
# -c            = continue/resume downloads
# -x4           = 4 connections per file (faster)
# --retry-wait  = wait 5s between retries
# --max-tries   = retry up to 10 times
# --timeout     = 300s timeout per connection

GROUP="${1:-all}"
DATE=$(date +%Y%m%d)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[BR/ACC]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err() { echo -e "${RED}[ERROR]${NC} $1"; }

download() {
    local url="$1"
    local dir="$2"
    local name="${3:-}"
    
    mkdir -p "$dir"
    
    if [ -n "$name" ]; then
        log "Downloading $name → $dir/"
        aria2c $ARIA2_OPTS -d "$dir" -o "$name" "$url" || warn "Failed: $name (will retry on next run)"
    else
        log "Downloading → $dir/"
        aria2c $ARIA2_OPTS -d "$dir" "$url" || warn "Failed: $url (will retry on next run)"
    fi
}

# ============================================================
# GRUPO 1: CNPJ — Receita Federal (~25GB compactado)
# Fonte: https://arquivos.receitafederal.gov.br/index.php/s/YggdBLfdninEJX9
# ============================================================
download_cnpj() {
    log "=========================================="
    log "CNPJ — Receita Federal (53.6M empresas)"
    log "=========================================="
    
    local DIR="$DATA_DIR/cnpj"
    local BASE="https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj"
    
    # A Receita disponibiliza os dados em vários arquivos .zip
    # Empresas (10 partes), Estabelecimentos (10 partes), Sócios (10 partes)
    # + tabelas auxiliares (Municípios, Natureza, CNAE, etc.)
    
    warn "CNPJ é ENORME (~25GB). Baixe diretamente do navegador se preferir:"
    warn "  https://arquivos.receitafederal.gov.br/index.php/s/YggdBLfdninEJX9"
    warn ""
    warn "Ou use aria2c manualmente para cada arquivo:"
    warn "  aria2c -c -x4 -d $DIR URL_DO_ARQUIVO"
    warn ""
    warn "Tip: Use o repo caiopizzol/cnpj-data-pipeline para processar os dados"
    warn "  git clone https://github.com/caiopizzol/cnpj-data-pipeline"
    warn "  cd cnpj-data-pipeline && cp .env.example .env && just up && just run"
    
    mkdir -p "$DIR"
    log "Diretório criado: $DIR"
    log "Baixe os arquivos ZIP para essa pasta e depois rode o ETL."
}

# ============================================================
# GRUPO 2: Sanções — Portal da Transparência (download manual)
# ============================================================
download_sanctions() {
    log "=========================================="
    log "Sanções — CEIS, CNEP, CEAF, CEPIM, PEP, Leniência"
    log "=========================================="
    
    local DIR="$DATA_DIR/sanctions"
    mkdir -p "$DIR"
    
    warn "Portal da Transparência BLOQUEIA downloads automáticos (captcha)."
    warn "Baixe manualmente pelo navegador:"
    echo ""
    echo "  CEIS (empresas sancionadas):"
    echo "    https://portaldatransparencia.gov.br/download-de-dados/ceis"
    echo ""
    echo "  CNEP (empresas punidas):"
    echo "    https://portaldatransparencia.gov.br/download-de-dados/cnep"
    echo ""
    echo "  CEAF (servidores expulsos):"
    echo "    https://portaldatransparencia.gov.br/download-de-dados/ceaf"
    echo ""
    echo "  CEPIM (ONGs impedidas):"
    echo "    https://portaldatransparencia.gov.br/download-de-dados/cepim"
    echo ""
    echo "  PEP (Pessoas Expostas Politicamente):"
    echo "    https://portaldatransparencia.gov.br/download-de-dados/pep"
    echo ""
    echo "  Acordos de Leniência:"
    echo "    https://portaldatransparencia.gov.br/download-de-dados/acordos-leniencia"
    echo ""
    echo "  CPGF (Cartão de Pagamento do Governo):"
    echo "    https://portaldatransparencia.gov.br/download-de-dados/cpgf"
    echo ""
    echo "  Viagens a Serviço:"
    echo "    https://portaldatransparencia.gov.br/download-de-dados/viagens"
    echo ""
    log "Salve os ZIPs em: $DIR"
    log "Depois rode: cd /opt/bracc/etl && python3 scripts/download_sanctions.py --output-dir $DIR"
}

# ============================================================
# GRUPO 3: TSE — Tribunal Superior Eleitoral (download direto!)
# ============================================================
download_tse() {
    log "=========================================="
    log "TSE — Candidaturas, Doações, Bens, Filiados"
    log "=========================================="
    
    local DIR="$DATA_DIR/tse"
    local BASE="https://cdn.tse.jus.br/estatistica/sead/odsele"
    
    # Candidaturas (últimas 3 eleições)
    for year in 2018 2020 2022 2024; do
        download "$BASE/consulta_cand/consulta_cand_${year}.zip" "$DIR/candidaturas" "consulta_cand_${year}.zip"
    done
    
    # Prestação de Contas (doações)
    for year in 2018 2020 2022 2024; do
        download "$BASE/prestacao_contas/prestacao_de_contas_eleitorais_candidatos_${year}.zip" "$DIR/doacoes" "doacoes_${year}.zip"
    done
    
    # Bens de Candidatos
    for year in 2018 2020 2022 2024; do
        download "$BASE/bem_candidato/bem_candidato_${year}.zip" "$DIR/bens" "bens_${year}.zip"
    done
    
    # Filiados (todos os partidos — URL genérica)
    warn "Filiados: baixe em https://dadosabertos.tse.jus.br/dataset/filiados"
    
    log "TSE downloads complete! Dir: $DIR"
}

# ============================================================
# GRUPO 4: OpenSanctions (download direto — API aberta)
# ============================================================
download_opensanctions() {
    log "=========================================="
    log "OpenSanctions — 4.1M entidades globais"
    log "=========================================="
    
    local DIR="$DATA_DIR/opensanctions"
    
    download "https://data.opensanctions.org/datasets/latest/default/entities.ftm.json" \
        "$DIR" "entities.ftm.json"
    
    download "https://data.opensanctions.org/datasets/latest/br_transparency/entities.ftm.json" \
        "$DIR" "br_transparency.ftm.json"
    
    log "OpenSanctions done!"
}

# ============================================================
# GRUPO 5: ICIJ — Panama/Pandora Papers (download direto)
# ============================================================
download_icij() {
    log "=========================================="
    log "ICIJ — Offshore Leaks (Panama/Pandora Papers)"
    log "=========================================="
    
    local DIR="$DATA_DIR/icij"
    
    download "https://offshoreleaks-data.icij.org/offshoreleaks/csv/full-oldb.LATEST.zip" \
        "$DIR" "full-oldb.LATEST.zip"
    
    log "ICIJ done! Unzip: cd $DIR && unzip full-oldb.LATEST.zip"
}

# ============================================================
# GRUPO 6: Câmara dos Deputados (API REST aberta)
# ============================================================
download_camara() {
    log "=========================================="
    log "Câmara dos Deputados — Gastos, Deputados"
    log "=========================================="
    
    local DIR="$DATA_DIR/camara"
    local BASE="https://dadosabertos.camara.leg.br/arquivos"
    
    # Deputados (últimas legislaturas)
    for leg in 56 57; do
        download "$BASE/deputados/csv/deputados-legislatura-${leg}.csv" "$DIR" "deputados-leg${leg}.csv"
    done
    
    # Despesas (CEAP)
    for year in 2023 2024 2025 2026; do
        download "$BASE/despesas/csv/Ano-${year}.csv" "$DIR" "despesas-${year}.csv"
    done
    
    log "Câmara done!"
}

# ============================================================
# GRUPO 7: Senado Federal
# ============================================================
download_senado() {
    log "=========================================="
    log "Senado Federal — Gastos, Senadores"
    log "=========================================="
    
    local DIR="$DATA_DIR/senado"
    
    download "https://www12.senado.leg.br/dados-abertos/arquivos/lista-senadores-exercicio" \
        "$DIR" "senadores-exercicio.json"
    
    for year in 2023 2024 2025 2026; do
        download "https://www12.senado.leg.br/transparencia/dados-abertos-transparencia/arquivos/ceaps-desde-${year}.csv" \
            "$DIR" "ceaps-${year}.csv"
    done
    
    log "Senado done!"
}

# ============================================================
# GRUPO 8: DataJud CNJ — Processos Judiciais
# ============================================================
download_datajud() {
    log "=========================================="
    log "DataJud CNJ — ~80M processos judiciais"
    log "=========================================="
    
    warn "DataJud requer API key gratuita:"
    warn "  1. Acesse: https://datajud-wiki.cnj.jus.br/"
    warn "  2. Solicite chave de API"
    warn "  3. Use o script: python3 scripts/download_datajud.py --api-key SUA_CHAVE"
}

# ============================================================
# GRUPO 9: BCB — Banco Central (API REST aberta)
# ============================================================
download_bcb() {
    log "=========================================="
    log "BCB — Banco Central do Brasil"
    log "=========================================="
    
    local DIR="$DATA_DIR/bcb"
    mkdir -p "$DIR"
    
    # IF.data (Instituições Financeiras)
    download "https://www3.bcb.gov.br/ifdata/rest/arquivos?tipo=1" \
        "$DIR" "ifdata_bancos.json"
    
    log "BCB: Use o ETL pipeline para séries completas"
    log "  python3 scripts/download_bcb.py --output-dir $DIR"
}

# ============================================================
# GRUPO 10: Querido Diário (API aberta — 5570+ municípios)
# ============================================================
download_querido_diario() {
    log "=========================================="
    log "Querido Diário — Diários Oficiais Municipais"
    log "=========================================="
    
    warn "Querido Diário é consultado via API (não precisa download bulk)"
    warn "API: https://queridodiario.ok.org.br/api/docs"
    warn "Já integrado no bot Discord!"
}

# ============================================================
# MAIN
# ============================================================
main() {
    echo ""
    log "╔══════════════════════════════════════════════════════════════╗"
    log "║  BR/ACC Dataset Downloader — aria2c (pause/resume)         ║"
    log "║  Data dir: $DATA_DIR"
    log "║  Date: $DATE"
    log "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    case "$GROUP" in
        all)
            download_cnpj
            echo ""; download_sanctions
            echo ""; download_tse
            echo ""; download_opensanctions
            echo ""; download_icij
            echo ""; download_camara
            echo ""; download_senado
            echo ""; download_datajud
            echo ""; download_bcb
            echo ""; download_querido_diario
            ;;
        cnpj) download_cnpj ;;
        sanctions) download_sanctions ;;
        tse) download_tse ;;
        opensanctions) download_opensanctions ;;
        icij) download_icij ;;
        camara) download_camara ;;
        senado) download_senado ;;
        datajud) download_datajud ;;
        bcb) download_bcb ;;
        *) err "Unknown group: $GROUP. Use: all, cnpj, sanctions, tse, opensanctions, icij, camara, senado, datajud, bcb" ;;
    esac
    
    echo ""
    log "════════════════════════════════════════════════"
    log "PRÓXIMOS PASSOS:"
    log "  1. Copie os dados para o servidor:"
    log "     scp -r $DATA_DIR/* root@217.216.95.126:/opt/bracc/data/"
    log "  2. Rode os ETL pipelines:"
    log "     ssh root@217.216.95.126 'cd /opt/bracc/etl && source .venv/bin/activate && python3 -m bracc_etl.runner --all'"
    log "════════════════════════════════════════════════"
    echo ""
    log "💡 Dicas aria2c:"
    log "  - Ctrl+C para pausar qualquer download"
    log "  - Rode o mesmo comando para continuar de onde parou"
    log "  - Progresso salvo em arquivos .aria2 (não delete!)"
    log "  - Se fechar o terminal, rode de novo — continua automaticamente"
}

main
