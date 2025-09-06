# visualization/plots.py
"""
Genera y guarda:
1) Precio con entradas/salidas
2) Curva de equity
Salida: PNGs en /visualization
"""

from config import settings
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PRICE_PNG = settings.VIS_DIR / "price_chart.png"
EQUITY_PNG = settings.VIS_DIR / "equity_curve.png"

def main():
    settings.VIS_DIR.mkdir(parents=True, exist_ok=True)

    trades_path = settings.REPORTS_DIR / "trades.csv"
    equity_path = settings.REPORTS_DIR / "equity_curve.csv"

    trades_df = pd.read_csv(trades_path, parse_dates=["entry_time", "exit_time"]) if trades_path.exists() else pd.DataFrame()
    equity_df = pd.read_csv(equity_path, index_col=0, parse_dates=True) if equity_path.exists() else pd.DataFrame()

    # Símbolo
    symbol = trades_df.loc[0, "symbol"] if not trades_df.empty else list(settings.INSTRUMENTS.keys())[0]

    # Cargar precios con índice 'timestamp'
    price_csv = settings.path_for_raw_csv(symbol, settings.DEFAULT_INTERVAL)
    price_df = pd.read_csv(price_csv, parse_dates=["timestamp"], index_col="timestamp")
    price = price_df["close"]

    sns.set_style("darkgrid")

    # 1) Precio con entradas/salidas
    fig1, ax1 = plt.subplots(figsize=(11, 6))
    ax1.plot(price.index, price.values, label=f"{symbol} close")

    if not trades_df.empty:
        long_trades = trades_df[trades_df["direction"] == "long"]
        short_trades = trades_df[trades_df["direction"] == "short"]

        if not long_trades.empty:
            ax1.scatter(long_trades["entry_time"], long_trades["entry_price"], marker="^", s=60, color="green", label="Entrada long")
            ax1.scatter(long_trades["exit_time"], long_trades["exit_price"], marker="v", s=60, color="red", label="Salida long")
        if not short_trades.empty:
            ax1.scatter(short_trades["entry_time"], short_trades["entry_price"], marker="^", s=60, color="red", label="Entrada short")
            ax1.scatter(short_trades["exit_time"], short_trades["exit_price"], marker="v", s=60, color="green", label="Salida short")

    ax1.set_title(f"{symbol} — Precio con entradas/salidas")
    ax1.set_xlabel("Fecha")
    ax1.set_ylabel("Precio")
    ax1.legend()
    fig1.tight_layout()
    fig1.savefig(PRICE_PNG)
    print(f"Guardado: {PRICE_PNG}")

    # 2) Curva de equity
    if not equity_df.empty:
        equity_curve = equity_df.iloc[:, 0]
        fig2, ax2 = plt.subplots(figsize=(11, 6))
        ax2.plot(equity_curve.index, equity_curve.values, label="Equity")
        ax2.set_title("Curva de Equity")
        ax2.set_xlabel("Fecha")
        ax2.set_ylabel("USD")
        ax2.legend()
        fig2.tight_layout()
        fig2.savefig(EQUITY_PNG)
        print(f"Guardado: {EQUITY_PNG}")
    else:
        print("No se encontró equity_curve.csv; ejecuta main.py primero.")

if __name__ == "__main__":
    main()
