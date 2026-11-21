"""
Pydantic v2 Schemas: Motor de Leiloes, Anti-Sniping (3 min), Realtime Events & Scanner 5-Vote Consensus
Conforms to: ADR-10, ADR-12, ADR-13, ADR-14, ADR-15 (Telas 003, 004, 041, 042, 043)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LeilaoCreateRequest(BaseModel):
    oferta_id: str = Field(..., description="UUID da oferta vinculada ao leilao")
    titulo: str = Field(..., min_length=3, max_length=150)
    categoria: str = Field(default="gpu")
    lance_inicial_centavos: int = Field(..., gt=0, description="Valor inicial em centavos (BIGINT)")
    incremento_minimo_centavos: int = Field(default=500, gt=0, description="Incremento minimo (padrao R$ 5,00 = 500 centavos)")
    duracao_segundos: int = Field(default=3600, ge=30, le=604800, description="Duracao do pregao em segundos")


class RealtimeEventPayload(BaseModel):
    channel: str
    event_name: str
    propagation_sla_ms: int = 100
    emitted_at: datetime
    data: Dict[str, Any]


class LeilaoResponse(BaseModel):
    id: str
    oferta_id: str
    seller_id: str
    titulo: str
    categoria: str
    lance_inicial_centavos: int
    incremento_minimo_centavos: int
    valor_vigente_centavos: int
    vencedor_id: Optional[str] = None
    termina_em: datetime
    server_now: datetime
    prorrogacoes_anti_sniping: int = 0
    status: str = "ABERTO"
    realtime_channel: str


class LanceCreateRequest(BaseModel):
    valor_centavos: int = Field(..., gt=0, description="Valor do lance em centavos")
    last_seen_bid_centavos: int = Field(..., ge=0, description="Ultimo valor vigente visto pelo cliente (controle de versao ADR-15)")


class LanceResponse(BaseModel):
    bid_id: str
    auction_id: str
    bidder_id: str
    valor_centavos: int
    taxa_moedas_retida: int = 5
    saldo_disponivel_apos: int
    saldo_bloqueado_apos: int
    status: str = "LEADING"
    termina_em: datetime
    anti_sniping_extended: bool = False
    prorrogacoes_anti_sniping: int = 0
    idempotent_replay: bool = False
    realtime_events: List[RealtimeEventPayload]


class ScannerHypothesisCandidate(BaseModel):
    sku: str
    model_name: str
    manufacturer: str
    category: str
    confidence: float


class ScannerDecisionRequest(BaseModel):
    image_hash: str = Field(..., min_length=8)
    top_confidence: float = Field(..., ge=0.0, le=1.0)
    detected_sku: str = Field(default="RTX-3060-12GB")
    detected_category: str = Field(default="gpu")
    is_blurry_or_low_light: bool = False
    selected_hypothesis_sku: Optional[str] = None


class ScannerDecisionResponse(BaseModel):
    decision_band: str
    confidence: float
    auto_filled_sku: Optional[str] = None
    badge: str
    coins_awarded: int
    candidates: List[ScannerHypothesisCandidate] = []
    sent_to_curation_queue: bool = False


class CommunityChallengeVoteRequest(BaseModel):
    chosen_sku: str = Field(..., min_length=2)


class CommunityChallengeVoteResponse(BaseModel):
    challenge_id: str
    voter_id: str
    chosen_sku: str
    total_votes: int
    required_votes: int = 5
    consensus_reached: bool
    winning_sku: Optional[str] = None
    agreement_ratio: float
    coins_rewarded: int
    wallet_available_balance: int
