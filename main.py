import streamlit as st
import pandas as pd
from groq import Groq
import plotly.graph_objects as go
import requests
from datetime import datetime
import time

# --- الإعدادات ---
st.set_page_config(page_title="AI Market Scanner Pro", layout="wide")
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# قائمة العملات
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT']

def fetch_data_direct(symbol):
    """جلب البيانات عبر API مباشر لضمان تخطي الحجب"""
    try:
        url = f"https://api.binance.com/api/3/klines?symbol={symbol}&interval=15m&limit=50"
        response = requests.get(url, timeout=10)
        data = response.json()
        df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'close_time', 'qav', 'num_trades', 'taker_base', 'taker_quote', 'ignore'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].apply(pd.to_numeric)
        return df
    except:
        return None

def analyze_with_ai(symbol, price, df):
    # حساب RSI بسيط يدوياً
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
    rsi = 100 - (100 / (1 + (gain / loss))) if loss != 0 else 50
    
    prompt = f"Analyze {symbol} at ${price:.2f}. RSI: {rsi:.2f}. Decision (BUY/SELL/HOLD)? Confidence %? Reason?"
    chat = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return chat.choices[0].message.content, rsi

# --- الواجهة ---
st.title("🎯 رادار الفرص الذهبية (V3 - النسخة المستقرة)")
st.write(f"🕒 تحديث مباشر: {datetime.now().strftime('%H:%M:%S')}")

auto_refresh = st.sidebar.checkbox("تحديث تلقائي كل 30 ثانية", value=True)

cols = st.columns(2)
for i, sym in enumerate(SYMBOLS):
    with cols[i % 2]:
        df = fetch_data_direct(sym)
        if df is not None:
            price = df['close'].iloc[-1]
            analysis, rsi_val = analyze_with_ai(sym, price, df)
            
            st.subheader(f"🪙 {sym}")
            if "BUY" in analysis.upper() and "90" in analysis:
                st.success(f"🔥 إشارة شراء: {analysis}")
            elif "SELL" in analysis.upper() and "90" in analysis:
                st.error(f"⚠️ إشارة بيع: {analysis}")
            else:
                st.info(f"📊 التحليل: {analysis}")
            
            # الشارت
            fig = go.Figure(data=[go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
            fig.update_layout(xaxis_rangeslider_visible=False, height=250, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"❌ تعذر الاتصال ببيانات {sym}")
        st.divider()

if auto_refresh:
    time.sleep(30)
    st.rerun()
