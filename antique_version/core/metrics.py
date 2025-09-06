"""
metrics.py — Performance and risk metrics for backtesting results.

Responsibilities:
- Compute Sharpe ratio (risk-adjusted return).
- Compute maximum drawdown.
- Compute CAGR (Compound Annual Growth Rate).
- Provide utility functions to summarize portfolio performance.
"""

import numpy as np
import pandas as pd


def compute_returns(equity_curve: pd.Series) -> pd.Series:
    """
    Compute percentage returns from equity curve.

    Args:
        equity_curve: pd.Series of portfolio equity indexed by datetime.

    Returns:
        pd.Series of returns.
    """
    returns = equity_curve.pct_change().dropna()
    return returns


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """
    Calculate annualized Sharpe ratio.

    Args:
        returns: pd.Series of periodic returns.
        risk_free_rate: Risk-free rate per year (e.g. 0.02 for 2%).
        periods_per_year: Number of periods per year (252 for daily, ~390 for intraday minutes).

    Returns:
        Sharpe ratio value.
    """
    excess_returns = returns - (risk_free_rate / periods_per_year)
    mean = excess_returns.mean()
    std = excess_returns.std()

    if std == 0:
        return 0.0

    sharpe = (mean / std) * np.sqrt(periods_per_year)
    return sharpe


def max_drawdown(equity_curve: pd.Series) -> float:
    """
    Compute maximum drawdown.

    Args:
        equity_curve: pd.Series of portfolio equity.

    Returns:
        Maximum drawdown (as negative percentage).
    """
    rolling_max = equity_curve.cummax()
    drawdown = equity_curve / rolling_max - 1.0
    return drawdown.min()


def cagr(equity_curve: pd.Series, periods_per_year: int = 252) -> float:
    """
    Compute Compound Annual Growth Rate (CAGR).

    Args:
        equity_curve: pd.Series of portfolio equity.
        periods_per_year: Number of periods per year.

    Returns:
        CAGR value.
    """
    start_value = equity_curve.iloc[0]
    end_value = equity_curve.iloc[-1]
    n_periods = len(equity_curve)

    years = n_periods / periods_per_year
    if years <= 0:
        return 0.0

    return (end_value / start_value) ** (1 / years) - 1


def summarize_performance(equity_curve: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> dict:
    """
    Generate summary of key performance metrics.

    Args:
        equity_curve: pd.Series of portfolio equity.
        risk_free_rate: Annual risk-free rate.
        periods_per_year: Periods per year for annualization.

    Returns:
        Dict with Sharpe, MDD, CAGR, total return.
    """
    returns = compute_returns(equity_curve)
    sharpe = sharpe_ratio(returns, risk_free_rate, periods_per_year)
    mdd = max_drawdown(equity_curve)
    growth = cagr(equity_curve, periods_per_year)
    total_return = equity_curve.iloc[-1] / equity_curve.iloc[0] - 1

    return {
        "Sharpe Ratio": sharpe,
        "Max Drawdown": mdd,
        "CAGR": growth,
        "Total Return": total_return,
    }
