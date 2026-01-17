import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sezonowość akcji", layout="wide")
st.title("Sezonowość: luty vs styczeń (ostatnie 5 lat)")

# Ograniczona lista dużych, pewnych tickerów (działają w Yahoo)
TICKERS = [
    "AAPL","MSFT","AMZN","GOOGL","META","NVDA","TSLA",
    "JPM","JNJ","V","PG","UNH","HD","MA","DIS","BAC",
    "XOM","CVX","KO","PEP","WMT","COST","MCD","NKE","SBUX"
]

YEARS = [2019, 2020, 2021, 2022, 2023]

if st.button("Uruchom analizę"):
    results = []

    for ticker in TICKERS:
        try:
            data = yf.download(
                ticker,
                start="2019-01-01",
                end="2024-03-01",
                interval="1d",
                auto_adjust=True,   # 🔑 kluczowe – NIE używamy Adj Close
                progress=False
            )

            if data.empty or "Close" not in data.columns:
                continue

            yearly_gains = []

            for year in YEARS:
                jan = data[(data.index.year == year) & (data.index.month == 1)]
                feb = data[(data.index.year == year) & (data.index.month == 2)]

                if jan.empty or feb.empty:
                    continue

                jan_price = jan["Close"].iloc[0]     # pierwsza sesja stycznia
                feb_price = feb["Close"].iloc[-1]    # ostatnia sesja lutego

                if jan_price > 0:
                    gain = (feb_price - jan_price) / jan_price * 100
                    yearly_gains.append(gain)

            if len(yearly_gains) >= 3:  # minimum sensownych obserwacji
                results.append({
                    "Spółka": ticker,
                    "Średni wzrost (%)": round(np.mean(yearly_gains), 2),
                    "Mediana (%)": round(np.median(yearly_gains), 2),
                    "Min (%)": round(min(yearly_gains), 2),
                    "Max (%)": round(max(yearly_gains), 2),
                    "Liczba lat": len(yearly_gains)
                })

        except Exception as e:
            st.warning(f"Błąd dla {ticker}: {e}")

    if not results:
        st.error("❌ Brak wyników – to NIE powinno się zdarzyć.")
        st.stop()

    df = pd.DataFrame(results).sort_values("Średni wzrost (%)", ascending=False)

    st.subheader("📊 Wyniki")
    st.dataframe(df, use_container_width=True)

    st.subheader("🏆 Top 10 – średni wzrost luty vs styczeń")
    top10 = df.head(10)

    fig, ax = plt.subplots(figsize=(10,5))
    ax.bar(top10["Spółka"], top10["Średni wzrost (%)"])
    ax.set_ylabel("Średni wzrost (%)")
    ax.set_xlabel("Spółka")
    ax.set_title("Sezonowość: luty vs styczeń")
    plt.xticks(rotation=45)
    st.pyplot(fig)
