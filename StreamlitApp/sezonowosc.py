import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sezonowość akcji", layout="wide")

st.title("📈 Analiza sezonowości akcji (klik i działa)")

st.markdown("""
Ta aplikacja szuka **powtarzalnych wzorców sezonowych** w cenach akcji  
(np. styczeń → luty, listopad → grudzień).
""")

# =========================
# PANEL STEROWANIA
# =========================

st.sidebar.header("⚙️ Ustawienia analizy")

years = st.sidebar.slider("Liczba lat analizy", 3, 10, 5)

period_name = st.sidebar.selectbox(
    "Okres sezonowy",
    {
        "Styczeń → Luty": (1, 15, 2, 28),
        "Listopad → Grudzień": (11, 1, 12, 31),
        "Marzec → Maj": (3, 1, 5, 31)
    }.keys()
)

periods = {
    "Styczeń → Luty": (1, 15, 2, 28),
    "Listopad → Grudzień": (11, 1, 12, 31),
    "Marzec → Maj": (3, 1, 5, 31)
}

sector_filter = st.sidebar.selectbox(
    "Sektor",
    ["Wszystkie", "Consumer Cyclical", "Energy", "Healthcare", "Technology", "Financial Services"]
)

# =========================
# DANE
# =========================

@st.cache_data
def load_data(tickers, years):
    data = {}
    for t in tickers:
        df = yf.download(t, period=f"{years+1}y", progress=False)
        if not df.empty:
            data[t] = df
    return data

@st.cache_data
def get_sector(ticker):
    try:
        return yf.Ticker(ticker).info.get("sector")
    except:
        return None

tickers = [
    "WMT","TGT","COST","HD","LOW",
    "XOM","CVX","JNJ","PFE","ABBV",
    "AAPL","MSFT","NVDA","GOOGL",
    "JPM","BAC","GS","V","MA"
]

price_data = load_data(tickers, years)

# =========================
# ANALIZA
# =========================

def closest_price(df, date):
    return df.iloc[(df.index - date).abs().argsort()[:1]]["Close"].values[0]

results = []

if st.button("▶ Uruchom analizę"):
    m1, d1, m2, d2 = periods[period_name]

    for t in tickers:
        df = price_data.get(t)
        if df is None:
            continue

        sector = get_sector(t)
        if sector_filter != "Wszystkie" and sector != sector_filter:
            continue

        returns = []

        for y in range(datetime.now().year - years, datetime.now().year):
            try:
                p1 = closest_price(df, datetime(y, m1, d1))
                p2 = closest_price(df, datetime(y, m2, d2))
                returns.append((p2 - p1) / p1)
            except:
                pass

        if returns:
            results.append({
                "Spółka": t,
                "Sektor": sector,
                "Średni wzrost (%)": round(np.mean(returns)*100, 2),
                "Lata na plusie": sum(r > 0 for r in returns)
            })

    df_res = pd.DataFrame(results).sort_values("Średni wzrost (%)", ascending=False)

    st.subheader("📊 Wyniki")
    st.dataframe(df_res, use_container_width=True)

    st.download_button(
        "⬇ Pobierz wyniki (CSV)",
        df_res.to_csv(index=False),
        "sezonowosc_wyniki.csv"
    )

    # =========================
    # WYKRES
    # =========================

    st.subheader("📈 Wykres sezonowy")

    selected = st.selectbox("Wybierz spółkę do wykresu", df_res["Spółka"])

    df = price_data[selected]
    paths = []

    for y in range(datetime.now().year - years, datetime.now().year):
        try:
            start = datetime(y, m1, d1)
            end = datetime(y, m2, d2)
            segment = df.loc[start:end]["Close"].pct_change().cumsum()
            paths.append(segment.values)
        except:
            pass

    if paths:
        avg = np.nanmean(np.array(paths), axis=0)
        fig, ax = plt.subplots()
        ax.plot(avg)
        ax.set_title(f"{selected} – średnia ścieżka sezonowa")
        ax.set_ylabel("Zmiana %")
        st.pyplot(fig)
