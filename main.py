import streamlit as st
import pandas as pd
from groq import Groq
import requests
import time

# --- الإعدادات ---
st.set_page_config(page_title="AI Sniper Radar", layout="wide")
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# العملات بنظام الـ API المباشر
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']

def get_data_safe(symbol):
    """جلب بيانات عبر رابط بديل لضمان تخطي الحجب"""
    try:
        # استخدام رابط API بديل ومستقر
        url = f"https://api1.binance.com/api/3/ticker/price?symbol={symbol}"
        res = requests.get(url, timeout=5)
        price_data = res.json()
        price = float(price_data['price'])
        
        # جلب شمعات بسيطة للتحليل
        k_url = f"https://api1.binance.com/api/3/klines?symbol={symbol}&interval=15m&limit=20"
        k_res = requests.get(k_url, timeout=5)
        k_data = k_res.json()
        
        df = pd.DataFrame(k_data, columns=['t','o','h','l','c','v','ct','q','n','tb','tq','i'])
        df['close'] = pd.to_numeric(df['c'])
        return price, df
    except:
        return None, None

def ask_ai(symbol, price):
    try:
        prompt = f"Crypto: {symbol}, Price: {price}. Should I BUY, SELL, or HOLD? Confidence %? Short reason."
        chat = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return chat.choices[0].message.content
    except:
        return "AI Busy | 0 | Error"

# --- الواجهة ---
st.title("🎯 رادار القناص (النسخة النهائية المستقرة)")

if st.button("تحديث يدوي 🔄"):
    st.rerun()

cols = st.columns(2)
for i, sym in enumerate(SYMBOLS):
    with cols[i % 2]:
        price, df = get_data_safe(sym)
        st.subheader(f"🪙 {sym}")
        
        if price:
            ans = ask_ai(sym, price)
            st.metric("السعر الحالي", f"${price:,.2f}")
            
            if "BUY" in ans.upper():
                st.success(f"✅ {ans}")
            elif "SELL" in ans.upper():
                st.error(f"❌ {ans}")
            else:
                st.info(f"📊 {ans}")
        else:
            st.warning(f"⚠️ تعذر جلب سعر {sym} حالياً. جرب التحديث.")
        st.divider()

# تحديث تلقائي آمن
time.sleep(60)
st.rerun()
