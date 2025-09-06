# main.py
"""
Ejecuta un backtest de SMA Crossover sobre un solo instrumento.
Parámetros solicitados:
- Capital inicial: 10,000 USD
- Máximo 500 USD por operación
- Stop-loss: 2%
- Take-profit: 4%
Guarda resultados (equity y trades) en /reports.
"""

from config import settings
from datafeed.loader import DataLoader
from strategies.sma_crossover import SMACrossoverStrategy
from backtest.engine import BacktestEngine
import pandas as pd

# Instrumento a probar (puedes cambiarlo si quieres otro del universo)
INSTRUMENT = "SPY"

INITIAL_CAPITAL = 10_000.0
CASH_PER_TRADE = 500.0
STOP_LOSS_PCT = 0.02
TAKE_PROFIT_PCT = 0.04

def main():
    # 1) Datos
    loader = DataLoader()
    data = loader.get(
        INSTRUMENT,
        interval=settings.DEFAULT_INTERVAL,
        period=settings.DEFAULT_PERIOD,
        use_cache=False
    )

    # 2) Estrategia
    strategy = SMACrossoverStrategy(instrument=INSTRUMENT, short_window=10, long_window=50)

    # 3) Motor y ejecución
    engine = BacktestEngine(strategy=strategy, initial_capital=INITIAL_CAPITAL)
    engine.run(
        data,
        cash_per_trade=CASH_PER_TRADE,
        stop_loss=STOP_LOSS_PCT,
        take_profit=TAKE_PROFIT_PCT,
    )

    # 4) Resultados
    print("Resumen de Portafolio:", engine.portfolio.summary())
    print("Métricas:", engine.get_performance())

    # Guardar equity curve
    equity_curve = engine.equity_curve
    settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    equity_curve.to_csv(settings.REPORTS_DIR / "equity_curve.csv")

    # Guardar trades cerrados
    trades_data = []
    for t in engine.portfolio.trades_closed:
        trades_data.append(
            {
                "symbol": t.ticker,
                "direction": t.direction,
                "entry_time": t.entry_time,
                "entry_price": t.entry_price,
                "exit_time": t.exit_time,
                "exit_price": t.exit_price,
                "size": t.size,
                "pnl": t.pnl,
            }
        )
    pd.DataFrame(trades_data).to_csv(settings.REPORTS_DIR / "trades.csv", index=False)
    print(f"Archivos guardados en: {settings.REPORTS_DIR}")

if __name__ == "__main__":
    main()
