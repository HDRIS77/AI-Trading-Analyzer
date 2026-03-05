import streamlit as st
import pandas as pd
from groq import Groq
import requests
import time

# --- الإعدادات ---
st.set_page_config(page_title="AI Sniper Radar V4", layout="wide")
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# عملات بتنسيق Binance
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']

def get_data_ultra_safe(symbol):
    """جلب بيانات عبر روابط بديلة متعددة لتجنب الحجب"""
    endpoints = [
        f"https://api1.binance.com/api/3/ticker/price?symbol={symbol}",
        f"https://api2.binance.com/api/3/ticker/price?symbol={symbol}",
        f"https://api3.binance.com/api/3/ticker/price?symbol={symbol}"
    ]
    for url in endpoints:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                return float(res.json()['price'])
        except:
            continue
    return None

def ask_ai_expert(symbol, price):
    try:
        prompt = f"Analyze {symbol} at ${price:,.2f}. Give Decision (BUY/SELL/HOLD), Confidence %, and short reason."
        chat = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return chat.choices[0].message.content
    except:
        return "AI Advisor Busy | 0% | Server Overload"

# --- الواجهة ---
st.title("🎯 رادار القناص (النسخة الفولاذية V4)")
st.write("تم تفعيل بروتوكول تخطي الحجب عبر Proxy APIs")

if st.button("تحديث يدوي 🔄"):
    st.rerun()

cols = st.columns(2)
for i, sym in enumerate(SYMBOLS):
    with cols[i % 2]:
        st.subheader(f"🪙 {sym}")
        price = get_data_ultra_safe(sym)
        
        if price is not None:
            st.metric("السعر اللحظي", f"${price:,.2f}")
            with st.spinner('جاري استشارة الذكاء الاصطناعي...'):
                ans = ask_ai_expert(sym, price)
                
                if "BUY" in ans.upper():
                    st.success(f"✅ {ans}")
                elif "SELL" in ans.upper():
                    st.error(f"❌ {ans}")
                else:
                    st.info(f"📊 {ans}")
        else:
            st.warning(f"⚠️ جميع السيرفرات محجوبة حالياً لعملة {sym}. جرب بعد قليل.")
        st.divider()

# تحديث تلقائي ذكي
time.sleep(30)
st.rerun()
