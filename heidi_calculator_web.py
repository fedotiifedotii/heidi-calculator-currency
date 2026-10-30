#!/usr/bin/env python3
"""
Хайди • Веб-калькулятор + Конвертер валют и крипты
Streamlit-версия
"""

import streamlit as st
import requests
from datetime import datetime

# ==================== НАСТРОЙКИ ====================
CURRENCIES = {
    "USD": "🇺🇸 Доллар США",
    "EUR": "🇪🇺 Евро",
    "RUB": "🇷🇺 Рубль",
    "CNY": "🇨🇳 Юань",
    "GBP": "🇬🇧 Фунт",
    "JPY": "🇯🇵 Иена",
    "KZT": "🇰🇿 Тенге",
    "UAH": "🇺🇦 Гривна",
    "BTC": "₿ Bitcoin",
    "ETH": "Ξ Ethereum",
    "USDT": "₮ Tether",
    "BNB": "🟡 BNB",
    "SOL": "◎ Solana",
    "XRP": "✕ XRP",
    "TON": "💎 TON",
    "DOGE": "🐶 Dogecoin",
}

CRYPTO = {"BTC", "ETH", "USDT", "BNB", "SOL", "XRP", "TON", "DOGE"}


@st.cache_data(ttl=60)
def get_rates():
    """Получить живые курсы (кэш 60 сек)"""
    rates = {"USD": 1.0}
    try:
        # Фиат
        r = requests.get("https://api.frankfurter.dev/v1/latest?from=USD", timeout=8)
        rates.update(r.json().get("rates", {}))

        # Крипта + RUB и др. через Coinbase
        r2 = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=USD", timeout=8)
        cb = r2.json().get("data", {}).get("rates", {})
        for symbol in list(CRYPTO) + ["RUB", "KZT", "UAH", "CNY"]:
            if symbol in cb:
                rates[symbol] = float(cb[symbol])
    except Exception as e:
        st.warning(f"Не удалось обновить курсы: {e}")
    return rates


def convert(amount, from_cur, to_cur, rates):
    if from_cur == to_cur:
        return amount
    if from_cur not in rates or to_cur not in rates:
        raise ValueError("Неизвестная валюта")
    amount_usd = amount / rates[from_cur] if from_cur != "USD" else amount
    return amount_usd * rates[to_cur] if to_cur != "USD" else amount_usd


# ==================== UI ====================
st.set_page_config(
    page_title="Хайди Калькулятор",
    page_icon="✨",
    layout="centered",
)

st.markdown("""
<style>
    .stApp { background-color: #1e1e2e; color: #cdd6f4; }
    h1, h2, h3 { color: #cba6f7 !important; }
    .result-box {
        background: #313244;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.3rem;
        color: #a6e3a1;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ Хайди Калькулятор")
st.caption("Калькулятор + живой конвертер валют и крипты")

tab1, tab2 = st.tabs(["🧮 Калькулятор", "💱 Конвертер"])

# ---------- КАЛЬКУЛЯТОР ----------
with tab1:
    if "expr" not in st.session_state:
        st.session_state.expr = ""
    if "display" not in st.session_state:
        st.session_state.display = "0"

    st.text_input("Выражение", value=st.session_state.display, disabled=True, key="disp")

    buttons = [
        ["C", "⌫", "%", "÷"],
        ["7", "8", "9", "×"],
        ["4", "5", "6", "−"],
        ["1", "2", "3", "+"],
        ["±", "0", ".", "="],
    ]

    for row in buttons:
        cols = st.columns(4)
        for i, btn in enumerate(row):
            if cols[i].button(btn, use_container_width=True, key=f"btn_{btn}_{i}"):
                if btn == "C":
                    st.session_state.expr = ""
                    st.session_state.display = "0"
                elif btn == "⌫":
                    st.session_state.expr = st.session_state.expr[:-1]
                    st.session_state.display = st.session_state.expr or "0"
                elif btn == "=":
                    try:
                        e = st.session_state.expr.replace("×", "*").replace("÷", "/").replace("−", "-")
                        result = eval(e)
                        st.session_state.display = str(round(result, 10)).rstrip("0").rstrip(".") if isinstance(result, float) else str(result)
                        st.session_state.expr = st.session_state.display
                    except:
                        st.session_state.display = "Ошибка"
                        st.session_state.expr = ""
                elif btn == "±":
                    if st.session_state.expr.startswith("-"):
                        st.session_state.expr = st.session_state.expr[1:]
                    else:
                        st.session_state.expr = "-" + st.session_state.expr
                    st.session_state.display = st.session_state.expr or "0"
                elif btn == "%":
                    try:
                        val = float(st.session_state.expr) / 100
                        st.session_state.expr = str(val)
                        st.session_state.display = st.session_state.expr
                    except:
                        pass
                else:
                    if st.session_state.display == "0" and btn not in ".÷×−+":
                        st.session_state.expr = btn
                    else:
                        st.session_state.expr += btn
                    st.session_state.display = st.session_state.expr
                st.rerun()

# ---------- КОНВЕРТЕР ----------
with tab2:
    rates = get_rates()

    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Сумма", min_value=0.0, value=100.0, step=1.0, format="%.8f")
    with col2:
        st.write("")  # spacer

    c1, c2 = st.columns(2)
    with c1:
        from_cur = st.selectbox("Из", options=list(CURRENCIES.keys()), format_func=lambda x: f"{x} — {CURRENCIES[x]}", index=0)
    with c2:
        to_cur = st.selectbox("В", options=list(CURRENCIES.keys()), format_func=lambda x: f"{x} — {CURRENCIES[x]}", index=2)

    if st.button("🔄 Конвертировать", use_container_width=True, type="primary"):
        try:
            result = convert(amount, from_cur, to_cur, rates)
            if to_cur in CRYPTO:
                formatted = f"{result:.8f}".rstrip("0").rstrip(".")
            else:
                formatted = f"{result:,.2f}".replace(",", " ")

            st.markdown(f"""
            <div class="result-box">
                <b>{amount} {from_cur}</b> → <b>{formatted} {to_cur}</b><br>
                <small>{CURRENCIES[from_cur]} → {CURRENCIES[to_cur]}</small>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(str(e))

    st.caption(f"Курсы обновляются раз в минуту • {datetime.now().strftime('%H:%M:%S')}")

st.markdown("---")
st.caption("Сделано с любовью Хайди 💜")
