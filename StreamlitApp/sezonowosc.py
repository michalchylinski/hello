import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sezonowość akcji", layout="wide")
st.title("Sezonowość akcji – analiza lutego vs stycznia")

# ---- Lista przykładowych 100 spółek NYSE ----
# W realnym zastosowaniu można pobrać listę dynamicznie
tickers = [
    "AAPL","MSFT","GOOG","AMZN","TSLA","NVDA","JPM","JNJ","V","PG",
    "UNH","HD","MA","DIS","BAC","PFE","ADBE","KO","NFLX","XOM",
    "CSCO","INTC","PEP","MRK","CVX","T","ABT","ORCL","NKE","MCD",
    "CRM","WMT","VZ","ACN","LLY","BMY","MDT","COST","IBM","QCOM",
    "TXN","HON","LIN","NEE","PM","UPS","LOW","MMM","SBUX","AMD",
    "GE","CAT","BLK","AXP","GS","RTX","AMGN","NOW","INTU","PLD",
    "AMAT","BKNG","ADI","FIS","ISRG","SPGI","SYK","CL","ZTS","REGN",
    "MO","CCI","DE","CSX","TMO","LMT","ANTM","MS","SCHW","BDX",
    "USB","SCHW","EL","ADP","C","APD","ICE","EW","PNC","DUK",
    "SO","VRTX","CTSH","ITW","TFC","COF","CSGP","MCK","ATVI","MAR"
]

if st.button("Uruchom analizę"):
    results = []

    for ticker in tickers:
        try:
            data = yf.download(ticker, period="5y", interval="1mo", progress=False)
            if data.empty:
                st.warning(f"Brak danych dla {ticker}")
                continue

            yearly_gains = []
            min_gains = []
            max_gains = []

            for year in range(2019, 2024):
                jan_date = f"{year}-01-15"
                feb_date = f"{year}-02-28"
                try:
                    jan_price = data.loc[data.index >= jan_date]["Adj Close"].iloc[0]
                    feb_price = data.loc[data.index >= feb_date]["Adj Close"].iloc[0]
                    gain = ((feb_price - jan_price) / jan_price) * 100
                    yearly_gains.append(gain)
                except IndexError:
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
        if "Średni wzrost (%)" in df_res.columns:
            df_res = df_res.sort_values("Średni wzrost (%)", ascending=False)
            st.subheader("Wyniki analizy")
            st.dataframe(df_res)

            # ---- Wykres słupkowy ----
            st.subheader("Top 20 spółek wg średniego wzrostu (%)")
            top20 = df_res.head(20)
            fig, ax = plt.subplots(figsize=(12,6))
            ax.bar(top20["Spółka"], top20["Średni wzrost (%)"], color="skyblue")
            ax.set_ylabel("Średni wzrost (%)")
            ax.set_xlabel("Spółka")
            ax.set_xticklabels(top20["Spółka"], rotation=45, ha="right")
            st.pyplot(fig)
        else:
            st.error("Kolumna 'Średni wzrost (%)' nie istnieje. Analiza nie mogła zostać przeprowadzona.")
    else:
        st.warning("Brak danych do wyświetlenia. Sprawdź tickery lub połączenie z internetem.")
