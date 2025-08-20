"""
portfolio.py — Portfolio management for backtesting/paper trading.

Responsibilities:
- Manage account capital and open/closed trades.
- Handle execution of new trades with risk controls (position sizing).
- Update PnL based on active trades and prices.
- Provide portfolio equity (balance + unrealized PnL).
"""

from __future__ import annotations
from typing import List, Dict, Optional
from core.trade import Trade
import datetime as dt


class Portfolio:
    """
    Portfolio of trades and account balance.

    Attributes:
        initial_capital: Starting balance.
        cash: Current available balance.
        trades_open: Dictionary of active trades keyed by trade_id.
        trades_closed: List of closed trades.
    """

    def __init__(self, initial_capital: float = 100000.0):
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
    ) -> Trade:
        """
        Open a new trade, deduct margin/cost from cash.

        Args:
            symbol: Ticker of instrument.
            direction: "long" or "short".
            entry_price: Price at entry.
            size: Units to trade.
            stop_loss: Stop-loss price.
            take_profit: Take-profit price.
            time: Timestamp of entry.

        Returns:
            The created Trade instance.
        """
        trade = Trade(
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            entry_time=time or dt.datetime.utcnow(),
        )

        # Deduct used capital (notional exposure simplified)
        cost = entry_price * size
        self.cash -= cost

        self.trades_open[trade.trade_id] = trade
        return trade

    def update_market(self, symbol: str, price: float, time: dt.datetime) -> None:
        """
        Update portfolio with latest price of a symbol.
        This checks SL/TP triggers and closes trades if needed.

        Args:
            symbol: Instrument ticker.
            price: Current market price.
            time: Current timestamp.
        """
        for trade_id, trade in list(self.trades_open.items()):
            if trade.symbol == symbol:
                closed = trade.check_exit(price, time)
                if closed:
                    self._settle_trade(trade)

    def close_trade(self, trade_id: str, price: float, time: Optional[dt.datetime] = None) -> None:
        """
        Force close a trade at a given price.

        Args:
            trade_id: ID of the trade to close.
            price: Exit price.
            time: Exit timestamp (default = now).
        """
        if trade_id in self.trades_open:
            trade = self.trades_open[trade_id]
            trade.close(price, time)
            self._settle_trade(trade)

    def _settle_trade(self, trade: Trade) -> None:
        """
        Finalize a closed trade: add PnL back to cash, move trade to closed list.
        """
        if trade.status != "closed":
            return

        # Return notional cost + PnL
        cost = trade.entry_price * trade.size
        self.cash += cost + trade.pnl

        self.trades_closed.append(trade)
        del self.trades_open[trade.trade_id]

    def equity(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio equity = cash + sum of unrealized PnL.

        Args:
            current_prices: Dict {symbol: current_price}

        Returns:
            Portfolio equity value.
        """
        equity = self.cash
        for trade in self.trades_open.values():
            if trade.symbol in current_prices:
                equity += trade.unrealized_pnl(current_prices[trade.symbol])
        return equity

    def summary(self) -> Dict[str, float]:
        """
        Portfolio snapshot: balances and trade counts.

        Returns:
            Dict with basic portfolio info.
        """
        return {
            "initial_capital": self.initial_capital,
            "cash": self.cash,
            "open_trades": len(self.trades_open),
            "closed_trades": len(self.trades_closed),
            "realized_pnl": sum(t.pnl for t in self.trades_closed if t.pnl is not None),
        }
