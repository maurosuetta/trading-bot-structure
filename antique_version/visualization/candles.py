"""
candles.py — Candlestick plotting utilities with indicators and signals.

Responsibilities:
- Plot OHLC candlestick charts.
- Overlay indicators (e.g., moving averages).
- Mark buy/sell signals on the chart.
"""

import mplfinance as mpf
import pandas as pd


def plot_candles_with_indicators(
    data: pd.DataFrame,
    signals: pd.Series = None,
    title: str = "Candlestick Chart",
    mav: list = None,
    save_path: str = None
):
    addplots = []

    # Señales buy/sell
    if signals is not None:
        buy_signals = signals[signals == 1]
        sell_signals = signals[signals == -1]

        if not buy_signals.empty:
            addplots.append(
                mpf.make_addplot(data.loc[buy_signals.index, "Close"],
                                 type='scatter', markersize=100, marker='^', color='g')
            )
        if not sell_signals.empty:
            addplots.append(
                mpf.make_addplot(data.loc[sell_signals.index, "Close"],
                                 type='scatter', markersize=100, marker='v', color='r')
            )

    # Preparar kwargs de mpf.plot
    plot_kwargs = dict(
        type='candle',
        mav=mav,
        volume=True,
        title=title,
        style='yahoo',
        addplot=addplots,
        figratio=(12,6),
        figscale=1.2
    )

    # Solo pasar savefig si save_path no es None
    if save_path is not None:
        plot_kwargs['savefig'] = save_path

    mpf.plot(data, **plot_kwargs)
