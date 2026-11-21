"""
API v1 Main Router Aggregation
Conforms to: ADR-03, ADR-06, ADR-08, ADR-09, ADR-13, ADR-16, ADR-17, ADR-22
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    daas,
    disputas,
    escrow,
    esg,
    health,
    leiloes,
    lgpd,
    ofertas,
    ong,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health & Diagnostics"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Profile"])
api_router.include_router(ofertas.router, prefix="/ofertas", tags=["Marketplace Listings"])
api_router.include_router(leiloes.router, prefix="/leiloes", tags=["Auctions, Anti-Sniping & Scanner Consensus"])
api_router.include_router(escrow.router, prefix="/escrow", tags=["Escrow & Financial Custody"])
api_router.include_router(disputas.router, prefix="/disputas", tags=["Warranty, Disputes & Arbitration"])
api_router.include_router(esg.router, prefix="/esg", tags=["ESG & Sustainability Metrics"])
api_router.include_router(ong.router, prefix="/ong", tags=["NGO Donations & Ecopoints"])
api_router.include_router(daas.router, prefix="/daas", tags=["Data as a Service (DaaS)"])
api_router.include_router(lgpd.router, prefix="/lgpd", tags=["LGPD & Data Privacy"])
