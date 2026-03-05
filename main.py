import streamlit as st
import pandas as pd
from groq import Groq
import requests
import time

# --- الإعدادات ---
st.set_page_config(page_title="AI Sniper Radar V5", layout="wide")
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# العملات (بتنسيق CryptoCompare)
SYMBOLS = ['BTC', 'ETH', 'SOL', 'BNB']

def fetch_price_unblocked(symbol):
    """جلب السعر من مصدر بديل تماماً (CryptoCompare)"""
    try:
        url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD"
        res = requests.get(url, timeout=10)
        data = res.json()
        return data.get('USD')
    except:
        return None

def ask_ai_expert(symbol, price):
    try:
        prompt = f"Crypto: {symbol}, Price: ${price:,.2f}. Should I BUY, SELL, or HOLD? Give confidence % and 1 short reason."
        chat = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return chat.choices[0].message.content
    except:
        return "AI Busy | 0% | Try later"

# --- الواجهة ---
st.title("🎯 رادار القناص (النسخة V5 - محرك CryptoCompare)")
st.write("تم استبدال محرك البيانات بمصدر أكاديمي لتخطي الحجب الشامل.")

if st.button("تحديث يدوي 🔄"):
    st.rerun()

cols = st.columns(2)
for i, sym in enumerate(SYMBOLS):
    with cols[i % 2]:
        st.subheader(f"🪙 {sym}/USD")
        price = fetch_price_unblocked(sym)
        
        if price:
            st.metric("السعر الحالي", f"${price:,.2f}")
            with st.spinner(f'جاري تحليل {sym}...'):
                ans = ask_ai_expert(sym, price)
                
                if "BUY" in ans.upper():
                    st.success(f"✅ {ans}")
                elif "SELL" in ans.upper():
                    st.error(f"❌ {ans}")
                else:
                    st.info(f"📊 {ans}")
        else:
            st.warning(f"⚠️ عذراً، حتى المصدر البديل محجوب عن السيرفر حالياً.")
        st.divider()

# تحديث تلقائي كل 60 ثانية
time.sleep(60)
st.rerun()
