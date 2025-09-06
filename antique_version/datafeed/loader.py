# datafeed/loader.py
"""
DataLoader para yfinance con caché CSV robusta.

Objetivos:
- Guardar índice como 'timestamp' (UTC) y columnas OHLCV planas en minúsculas.
- Al leer la caché, tolerar cabeceras multi-nivel y formatos "raros".
- Si la caché no es fiable, borrar y redescargar.
"""

from __future__ import annotations

import pandas as pd
import yfinance as yf
from pathlib import Path
from typing import Optional, Tuple, List, Union

from config import settings


OHLC_MAP = {
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "adj close": "adj_close",
    "adj_close": "adj_close",
    "adjclose": "adj_close",
    "volume": "volume",
}

def _to_lower_str(x: Union[str, tuple]) -> str:
    """Convierte nombres de columna (incluido MultiIndex) a una clave simple en minúsculas."""
    if isinstance(x, tuple):
        parts: List[str] = [str(p).strip().lower() for p in x if p is not None]
        return "_".join([p for p in parts if p])
    return str(x).strip().lower()


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    - Aplana MultiIndex si existe.
    - Pasa todo a minúsculas.
    - Renombra OHLCV a {'open','high','low','close','adj_close','volume'} si aparecen variantes.
    - Si vienen columnas tipo 'close_spy' o 'spy_close' y es un único ticker, usa 'close'.
    """
    # Aplanar MultiIndex si procede
    if isinstance(df.columns, pd.MultiIndex):
        # Si es un único ticker, típicamente columnas como ('Open','SPY'), etc.
        cols_flat = [_to_lower_str(c) for c in df.columns.to_flat_index()]
        df.columns = cols_flat
    else:
        df.columns = [_to_lower_str(c) for c in df.columns]

    # Intentar mapear nombres a OHLC_MAP
    new_cols = {}
    for c in df.columns:
        # Casos directos: 'open', 'close', etc.
        if c in OHLC_MAP:
            new_cols[c] = OHLC_MAP[c]
            continue
        # Casos 'close_spy', 'spy_close', 'adj close_spy', etc.
        tokens = c.replace("-", "_").split("_")
        # Busca token OHLC en los componentes
        found = None
        for i in range(len(tokens)):
            candidate = " ".join(tokens[i:])  # 'close', 'adj close', etc.
            candidate = candidate.replace("  ", " ").strip()
            if candidate in OHLC_MAP:
                found = OHLC_MAP[candidate]
                break
            # también probar uniendo con '_'
            candidate2 = "_".join(tokens[i:])
            if candidate2 in OHLC_MAP:
                found = OHLC_MAP[candidate2]
                break
        if found:
            new_cols[c] = found
        else:
            # dejarlo como está si no es OHLCV
            new_cols[c] = c

    df = df.rename(columns=new_cols)

    # Si existen múltiples columnas equivalentes (p.ej. 'close' y 'close_spy' mapeadas ambas a 'close'),
    # nos quedamos con la primera y descartamos duplicados.
    df = df.loc[:, ~df.columns.duplicated(keep="first")]

    # Asegurar que, al menos, 'close' exista si hay alguna variante plausible:
    if "close" not in df.columns:
        # intenta localizar alguna columna con 'close' dentro
        candidates = [c for c in df.columns if "close" in c]
        if candidates:
            df = df.rename(columns={candidates[0]: "close"})

    return df


class DataLoader:
    def __init__(self, raw_dir: Optional[Path] = None) -> None:
        self.raw_dir = raw_dir or settings.RAW_DATA_DIR

    def _cache_path(self, symbol: str, interval: str) -> Path:
        safe_symbol = symbol.replace("=", "-").replace("/", "-")
        return Path(self.raw_dir) / f"{safe_symbol}_{interval}.csv"

    def _download_from_yf(self, symbol: str, interval: str, period: str) -> pd.DataFrame:
        df = yf.download(
            tickers=symbol,
            interval=interval,
            period=period,
            auto_adjust=False,
            progress=False,
            prepost=False,
        )
        if df.empty:
            raise ValueError(f"No data returned for {symbol} with {interval}/{period}.")

        # Índice -> UTC con nombre 'timestamp'
        df.index = pd.to_datetime(df.index, utc=True)
        df.index.name = "timestamp"

        # Normalizar columnas
        df = _standardize_columns(df)

        # Si aún así no hay 'close', error explícito
        if "close" not in df.columns:
            raise ValueError(f"Downloaded data missing 'close' column for {symbol}. Columns: {list(df.columns)}")

        return df

    def _try_read_cached_csv(self, path: Path) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Intenta leer CSV en varios formatos:
        - Con índice 'timestamp'
        - Con 2 filas de cabecera (MultiIndex)
        - Primera columna como índice
        Devuelve (df, error). Si df es None, error describe el problema.
        """
        # 1) Formato preferido (guardado por este loader)
        try:
            df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
            df.index = pd.to_datetime(df.index, utc=True)
            df.index.name = "timestamp"
            df = _standardize_columns(df)
            return df, None
        except Exception as e1:
            pass

        # 2) CSV con MultiIndex de columnas (dos filas de cabecera)
        try:
            df = pd.read_csv(path, header=[0, 1])
            # Si hay columna de fecha explícita, recupérala; si no, usar primera col como índice
            # Detectar columna timestamp/date
            date_cols = [c for c in df.columns if isinstance(c, tuple) and _to_lower_str(c[0]) in ("timestamp", "date", "datetime")]
            if date_cols:
                # extraer esa columna como serie de índice
                c0 = date_cols[0]
                idx = pd.to_datetime(df[c0], utc=True, errors="coerce")
                df = df.drop(columns=[c0])
                df.index = idx
            else:
                # fallback: asumir primera columna es fecha
                first_col = df.columns[0]
                idx = pd.to_datetime(df[first_col], utc=True, errors="coerce")
                df = df.drop(columns=[first_col])
                df.index = idx

            df.index.name = "timestamp"
            df = _standardize_columns(df)
            # Filtrar filas con índice NaT
            df = df[~df.index.isna()]
            return df, None
        except Exception as e2:
            pass

        # 3) Primera columna como índice con parse_dates=[0]
        try:
            df = pd.read_csv(path, parse_dates=[0], index_col=0)
            df.index = pd.to_datetime(df.index, utc=True, errors="coerce")
            df.index.name = "timestamp"
            df = df[~df.index.isna()]
            df = _standardize_columns(df)
            return df, None
        except Exception as e3:
            return None, f"Cached CSV not parseable: {e3}"

    def get(
        self,
        symbol: str,
        interval: Optional[str] = None,
        period: Optional[str] = None,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        interval = interval or settings.DEFAULT_INTERVAL
        period = period or settings.yf_max_period_for_interval(interval)
        cache_file = self._cache_path(symbol, interval)

        if use_cache and cache_file.exists():
            df, err = self._try_read_cached_csv(cache_file)
            if df is not None and "close" in df.columns:
                return df
            # Si no se pudo leer o falta 'close', redescargar
            try:
                cache_file.unlink(missing_ok=True)
            except Exception:
                pass

        # Descarga limpia y guardado normalizado
        df = self._download_from_yf(symbol, interval, period)
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache_file, index_label="timestamp")
        return df
