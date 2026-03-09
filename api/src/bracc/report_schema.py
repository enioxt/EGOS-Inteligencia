"""Investigation Report Schema — canonical structure for any LLM-generated report.

See docs/REPORT_STANDARD.md for the full specification.
Any model (Gemini Flash, GPT-4o-mini, Claude Haiku) MUST follow this schema.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    HIGH = "alta"
    MEDIUM = "media"
    LOW = "baixa"


class EntityType(str, Enum):
    COMPANY = "company"
    PERSON = "person"
    GROUP = "group"
    SECTOR = "sector"


# --- Sub-models ---


class GeneratedBy(BaseModel):
    model: str = Field(description="LLM model used, e.g. 'openai/gpt-4o-mini'")
    cost_brl: float = Field(default=0.0, description="Estimated cost in BRL")
    platform: str = Field(default="EGOS Inteligência")


class KeyNumber(BaseModel):
    label: str
    value: str
    context: str = ""


class EntityField(BaseModel):
    field: str
    value: str
    source: str


class OwnershipEntry(BaseModel):
    name: str
    role: str = Field(description="Sócio | Administrador | Diretor")
    type: str = Field(description="PF | PJ")
    document: str = Field(default="", description="CPF mascarado ou CNPJ")
    alert: str = Field(default="", description="Alerta se sócio PJ ou padrão suspeito")


class ConnectionType(BaseModel):
    type: str = Field(description="SOCIO_DE, SANCIONADA, DOOU, VENCEU, etc.")
    count: int


class GraphAnalysis(BaseModel):
    found_in_graph: bool
    node_type: str = ""
    total_connections: int = 0
    connection_types: list[ConnectionType] = []
    multi_hop_paths: Optional[str] = None


class SourceCheck(BaseModel):
    source: str = Field(description="Nome da base: CEIS, CNEP, PEP, OpenSanctions, BNDES, etc.")
    result: str = Field(description="Encontrado | Nenhum registro | Pendente")
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH
    details: str = ""
    api_url: str = ""
    total_value: str = ""


class Observation(BaseModel):
    number: int
    title: str
    description: str = Field(description="Factual, sem acusações. Dados e números.")
    data_points: list[str] = []
    sources: list[str] = []


class GapItem(BaseModel):
    data: str = Field(description="O que falta")
    reason: str = Field(description="Por que não temos")
    when: str = Field(default="", description="ETA")
    impact: str = Field(default="", description="Como afeta a análise")


class SourceEntry(BaseModel):
    number: int
    name: str
    url: str = ""
    consulted_at: str = ""
    records_count: str = ""


# --- Main Report ---


LEGAL_DISCLAIMER = (
    "Este relatório apresenta exclusivamente dados de acesso público, "
    "obtidos via APIs oficiais do governo brasileiro e datasets abertos. "
    "Não constitui acusação, denúncia ou parecer jurídico. "
    "As observações aqui contidas são compilações factuais de registros públicos, "
    "cabendo aos órgãos competentes qualquer apuração. "
    "O objetivo desta plataforma é promover transparência e acesso à informação pública."
)


class InvestigationReport(BaseModel):
    """Canonical investigation report schema.

    Any LLM generating a report MUST populate all required fields.
    Language rules: never accuse, always cite source, mask CPFs.
    """

    report_id: str = Field(description="REPORT-YYYY-NNN")
    version: str = Field(default="1.0")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_by: GeneratedBy

    # Metadata
    title: str
    subtitle: str = ""
    entity_type: EntityType
    sources_count: int = 0
    observations_count: int = 0
    confidence_overall: ConfidenceLevel = ConfidenceLevel.MEDIUM

    # Required sections
    legal_disclaimer: str = Field(default=LEGAL_DISCLAIMER)
    summary: str = Field(description="Executive summary, max 200 words")
    key_numbers: list[KeyNumber] = []
    entity_data: list[EntityField] = Field(description="CNPJ, situação, endereço, etc.")
    ownership: list[OwnershipEntry] = Field(
        default=[],
        description="QSA / vínculos. Se vazio, explicar no gap.",
    )
    graph_analysis: GraphAnalysis
    source_checks: list[SourceCheck] = Field(
        min_length=1,
        description="Min 1 base verificada. Idealmente todas as 8 bases.",
    )
    observations: list[Observation] = Field(
        min_length=1,
        description="Observações factuais. NUNCA acusações.",
    )
    gaps: list[GapItem] = Field(
        description="O que NÃO foi encontrado e por quê.",
    )
    sources_list: list[SourceEntry] = Field(
        min_length=1,
        description="Todas as fontes com URL e data.",
    )

    # Optional sections
    methodology: str = ""
    citizen_steps: list[str] = []
    developer_steps: list[str] = []


# --- Prompt template for LLM report generation ---

REPORT_GENERATION_PROMPT = """Você é um analista de dados públicos da plataforma EGOS Inteligência.
Sua tarefa é gerar um relatório de investigação seguindo RIGOROSAMENTE o schema abaixo.

REGRAS ABSOLUTAS:
1. NUNCA acusar — apenas compilar fatos públicos
2. SEMPRE citar fonte, URL e data de consulta
3. SEMPRE informar nível de confiança (alta/média/baixa)
4. SEMPRE listar gaps (o que não foi encontrado)
5. CPFs SEMPRE mascarados: ***.***.***-XX
6. Linguagem: "Registros indicam...", "Conforme dados do...", "Observa-se que..."
7. NUNCA: "corrupto", "fraude", "lavagem", "certamente"

SCHEMA (preencha todos os campos obrigatórios):
{schema}

DADOS DISPONÍVEIS:
{data}

Gere o relatório completo em JSON seguindo o schema acima."""
