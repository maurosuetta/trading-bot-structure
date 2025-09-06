# core/portfolio.py
"""
Portfolio con gestión de caja y trades abiertos/cerrados.

Correcciones:
- Usar 'ticker' (coincide con Trade) en vez de 'symbol' para acceder a atributos.
- Al abrir trades, respetar la caja disponible (si el coste excede, ajustar tamaño).
"""

from __future__ import annotations
from typing import List, Dict, Optional
from core.trade import Trade
import datetime as dt


class Portfolio:
    def __init__(self, initial_capital: float = 10_000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.trades_open: Dict[str, Trade] = {}
        self.trades_closed: List[Trade] = []

    def open_trade(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        size: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        time: Optional[dt.datetime] = None,
    ) -> Optional[Trade]:
        # Ajuste por caja disponible
        cost = entry_price * size
        if cost > self.cash and entry_price > 0:
            size = self.cash / entry_price
            cost = entry_price * size
        if cost <= 0:
            return None

        trade = Trade(
            ticker=symbol,
            direction=direction,
            entry_price=entry_price,
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            entry_time=time or dt.datetime.utcnow(),
        )

        self.cash -= cost
        self.trades_open[trade.trade_id] = trade
        return trade

    def update_market(self, symbol: str, price: float, time: dt.datetime) -> None:
        for trade_id, trade in list(self.trades_open.items()):
            if trade.ticker == symbol:
                closed = trade.check_exit(price, time)
                if closed:
                    self._settle_trade(trade)

    def close_trade(self, trade_id: str, price: float, time: Optional[dt.datetime] = None) -> None:
        if trade_id in self.trades_open:
            trade = self.trades_open[trade_id]
            trade.close(price, time)
            self._settle_trade(trade)

    def _settle_trade(self, trade: Trade) -> None:
        if trade.status != "closed":
            return
        cost = trade.entry_price * trade.size
        self.cash += cost + (trade.pnl or 0.0)
        self.trades_closed.append(trade)
        del self.trades_open[trade.trade_id]

    def equity(self, current_prices: Dict[str, float]) -> float:
        equity = self.cash
        for trade in self.trades_open.values():
            if trade.ticker in current_prices:
                equity += trade.unrealized_pnl(current_prices[trade.ticker])
        return equity

    def summary(self) -> Dict[str, float]:
        return {
            "initial_capital": self.initial_capital,
            "cash": self.cash,
            "open_trades": len(self.trades_open),
            "closed_trades": len(self.trades_closed),
            "realized_pnl": sum(t.pnl for t in self.trades_closed if t.pnl is not None),
        }
