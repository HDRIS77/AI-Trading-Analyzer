import streamlit as st
import pandas as pd
from groq import Groq
import plotly.graph_objects as go
import requests
import time

# --- الإعدادات ---
st.set_page_config(page_title="AI Sniper Radar", layout="wide")
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# العملات
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']

def get_data(symbol):
    """جلب بيانات مباشرة بدون مكتبات وسيطة"""
    try:
        url = f"https://api.binance.com/api/3/klines?symbol={symbol}&interval=15m&limit=50"
        res = requests.get(url, timeout=10)
        data = res.json()
        df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'v', 'ct', 'q', 'n', 'tb', 'tq', 'i'])
        df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].apply(pd.to_numeric)
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        return df
    except:
        return None

def ask_ai(symbol, price, df):
    # حساب RSI سريع
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean().iloc[-1]
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
    rsi = 100 - (100 / (1 + (gain / loss))) if loss != 0 else 50
    
    prompt = f"Crypto: {symbol}, Price: {price}, RSI: {rsi:.2f}. Decision (BUY/SELL/HOLD)? Confidence %? Reason?"
    chat = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return chat.choices[0].message.content

# --- الواجهة ---
st.title("🎯 رادار القناص الذكي (نسخة V3 المستقرة)")

if st.button("تحديث يدوي 🔄") or True:
    cols = st.columns(2)
    for i, sym in enumerate(SYMBOLS):
        with cols[i % 2]:
            df = get_data(sym)
            if df is not None:
                p = df['close'].iloc[-1]
                ans = ask_ai(sym, p, df)
                st.subheader(f"🪙 {sym}")
                
                # تلوين النتيجة
                if "BUY" in ans.upper() and "90" in ans:
                    st.success(f"✅ إشارة قوية: {ans}")
                elif "SELL" in ans.upper() and "90" in ans:
                    st.error(f"❌ إشارة بيع: {ans}")
                else:
                    st.info(f"📊 التحليل: {ans}")
                
                # الشارت
                fig = go.Figure(data=[go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
                fig.update_layout(xaxis_rangeslider_visible=False, height=250, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"❌ تعذر الوصول لبيانات {sym}")
            st.divider()

st.sidebar.write("الحالة: متصل عبر API مباشر")
