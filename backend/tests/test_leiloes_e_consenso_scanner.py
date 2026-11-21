"""
E2E & Concurrency Tests for SPRINT15_005:
- Auction creation & server clock synchronization (ADR-15)
- Atomic bids with SELECT FOR UPDATE lock, 5-coin BID_HOLD / BID_RELEASE, Idempotency-Key (ADR-10, ADR-14)
- Optimistic version guard last_seen_bid_centavos -> 409 BID_OUTDATED & 409 ALREADY_LEADING (RFC 9457)
- Anti-Sniping 3-minute rule (< 180s extends ends_at by +180s) & Realtime <= 100ms broadcast events
- Scanner AI 3 confidence bands (>= 0.80 Auto L5, 0.50-0.79 Top-3 Hypotheses, < 0.50 Manual) & 5-Vote Consensus (ADR-12)
"""

from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app

client = TestClient(app)


def _headers(user_id: str, kyc: bool = True, trust: float = 95.0, idem_key: str | None = None) -> dict:
    token = create_access_token(
        user_id=user_id,
        email=f"{user_id}@steely.local",
        role="USER",
        kyc_verified=kyc,
        trust_score=trust,
    )
    h = {"Authorization": f"Bearer {token}"}
    if idem_key:
        h["Idempotency-Key"] = idem_key
    return h


def test_auction_lifecycle_bid_hold_release_and_conflict_409():
    # 1. Seller creates auction
    r_create = client.post(
        "/api/v1/leiloes/",
        headers=_headers("seller-01"),
        json={
            "oferta_id": "off-rtx4070-01",
            "titulo": "RTX 4070 Super 12GB Founders",
            "categoria": "gpu",
            "lance_inicial_centavos": 250000,
            "incremento_minimo_centavos": 500,
            "duracao_segundos": 600,
        },
    )
    assert r_create.status_code == 201
    auc = r_create.json()
    auction_id = auc["id"]
    assert auc["valor_vigente_centavos"] == 0
    assert "realtime:auctions:" in auc["realtime_channel"]

    # 2. Bidder A places opening bid (250000 cents) -> holds 5 coins (available: 95, locked: 5)
    r_bid_a = client.post(
        f"/api/v1/leiloes/{auction_id}/lances",
        headers=_headers("bidder-a", idem_key="idem-bid-a1"),
        json={"valor_centavos": 250000, "last_seen_bid_centavos": 0},
    )
    assert r_bid_a.status_code == 201
    bid_a = r_bid_a.json()
    assert bid_a["saldo_disponivel_apos"] == 95
    assert bid_a["saldo_bloqueado_apos"] == 5
    assert bid_a["anti_sniping_extended"] is False
    assert bid_a["realtime_events"][0]["event_name"] == "bid.accepted"
    assert bid_a["realtime_events"][0]["propagation_sla_ms"] <= 100

    # 3. Idempotent replay with same Idempotency-Key returns same bid without double-charging coins
    r_bid_a_replay = client.post(
        f"/api/v1/leiloes/{auction_id}/lances",
        headers=_headers("bidder-a", idem_key="idem-bid-a1"),
        json={"valor_centavos": 250000, "last_seen_bid_centavos": 0},
    )
    assert r_bid_a_replay.status_code == 201
    assert r_bid_a_replay.json()["idempotent_replay"] is True
    assert r_bid_a_replay.json()["bid_id"] == bid_a["bid_id"]

    # 4. Bidder A tries to outbid themselves -> 409 ALREADY_LEADING
    r_self = client.post(
        f"/api/v1/leiloes/{auction_id}/lances",
        headers=_headers("bidder-a", idem_key="idem-bid-a2"),
        json={"valor_centavos": 255000, "last_seen_bid_centavos": 250000},
    )
    assert r_self.status_code == 409
    assert r_self.json()["title"] == "ALREADY_LEADING"

    # 5. Bidder B sends stale last_seen_bid_centavos=0 -> 409 BID_OUTDATED (RFC 9457)
    r_stale = client.post(
        f"/api/v1/leiloes/{auction_id}/lances",
        headers=_headers("bidder-b", idem_key="idem-bid-b-stale"),
        json={"valor_centavos": 255000, "last_seen_bid_centavos": 0},
    )
    assert r_stale.status_code == 409
    assert r_stale.headers["content-type"] == "application/problem+json"
    assert r_stale.json()["title"] == "BID_OUTDATED"

    # 6. Bidder B sends valid bid with last_seen_bid_centavos=250000 -> outbids A and releases A's 5 coins
    r_bid_b = client.post(
        f"/api/v1/leiloes/{auction_id}/lances",
        headers=_headers("bidder-b", idem_key="idem-bid-b1"),
        json={"valor_centavos": 255000, "last_seen_bid_centavos": 250000},
    )
    assert r_bid_b.status_code == 201
    assert r_bid_b.json()["saldo_disponivel_apos"] == 95
    assert r_bid_b.json()["saldo_bloqueado_apos"] == 5


def test_anti_sniping_3_minutes_extension_and_realtime_event():
    # Create auction with 120 seconds left (inside the 180s / 3-min anti-sniping window)
    r_create = client.post(
        "/api/v1/leiloes/",
        headers=_headers("seller-02"),
        json={
            "oferta_id": "off-ryzen-5800x3d",
            "titulo": "Ryzen 7 5800X3D Box",
            "categoria": "cpu",
            "lance_inicial_centavos": 120000,
            "incremento_minimo_centavos": 500,
            "duracao_segundos": 120,
        },
    )
    assert r_create.status_code == 201
    auc = r_create.json()
    auction_id = auc["id"]

    r_bid = client.post(
        f"/api/v1/leiloes/{auction_id}/lances",
        headers=_headers("bidder-snipe", idem_key="idem-snipe-1"),
        json={"valor_centavos": 120000, "last_seen_bid_centavos": 0},
    )
    assert r_bid.status_code == 201
    body = r_bid.json()
    assert body["anti_sniping_extended"] is True
    assert body["prorrogacoes_anti_sniping"] == 1
    event_names = [e["event_name"] for e in body["realtime_events"]]
    assert "bid.accepted" in event_names
    assert "auction.extended" in event_names


def test_kyc_and_trust_score_guards():
    r_no_kyc = client.post(
        "/api/v1/leiloes/",
        headers=_headers("user-no-kyc", kyc=False, trust=90.0),
        json={
            "oferta_id": "off-1",
            "titulo": "Teste KYC",
            "lance_inicial_centavos": 10000,
        },
    )
    assert r_no_kyc.status_code == 403

    r_low_trust = client.post(
        "/api/v1/leiloes/",
        headers=_headers("user-low-trust", kyc=True, trust=65.0),
        json={
            "oferta_id": "off-2",
            "titulo": "Teste Trust Score",
            "lance_inicial_centavos": 10000,
        },
    )
    assert r_low_trust.status_code == 403


def test_scanner_3_confidence_bands_and_5_vote_consensus():
    # 1. Green band (>= 0.80) -> AUTO_L5 + 15 coins
    r_green = client.post(
        "/api/v1/leiloes/scanner/analyze",
        headers=_headers("scanner-user-1"),
        json={"image_hash": "hash_green_001", "top_confidence": 0.92, "detected_sku": "RTX-3060-12GB"},
    )
    assert r_green.status_code == 200
    assert r_green.json()["decision_band"] == "AUTO_L5"
    assert r_green.json()["coins_awarded"] == 15

    # 2. Yellow band (0.50..0.79) -> TOP3_HYPOTHESES with 3 candidates
    r_yellow = client.post(
        "/api/v1/leiloes/scanner/analyze",
        headers=_headers("scanner-user-1"),
        json={
            "image_hash": "hash_yellow_002",
            "top_confidence": 0.68,
            "detected_sku": "RTX-3060",
            "selected_hypothesis_sku": "RTX-3060-TI",
        },
    )
    assert r_yellow.status_code == 200
    assert r_yellow.json()["decision_band"] == "TOP3_HYPOTHESES"
    assert len(r_yellow.json()["candidates"]) == 3
    assert r_yellow.json()["coins_awarded"] == 15

    # 3. Red band (< 0.50) -> MANUAL_CURATION + 0 coins + sent_to_curation_queue
    r_red = client.post(
        "/api/v1/leiloes/scanner/analyze",
        headers=_headers("scanner-user-1"),
        json={"image_hash": "hash_red_003", "top_confidence": 0.34},
    )
    assert r_red.status_code == 200
    assert r_red.json()["decision_band"] == "MANUAL_CURATION"
    assert r_red.json()["coins_awarded"] == 0
    assert r_red.json()["sent_to_curation_queue"] is True

    # 4. 5-Vote Community Consensus Challenge (4 agree on ZOTAC-RTX-3060-12GB, 1 disagrees -> 80% consensus!)
    votes = [
        ("voter-1", "ZOTAC-RTX-3060-12GB"),
        ("voter-2", "ZOTAC-RTX-3060-12GB"),
        ("voter-3", "ZOTAC-RTX-3060-TI-8GB"),
        ("voter-4", "ZOTAC-RTX-3060-12GB"),
        ("voter-5", "ZOTAC-RTX-3060-12GB"),
    ]
    last_resp = None
    for uid, sku in votes:
        r_vote = client.post(
            "/api/v1/leiloes/scanner/desafios/chal-consensus-5v/votar",
            headers=_headers(uid),
            json={"chosen_sku": sku},
        )
        assert r_vote.status_code == 200
        last_resp = r_vote.json()

    assert last_resp["total_votes"] == 5
    assert last_resp["consensus_reached"] is True
    assert last_resp["winning_sku"] == "ZOTAC-RTX-3060-12GB"
    assert last_resp["agreement_ratio"] == 0.80
    assert last_resp["coins_rewarded"] == 5
