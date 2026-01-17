import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sezonowość akcji", layout="wide")
st.title("Sezonowość akcji – analiza lutego vs stycznia (ostatnie 5 lat)")

# Lista przykładowych 50 spółek NYSE dla szybszego działania w Cloud
tickers = [
    "AAPL","MSFT","GOOG","AMZN","TSLA","NVDA","JPM","JNJ","V","PG",
    "UNH","HD","MA","DIS","BAC","PFE","ADBE","KO","NFLX","XOM",
    "CSCO","INTC","PEP","MRK","CVX","T","ABT","ORCL","NKE","MCD",
    "CRM","WMT","VZ","ACN","LLY","BMY","MDT","COST","IBM","QCOM",
    "TXN","HON","LIN","NEE","PM","UPS","LOW","MMM","SBUX","AMD"
]

if st.button("Uruchom analizę"):
    results = []

    for ticker in tickers:
        try:
            # Pobranie dziennych danych z ostatnich 5 lat
            data = yf.download(ticker, start="2019-01-01", end="2024-01-31", interval="1d", progress=False)
            if data.empty:
                st.warning(f"Brak danych dla {ticker}")
                continue

            yearly_gains = []

            for year in range(2019, 2024):
                try:
                    jan_data = data[(data.index.year == year) & (data.index.month == 1)]
                    feb_data = data[(data.index.year == year) & (data.index.month == 2)]

                    if jan_data.empty or feb_data.empty:
                        continue

                    jan_price = jan_data.loc[jan_data.index >= pd.Timestamp(f"{year}-01-15")]["Adj Close"].iloc[0]
                    feb_price = feb_data.loc[feb_data.index <= pd.Timestamp(f"{year}-02-28")]["Adj Close"].iloc[-1]

                    gain = ((feb_price - jan_price) / jan_price) * 100
                    yearly_gains.append(gain)
                except Exception:
                    continue

            if yearly_gains:
                results.append({
                    "Spółka": ticker,
                    "Średni wzrost (%)": np.mean(yearly_gains),
                    "Min wzrost (%)": np.min(yearly_gains),
                    "Max wzrost (%)": np.max(yearly_gains)
                })
            else:
                st.info(f"Brak pełnych danych dla {ticker}")

        except Exception as e:
            st.error(f"Błąd przy pobieraniu danych dla {ticker}: {e}")

    if results:
        df_res = pd.DataFrame(results)
        df_res = df_res.sort_values("Średni wzrost (%)", ascending=False)
        st.subheader("Wyniki analizy")
        st.dataframe(df_res)

        # Wykres Top 20
        st.subheader("Top 20 spółek wg średniego wzrostu (%)")
        top20 = df_res.head(20)
        fig, ax = plt.subplots(figsize=(12,6))
        ax.bar(top20["Spółka"], top20["Średni wzrost (%)"], color="skyblue")
        ax.set_ylabel("Średni wzrost (%)")
        ax.set_xlabel("Spółka")
        ax.set_xticklabels(top20["Spółka"], rotation=45, ha="right")
        st.pyplot(fig)

    else:
        st.warning("Brak danych do wyświetlenia. Sprawdź tickery lub połączenie z internetem.")
