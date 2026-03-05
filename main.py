import streamlit as st
import yfinance as yf
import pandas as pd
from groq import Groq
import plotly.graph_objects as go
import time
from datetime import datetime

# --- الإعدادات الأساسية ---
st.set_page_config(page_title="AI Multi-Scanner Pro", layout="wide")

# مفتاح Groq الخاص بك
GROQ_API_KEY = "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"

# تهيئة Groq
client = Groq(api_key=GROQ_API_KEY)

# قائمة العملات بتنسيق Yahoo Finance (BTC-USD بدل BTC/USDT)
SYMBOLS = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD']

def get_data_and_analyze(symbol):
    try:
        # جلب البيانات من Yahoo Finance (فريم 15 دقيقة لآخر يومين)
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="2d", interval="15m")
        
        if df.empty or len(df) < 20:
            return None, "No Data"

        current_price = df['Close'].iloc[-1]
        
        # حساب مؤشر RSI بسيط
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        # سؤال Groq AI
        prompt = f"""
        Quick Financial Analysis for {symbol}:
        - Price: {current_price:.2f}
        - RSI: {rsi:.2f}
        Decision (BUY/SELL/HOLD)? Confidence %? One short reason.
        Format: القرار | الثقة | السبب
        """
        
        chat = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        ai_res = chat.choices[0].message.content
        return df, ai_res
    except Exception as e:
        return None, f"Error: {str(e)}"

# --- واجهة الموقع ---
st.title("🎯 رادار الفرص الذهبية (نسخة Yahoo Finance)")
st.write(f"⏱️ آخر تحديث للسوق: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# خيارات التحكم
with st.sidebar:
    st.header("⚙️ التحكم")
    auto_refresh = st.checkbox("تحديث تلقائي كل دقيقة", value=False)
    st.info("هذه النسخة تستخدم Yahoo Finance لتجنب مشاكل الحجب.")

# عرض النتائج في شبكة (Grid)
cols = st.columns(2)

for i, sym in enumerate(SYMBOLS):
    with cols[i % 2]:
        df, result = get_data_and_analyze(sym)
        
        st.subheader(f"🪙 {sym}")
        if df is not None:
            # تمييز القرار بالألوان
            if "BUY" in result.upper() and "90" in result:
                st.success(f"🔥 إشارة دخول: {result}")
            elif "SELL" in result.upper() and "90" in result:
                st.error(f"⚠️ إشارة خروج: {result}")
            else:
                st.info(f"📊 التحليل: {result}")
            
            # رسم شارت مصغر
            fig = go.Figure(data=[go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']
            )])
            fig.update_layout(xaxis_rangeslider_visible=False, height=300, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"❌ تعذر جلب بيانات {sym}")
        st.divider()

# التحديث التلقائي
if auto_refresh:
    time.sleep(60)
    st.rerun()
