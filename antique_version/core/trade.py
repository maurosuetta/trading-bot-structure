"""
trade.py — Trade record and execution simulation.

Responsibilities:
- Represent a single trade (long/short).
- Track entry/exit prices, size, PnL, stop-loss, take-profit.
- Allow closing of trades and updating status.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import uuid
import datetime as dt


@dataclass
class Trade:
    """
    A trade record for backtesting or paper trading.

    Attributes:
        trade_id: Unique identifier for the trade.
        ticker: Instrument ticker (e.g. "SPY", "TSLA").
        direction: "long" or "short".
        entry_price: Price at which the position is opened.
        size: Number of units/contracts/shares.
        stop_loss: Stop-loss level (absolute price).
        take_profit: Take-profit level (absolute price).
        entry_time: Timestamp of entry.
        exit_price: Price at which the trade was closed.
        exit_time: Timestamp of exit.
        status: "open" or "closed".
    """
    ticker: str
    direction: str
    entry_price: float
    size: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    entry_time: dt.datetime = field(default_factory=dt.datetime.utcnow)

    # System generated fields
    trade_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    exit_price: Optional[float] = None
    exit_time: Optional[dt.datetime] = None
    status: str = "open"
    pnl: Optional[float] = None  # Profit and loss in currency

    def check_exit(self, current_price: float, current_time: dt.datetime) -> bool:
        """
        Check if SL/TP is hit, and close the trade if so.

        Args:
            current_price: Latest price.
            current_time: Timestamp.

        Returns:
            True if trade was closed, False otherwise.
        """
        if self.status == "closed":
            return False

        # Stop-loss logic
        if self.stop_loss is not None:
            if self.direction == "long" and current_price <= self.stop_loss:
                self.close(current_price, current_time)
                return True
            if self.direction == "short" and current_price >= self.stop_loss:
                self.close(current_price, current_time)
                return True

        # Take-profit logic
        if self.take_profit is not None:
            if self.direction == "long" and current_price >= self.take_profit:
                self.close(current_price, current_time)
                return True
            if self.direction == "short" and current_price <= self.take_profit:
                self.close(current_price, current_time)
                return True

        return False

    def close(self, price: float, time: Optional[dt.datetime] = None) -> None:
        """
        Close the trade at a given price.

        Args:
            price: Exit price.
            time: Exit time (defaults to now).
        """
        if self.status == "closed":
            return

        self.exit_price = price
        self.exit_time = time or dt.datetime.utcnow()
        self.status = "closed"

        # Calculate PnL
        if self.direction == "long":    
            self.pnl = (self.exit_price - self.entry_price) * self.size
        elif self.direction == "short":
            self.pnl = (self.entry_price - self.exit_price) * self.size
        else:
            raise ValueError("Invalid direction: must be 'long' or 'short'")

    def unrealized_pnl(self, current_price: float) -> float:
        """
        Calculate unrealized PnL (if trade is still open).

        Args:
            current_price: Current market price.

        Returns:
            Unrealized PnL in currency.
        """
        if self.status == "closed":
            return 0.0

        if self.direction == "long":
            return (current_price - self.entry_price) * self.size
        elif self.direction == "short":
            return (self.entry_price - current_price) * self.size
        else:
            raise ValueError("Invalid direction: must be 'long' or 'short'")
