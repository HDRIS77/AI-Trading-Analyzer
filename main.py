import streamlit as st
import ccxt
import pandas as pd
from groq import Groq
import time

# --- الإعدادات الآمنة ---
st.set_page_config(page_title="AI Market Scanner", layout="wide")
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)
exchange = ccxt.binance()

# قائمة العملات التي سيوفر الرادار مراقبتها
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT']

def fetch_and_analyze(symbol):
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=50)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        current_price = df['close'].iloc[-1]
        
        # تحليل فني سريع (RSI)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain.iloc[-1] / loss.iloc[-1])))
        
        # سؤال Groq عن العملة
        prompt = f"Quick analysis for {symbol}: Price {current_price}, RSI {rsi:.2f}. Decision (BUY/SELL/HOLD) and Confidence %? Short reason."
        chat = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return symbol, current_price, chat.choices[0].message.content
    except:
        return symbol, 0, "Error | 0 | Connection Issue"

st.title("🎯 رادار الفرص الذهبية (Multi-Scanner)")
st.write("يتم فحص أفضل 6 عملات رقمية الآن بحثاً عن إشارة 90% ثقة...")

if st.button('إبدأ المسح الشامل 🚀') or st.checkbox("تحديث تلقائي كل دقيقة"):
    cols = st.columns(2) # عرض النتائج في عمودين لتوفير المساحة
    
    for i, sym in enumerate(SYMBOLS):
        with cols[i % 2]:
            sym_name, price, res = fetch_and_analyze(sym)
            
            # تصميم البطاقة (Card) لكل عملة
            with st.container():
                st.subheader(f"🪙 {sym_name}")
                if "BUY" in res.upper() and "90" in res:
                    st.success(f"🔥 فرصة شراء ذهبية: {res}")
                elif "SELL" in res.upper() and "90" in res:
                    st.error(f"⚠️ فرصة بيع قوية: {res}")
                else:
                    st.info(f"📊 التحليل: {res}")
                st.divider()
    
    if st.checkbox("تنبيه صوتي عند وجود فرصة"):
        st.write("📢 سيتم تفعيل جرس التنبيه عند ظهور ثقة +95%")

    time.sleep(60)
    st.rerun()
