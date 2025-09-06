# core/instruments.py
"""
Instrument model.

Correcciones:
- Mapear 'asset_class' desde settings a 'type' si 'type' no existe.
- Eliminar prints en get_instruments().
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

from config import settings


@dataclass(frozen=True)
class Instrument:
    ticker: str
    type: str
    currency: str
    exchange: str
    description: str

    @classmethod
    def from_dict(cls, ticker: str, meta: Dict[str, Any]) -> "Instrument":
        return cls(
            ticker=ticker,
            type=meta.get("type", meta.get("asset_class", "unknown")),
            currency=meta.get("currency", "USD"),
            exchange=meta.get("exchange", "unknown"),
            description=meta.get("description", ""),
        )


def get_instruments() -> Dict[str, Instrument]:
    instruments: Dict[str, Instrument] = {}
    for symbol, meta in settings.INSTRUMENTS.items():
        instruments[symbol] = Instrument.from_dict(symbol, meta)
    return instruments
