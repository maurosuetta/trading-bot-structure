# backtest/engine.py
"""
Backtesting engine para ejecutar estrategias sobre datos históricos.

Correcciones clave:
- Usa columna 'close' (minúsculas) para alinearse con DataLoader.
- Cierre de posición opuesta cuando aparece señal contraria.
- stop_loss y take_profit como PORCENTAJES relativos al precio de entrada.
- cash_per_trade: limita el nominal por operación (p.ej., 500 USD).
"""

from typing import Dict, Optional
import pandas as pd
import datetime as dt

from core.portfolio import Portfolio
from strategies.base import Strategy
from core.metrics import summarize_performance


class BacktestEngine:
    def __init__(self, strategy: Strategy, initial_capital: float = 10_000.0):
        self.strategy = strategy
        self.portfolio = Portfolio(initial_capital=initial_capital)
        self.equity_curve: pd.Series = pd.Series(dtype=float)

    def run(
        self,
        data: pd.DataFrame,
        cash_per_trade: float = 500.0,
        stop_loss: Optional[float] = 0.02,     # porcentaje (2% = 0.02)
        take_profit: Optional[float] = 0.04,   # porcentaje (4% = 0.04)
    ):
        """
        Args:
            data: DataFrame con columna 'close' e índice datetime (UTC).
            cash_per_trade: Máximo nominal por trade en moneda.
            stop_loss: Porcentaje de SL respecto al precio de entrada (None para desactivar).
            take_profit: Porcentaje de TP respecto al precio de entrada (None para desactivar).
        """
        # Generar señales
        signals = self.strategy.generate_signals(data)

        # Historia de equity
        equity_history = []

        for timestamp, signal in signals.items():
            price = float(data.loc[timestamp, "close"])

            # 1) Actualizar SL/TP en posiciones abiertas
            self.portfolio.update_market(self.strategy.instrument, price, timestamp)

            # Estado actual por instrumento
            directions = {
                t.direction
                for t in self.portfolio.trades_open.values()
                if t.ticker == self.strategy.instrument
            }
            has_long = "long" in directions
            has_short = "short" in directions

            # 2) Gestión de señales: cerrar opuesto y abrir nueva si procede
            if signal == 1:
                # Cerrar cortos abiertos
                if has_short:
                    for t_id, t in list(self.portfolio.trades_open.items()):
                        if t.ticker == self.strategy.instrument and t.direction == "short":
                            self.portfolio.close_trade(t_id, price, timestamp)
                # Abrir largo si no existe
                if not has_long:
                    # Calcular tamaño desde cash_per_trade y caja disponible
                    alloc_cash = min(cash_per_trade, self.portfolio.cash)
                    if alloc_cash > 0:
                        size = alloc_cash / price
                        sl = price * (1 - stop_loss) if stop_loss is not None else None
                        tp = price * (1 + take_profit) if take_profit is not None else None
                        self.portfolio.open_trade(
                            symbol=self.strategy.instrument,
                            direction="long",
                            entry_price=price,
                            size=size,
                            stop_loss=sl,
                            take_profit=tp,
                            time=timestamp,
                        )

            elif signal == -1:
                # Cerrar largos abiertos
                if has_long:
                    for t_id, t in list(self.portfolio.trades_open.items()):
                        if t.ticker == self.strategy.instrument and t.direction == "long":
                            self.portfolio.close_trade(t_id, price, timestamp)
                # Abrir corto si no existe
                if not has_short:
                    alloc_cash = min(cash_per_trade, self.portfolio.cash)
                    if alloc_cash > 0:
                        size = alloc_cash / price
                        sl = price * (1 + stop_loss) if stop_loss is not None else None
                        tp = price * (1 - take_profit) if take_profit is not None else None
                        self.portfolio.open_trade(
                            symbol=self.strategy.instrument,
                            direction="short",
                            entry_price=price,
                            size=size,
                            stop_loss=sl,
                            take_profit=tp,
                            time=timestamp,
                        )

            # 3) Registrar equity
            current_prices = {self.strategy.instrument: price}
            equity_history.append(self.portfolio.equity(current_prices))

        self.equity_curve = pd.Series(equity_history, index=signals.index)

    def get_performance(self, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> Dict[str, float]:
        return summarize_performance(
            self.equity_curve, risk_free_rate=risk_free_rate, periods_per_year=periods_per_year
        )
