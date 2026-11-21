"""
FastAPI Router: Motor de Leiloes (SELECT FOR UPDATE, Anti-Sniping 3 min, Realtime <= 100ms)
& Integracao Scanner IA (3 Faixas de Confianca ADR-12 + Desafio Consenso 5 Votos)
Conforms to: RB-01, RB-09, RB-10, ADR-09, ADR-10, ADR-12, ADR-13, ADR-14, ADR-15
Telas atendidas: PROTOTIPAGEM_003, 004, 041, 042, 043
"""

from collections import Counter
from datetime import datetime, timedelta, timezone
import threading
from typing import Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, Header, status

from app.api.deps import get_current_user
from app.core.errors import ProblemException
from app.schemas.auth import AuthenticatedUserPayload
from app.schemas.leilao import (
    CommunityChallengeVoteRequest,
    CommunityChallengeVoteResponse,
    LanceCreateRequest,
    LanceResponse,
    LeilaoCreateRequest,
    LeilaoResponse,
    RealtimeEventPayload,
    ScannerDecisionRequest,
    ScannerDecisionResponse,
    ScannerHypothesisCandidate,
)

router = APIRouter()

# Row-level mutexes simulating PostgreSQL SELECT ... FOR UPDATE per auction & deterministic wallet order
_AUCTION_LOCKS: Dict[str, threading.Lock] = {}
_GLOBAL_LOCK = threading.Lock()

AUCTIONS_STORE: Dict[str, Dict] = {}
BIDS_BY_IDEMPOTENCY: Dict[str, LanceResponse] = {}
BIDS_HISTORY: Dict[str, List[Dict]] = {}
WALLETS_STORE: Dict[str, Dict[str, int]] = {}
CHALLENGES_STORE: Dict[str, Dict] = {
    "chal-gpu-001": {
        "id": "chal-gpu-001",
        "image_url": "storage://offers-media/challenges/rtx3060_twin_edge.webp",
        "options": ["ZOTAC-RTX-3060-12GB", "ZOTAC-RTX-3060-TI-8GB", "ASUS-DUAL-RTX-3060"],
        "votes": {},  # user_id -> chosen_sku
        "resolved_sku": None,
    }
}

ANTI_SNIPING_WINDOW_SECONDS = 180  # 3 minutes (ADR-15 / SPRINT15_005)
ANTI_SNIPING_EXTENSION_SECONDS = 180  # +3 minutes
MAX_ANTI_SNIPING_EXTENSIONS = 10
BID_HOLD_FEE_COINS = 5


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _get_or_init_wallet(user_id: str) -> Dict[str, int]:
    if user_id not in WALLETS_STORE:
        WALLETS_STORE[user_id] = {"available": 100, "locked": 0, "daily_minted": 0}
    return WALLETS_STORE[user_id]


def _enforce_eligibility(user: AuthenticatedUserPayload) -> None:
    """Defense-in-depth RB-01 (KYC) and RB-10 (Trust Score >= 70)."""
    if not user.kyc_verified:
        raise ProblemException(
            status_code=status.HTTP_403_FORBIDDEN,
            title="KYC Verification Required",
            detail="Participacao em leiloes exclusivos e recompensas exige KYC verificado (RB-01).",
            type_uri="https://steely.com.br/errors/kyc-required",
        )
    if user.trust_score < 70.0:
        raise ProblemException(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Trust Score Below Threshold",
            detail=f"Trust Score ({user.trust_score}) abaixo do minimo exigido de 70% (RB-10).",
            type_uri="https://steely.com.br/errors/low-trust-score",
        )


@router.post(
    "/",
    response_model=LeilaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria leilao exclusivo de hardware com relogio oficial do servidor (ADR-15)",
)
async def criar_leilao(
    payload: LeilaoCreateRequest,
    current_user: AuthenticatedUserPayload = Depends(get_current_user),
) -> LeilaoResponse:
    _enforce_eligibility(current_user)
    now = _now_utc()
    auction_id = f"auc-{uuid.uuid4().hex[:10]}"
    ends_at = now + timedelta(seconds=payload.duracao_segundos)

    record = {
        "id": auction_id,
        "oferta_id": payload.oferta_id,
        "seller_id": current_user.user_id,
        "titulo": payload.titulo,
        "categoria": payload.categoria.lower(),
        "lance_inicial_centavos": payload.lance_inicial_centavos,
        "incremento_minimo_centavos": payload.incremento_minimo_centavos,
        "valor_vigente_centavos": 0,
        "vencedor_id": None,
        "termina_em": ends_at,
        "prorrogacoes_anti_sniping": 0,
        "status": "ABERTO",
        "realtime_channel": f"realtime:auctions:{auction_id}",
    }
    with _GLOBAL_LOCK:
        AUCTIONS_STORE[auction_id] = record
        _AUCTION_LOCKS[auction_id] = threading.Lock()
        BIDS_HISTORY[auction_id] = []

    return LeilaoResponse(**record, server_now=now)


@router.get(
    "/",
    response_model=List[LeilaoResponse],
    summary="Lista leiloes ativos com server_now para sincronizacao de cronometro",
)
async def listar_leiloes() -> List[LeilaoResponse]:
    now = _now_utc()
    return [LeilaoResponse(**auc, server_now=now) for auc in AUCTIONS_STORE.values()]


@router.get(
    "/{auction_id}",
    response_model=LeilaoResponse,
    summary="Consulta estado do leilao e deslocamento de relogio do servidor",
)
async def obter_leilao(auction_id: str) -> LeilaoResponse:
    if auction_id not in AUCTIONS_STORE:
        raise ProblemException(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Auction Not Found",
            detail=f"Leilao {auction_id} nao encontrado.",
        )
    return LeilaoResponse(**AUCTIONS_STORE[auction_id], server_now=_now_utc())


@router.post(
    "/{auction_id}/lances",
    response_model=LanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra lance atomico com SELECT FOR UPDATE, reserva de 5 moedas e Anti-Sniping de 3 min (ADR-15)",
)
async def dar_lance(
    auction_id: str,
    payload: LanceCreateRequest,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    current_user: AuthenticatedUserPayload = Depends(get_current_user),
) -> LanceResponse:
    _enforce_eligibility(current_user)

    if not idempotency_key or not idempotency_key.strip():
        raise ProblemException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Missing Idempotency-Key",
            detail="Cabecalho Idempotency-Key e obrigatorio para lances (ADR-14 / ADR-15).",
        )

    idem_scoped = f"{current_user.user_id}:{auction_id}:{idempotency_key.strip()}"
    if idem_scoped in BIDS_BY_IDEMPOTENCY:
        cached = BIDS_BY_IDEMPOTENCY[idem_scoped].model_copy(deep=True)
        cached.idempotent_replay = True
        return cached

    if auction_id not in AUCTIONS_STORE:
        raise ProblemException(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Auction Not Found",
            detail=f"Leilao {auction_id} nao encontrado.",
        )

    auction_lock = _AUCTION_LOCKS[auction_id]
    # Pessimistic Lock (SELECT ... FOR UPDATE on auction row + wallets)
    with auction_lock:
        auc = AUCTIONS_STORE[auction_id]
        now = _now_utc()

        if auc["status"] != "ABERTO" or now >= auc["termina_em"]:
            auc["status"] = "ENCERRADO"
            raise ProblemException(
                status_code=status.HTTP_409_CONFLICT,
                title="Auction Closed",
                detail="Este leilao ja foi encerrado pelo relogio do servidor.",
                type_uri="https://steely.com.br/errors/auction-closed",
            )

        if payload.last_seen_bid_centavos != auc["valor_vigente_centavos"]:
            raise ProblemException(
                status_code=status.HTTP_409_CONFLICT,
                title="BID_OUTDATED",
                detail=(
                    f"O valor vigente mudou para {auc['valor_vigente_centavos']} centavos "
                    f"(lastSeenBid enviado: {payload.last_seen_bid_centavos})."
                ),
                type_uri="https://steely.com.br/errors/bid-outdated",
            )

        if auc["vencedor_id"] == current_user.user_id:
            raise ProblemException(
                status_code=status.HTTP_409_CONFLICT,
                title="ALREADY_LEADING",
                detail="Voce ja e o lider atual deste leilao (ADR-15).",
                type_uri="https://steely.com.br/errors/already-leading",
            )

        min_required = (
            auc["lance_inicial_centavos"]
            if auc["valor_vigente_centavos"] == 0
            else auc["valor_vigente_centavos"] + auc["incremento_minimo_centavos"]
        )
        if payload.valor_centavos < min_required:
            raise ProblemException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                title="Bid Below Minimum Increment",
                detail=f"O lance minimo exigido e de {min_required} centavos.",
            )

        bidder_wallet = _get_or_init_wallet(current_user.user_id)
        if bidder_wallet["available"] < BID_HOLD_FEE_COINS:
            raise ProblemException(
                status_code=status.HTTP_409_CONFLICT,
                title="Insufficient Coins for BID_HOLD",
                detail="Saldo insuficiente para reservar a taxa de participacao de 5 moedas (RB-09 / ADR-10).",
            )

        # 1. BID_HOLD on new leader (5 coins moved from available -> locked)
        bidder_wallet["available"] -= BID_HOLD_FEE_COINS
        bidder_wallet["locked"] += BID_HOLD_FEE_COINS

        # 2. BID_RELEASE on previous leader (5 coins returned from locked -> available)
        prev_leader = auc["vencedor_id"]
        if prev_leader is not None:
            prev_wallet = _get_or_init_wallet(prev_leader)
            prev_wallet["locked"] = max(0, prev_wallet["locked"] - BID_HOLD_FEE_COINS)
            prev_wallet["available"] += BID_HOLD_FEE_COINS
            for b in BIDS_HISTORY[auction_id]:
                if b["status"] == "LEADING":
                    b["status"] = "OUTBID"

        # 3. Anti-Sniping: extend ends_at by +3 minutes (180s) if remaining <= 3 minutes (up to 10 extensions)
        remaining_sec = (auc["termina_em"] - now).total_seconds()
        extended = False
        if remaining_sec <= ANTI_SNIPING_WINDOW_SECONDS and auc["prorrogacoes_anti_sniping"] < MAX_ANTI_SNIPING_EXTENSIONS:
            auc["termina_em"] = auc["termina_em"] + timedelta(seconds=ANTI_SNIPING_EXTENSION_SECONDS)
            auc["prorrogacoes_anti_sniping"] += 1
            extended = True

        auc["valor_vigente_centavos"] = payload.valor_centavos
        auc["vencedor_id"] = current_user.user_id

        bid_id = f"bid-{uuid.uuid4().hex[:10]}"
        BIDS_HISTORY[auction_id].append(
            {
                "bid_id": bid_id,
                "bidder_id": current_user.user_id,
                "valor_centavos": payload.valor_centavos,
                "status": "LEADING",
                "created_at": now,
            }
        )

        # 4. Realtime Broadcast Events (<= 100ms SLA - RNF-06 / ADR-13 / ADR-15)
        events = [
            RealtimeEventPayload(
                channel=auc["realtime_channel"],
                event_name="bid.accepted",
                propagation_sla_ms=100,
                emitted_at=now,
                data={
                    "auction_id": auction_id,
                    "bid_id": bid_id,
                    "leader_id": current_user.user_id,
                    "current_price_cents": payload.valor_centavos,
                    "ends_at": auc["termina_em"].isoformat(),
                },
            )
        ]
        if extended:
            events.append(
                RealtimeEventPayload(
                    channel=auc["realtime_channel"],
                    event_name="auction.extended",
                    propagation_sla_ms=100,
                    emitted_at=now,
                    data={
                        "auction_id": auction_id,
                        "new_ends_at": auc["termina_em"].isoformat(),
                        "extensions_count": auc["prorrogacoes_anti_sniping"],
                    },
                )
            )

        resp = LanceResponse(
            bid_id=bid_id,
            auction_id=auction_id,
            bidder_id=current_user.user_id,
            valor_centavos=payload.valor_centavos,
            taxa_moedas_retida=BID_HOLD_FEE_COINS,
            saldo_disponivel_apos=bidder_wallet["available"],
            saldo_bloqueado_apos=bidder_wallet["locked"],
            status="LEADING",
            termina_em=auc["termina_em"],
            anti_sniping_extended=extended,
            prorrogacoes_anti_sniping=auc["prorrogacoes_anti_sniping"],
            idempotent_replay=False,
            realtime_events=events,
        )
        BIDS_BY_IDEMPOTENCY[idem_scoped] = resp
        return resp


@router.post(
    "/scanner/analyze",
    response_model=ScannerDecisionResponse,
    summary="Motor de limiares do Scanner IA em 3 faixas: >=80% Auto L5, 50-79% Top-3 Hipoteses, <50% Manual (ADR-12)",
)
async def analisar_limiar_scanner(
    payload: ScannerDecisionRequest,
    current_user: AuthenticatedUserPayload = Depends(get_current_user),
) -> ScannerDecisionResponse:
    # Stage 0: Image quality gate (ADR-12 / STY017-RN02)
    if payload.is_blurry_or_low_light:
        return ScannerDecisionResponse(
            decision_band="LOW_QUALITY_RECAPTURE",
            confidence=0.0,
            auto_filled_sku=None,
            badge="Recaptura Necessaria",
            coins_awarded=0,
            candidates=[],
            sent_to_curation_queue=False,
        )

    wallet = _get_or_init_wallet(current_user.user_id)

    # Green Band: >= 0.80 -> Auto-fill L5 + "Identificado por IA" + 15 coins
    if payload.top_confidence >= 0.80:
        reward = 15 if (current_user.trust_score >= 70.0 and wallet["daily_minted"] + 15 <= 200) else 0
        wallet["available"] += reward
        wallet["daily_minted"] += reward
        return ScannerDecisionResponse(
            decision_band="AUTO_L5",
            confidence=payload.top_confidence,
            auto_filled_sku=payload.detected_sku,
            badge="Identificado por IA",
            coins_awarded=reward,
            candidates=[
                ScannerHypothesisCandidate(
                    sku=payload.detected_sku,
                    model_name=payload.detected_sku.replace("-", " "),
                    manufacturer="NVIDIA / Parceiro",
                    category=payload.detected_category,
                    confidence=payload.top_confidence,
                )
            ],
            sent_to_curation_queue=False,
        )

    # Yellow Band: 0.50 <= score < 0.80 -> Top-3 Hypotheses (STY017-RN03)
    if payload.top_confidence >= 0.50:
        top3 = [
            ScannerHypothesisCandidate(
                sku=payload.detected_sku,
                model_name=f"{payload.detected_sku} OC Edition",
                manufacturer="ASUS",
                category=payload.detected_category,
                confidence=payload.top_confidence,
            ),
            ScannerHypothesisCandidate(
                sku=f"{payload.detected_sku}-TI",
                model_name=f"{payload.detected_sku} Ti Twin Edge",
                manufacturer="ZOTAC",
                category=payload.detected_category,
                confidence=round(max(0.25, payload.top_confidence - 0.12), 3),
            ),
            ScannerHypothesisCandidate(
                sku=f"{payload.detected_sku}-VENTUS",
                model_name=f"{payload.detected_sku} Ventus 2X",
                manufacturer="MSI",
                category=payload.detected_category,
                confidence=round(max(0.25, payload.top_confidence - 0.21), 3),
            ),
        ]
        chosen = payload.selected_hypothesis_sku
        reward = 15 if (chosen and current_user.trust_score >= 70.0 and wallet["daily_minted"] + 15 <= 200) else 0
        wallet["available"] += reward
        wallet["daily_minted"] += reward
        return ScannerDecisionResponse(
            decision_band="TOP3_HYPOTHESES",
            confidence=payload.top_confidence,
            auto_filled_sku=chosen,
            badge="Identificado por IA (Desambiguacao Assistida)" if chosen else "Aguardando Escolha Top-3",
            coins_awarded=reward,
            candidates=top3,
            sent_to_curation_queue=False,
        )

    # Red Band: < 0.50 -> Manual fallback + Curation Queue + 0 coins (STY017-RN04)
    return ScannerDecisionResponse(
        decision_band="MANUAL_CURATION",
        confidence=payload.top_confidence,
        auto_filled_sku=None,
        badge="Preenchimento Manual",
        coins_awarded=0,
        candidates=[],
        sent_to_curation_queue=True,
    )


@router.post(
    "/scanner/desafios/{challenge_id}/votar",
    response_model=CommunityChallengeVoteResponse,
    summary="Vota em desafio de rotulagem comunitaria com consenso de 5 votos (RF-16 / ADR-10 / ADR-12)",
)
async def votar_desafio_scanner(
    challenge_id: str,
    payload: CommunityChallengeVoteRequest,
    current_user: AuthenticatedUserPayload = Depends(get_current_user),
) -> CommunityChallengeVoteResponse:
    _enforce_eligibility(current_user)

    with _GLOBAL_LOCK:
        if challenge_id not in CHALLENGES_STORE:
            CHALLENGES_STORE[challenge_id] = {
                "id": challenge_id,
                "options": [payload.chosen_sku],
                "votes": {},
                "resolved_sku": None,
            }
        chal = CHALLENGES_STORE[challenge_id]
        chal["votes"][current_user.user_id] = payload.chosen_sku

        total_votes = len(chal["votes"])
        counts = Counter(chal["votes"].values())
        top_sku, top_count = counts.most_common(1)[0]
        agreement_ratio = round(top_count / total_votes, 2)

        # Consensus Rule: 5 distinct votes with >= 80% (4/5) agreement
        consensus_reached = total_votes >= 5 and agreement_ratio >= 0.80
        if consensus_reached:
            chal["resolved_sku"] = top_sku

        wallet = _get_or_init_wallet(current_user.user_id)
        reward = 0
        if wallet["daily_minted"] + 5 <= 200:
            reward = 5
            wallet["available"] += reward
            wallet["daily_minted"] += reward

        return CommunityChallengeVoteResponse(
            challenge_id=challenge_id,
            voter_id=current_user.user_id,
            chosen_sku=payload.chosen_sku,
            total_votes=total_votes,
            required_votes=5,
            consensus_reached=consensus_reached,
            winning_sku=chal["resolved_sku"],
            agreement_ratio=agreement_ratio,
            coins_rewarded=reward,
            wallet_available_balance=wallet["available"],
        )
