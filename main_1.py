import yfinance as yf
import pandas as pd

# 1. Define el ticker (símbolo del activo) y el rango de fechas.
ticker = "GOOGL"
start_date = "2023-01-01"
end_date = "2024-01-01"

# 2. Descarga los datos históricos.
# El método yf.download() devuelve un DataFrame de pandas con los datos OHLCV.
# 'interval' es opcional y por defecto es diario ('1d'). Puedes cambiarlo a '1h' (por hora), '1m' (por minuto), etc.
data = yf.download(ticker, start=start_date, end=end_date)
data.to_csv(f"{ticker}-({start_date}to{end_date}).csv")
# 3. Muestra los primeros 5 registros del DataFrame.
print("Datos descargados:")
print(data.head())

# 4. Puedes acceder a columnas específicas.
cierre_ajustado = data['Adj Close']
print("\nPrimeros 5 precios de cierre ajustado:")
print(cierre_ajustado.head())