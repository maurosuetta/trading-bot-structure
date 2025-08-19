"""
instruments.py — Instrument metadata model.

Responsibilities:
- Represent a tradable instrument (ETF, stock, crypto, etc.).
- Hold metadata: symbol, type, currency, exchange, description.
- Provide factory method to load instruments from settings.INSTRUMENTS.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

from config import settings


@dataclass(frozen=True)
class Instrument:
    """
    A financial instrument with metadata.
    
    Example:
        spy = Instrument(
            symbol="SPY",
            type="etf",
            currency="USD",
            exchange="NYSE",
            description="SPDR S&P 500 ETF Trust"
        )
    """
    symbol: str
    type: str
    currency: str
    exchange: str
    description: str

    @classmethod
    def from_dict(cls, symbol: str, meta: Dict[str, Any]) -> "Instrument":
        """
        Build an Instrument from a metadata dictionary.

        Args:
            symbol: Ticker symbol.
            meta: Metadata dict with fields like type, currency, exchange, description.

        Returns:
            Instrument object.
        """
        return cls(
            symbol=symbol,
            type=meta.get("type", "unknown"),
            currency=meta.get("currency", "USD"),
            exchange=meta.get("exchange", "unknown"),
            description=meta.get("description", ""),
        )


def get_instruments() -> Dict[str, Instrument]:
    """
    Load all instruments defined in settings.INSTRUMENTS.

    Returns:
        Dictionary mapping symbol -> Instrument.
    """
    instruments: Dict[str, Instrument] = {}
    for symbol, meta in settings.INSTRUMENTS.items():
        instruments[symbol] = Instrument.from_dict(symbol, meta)
    return instruments
