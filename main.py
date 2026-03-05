import ccxt
import pandas as pd
import time

# 1. إعداد الاتصال بالبورصة (كمثال Binance)
exchange = ccxt.binance()

def fetch_data(symbol='BTC/USDT', timeframe='5m'):
    # جلب آخر 100 شمعة
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df

def analyze_signals(df):
    # حساب المتوسط المتحرك (SMA)
    df['sma_20'] = df['close'].rolling(window=20).mean()
    
    # حساب مؤشر RSI (مؤشر التشبع الشرائي والبيعي)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    last_price = df['close'].iloc[-1]
    last_rsi = df['rsi'].iloc[-1]
    last_sma = df['sma_20'].iloc[-1]

    # منطق اتخاذ القرار (محرك الثقة)
    confidence = 0
    recommendation = "HOLD 🟡"

    if last_price > last_sma: confidence += 40  # سعر فوق المتوسط = اتجاه صاعد
    if last_rsi < 30: confidence += 50         # سعر رخيص جداً = فرصة شراء قوية
    elif last_rsi < 50: confidence += 20       # سعر مقبول للشراء

    if confidence >= 70: recommendation = "STRONG BUY 🟢"
    elif confidence <= 30: recommendation = "STRONG SELL 🔴"

    return recommendation, confidence, last_price

# تشغيل المحلل في حلقة مستمرة
print("🚀 جاري تشغيل مساعد التداول الذكي...")
while True:
    try:
        data = fetch_data()
        rec, conf, price = analyze_signals(data)
        print(f"💰 السعر الحالي: {price} | التوصية: {rec} | نسبة الثقة: {conf}%")
        time.sleep(10) # تحديث كل 10 ثوانٍ
    except Exception as e:
        print(f"❌ خطأ: {e}")
        time.sleep(5)
