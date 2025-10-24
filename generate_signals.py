"""
Toplu Sinyal Üretimi - Tüm hisseler için sinyal üret
"""
from strategies.signal_generator import SignalGenerator
from database.db_manager import DatabaseManager
import json

def main():
    print("="*80)
    print("🎯 SİNYAL ÜRETME SİSTEMİ - FAZ 8")
    print("="*80)
    print()

    generator = SignalGenerator()
    db = DatabaseManager()

    # Tüm hisse-timeframe çiftlerini al
    tickers = db.get_all_tickers()

    signals_count = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
    strong_signals = []

    for ticker in tickers:
        timeframes = db.get_all_timeframes_for_ticker(ticker)

        for timeframe in timeframes:
            print(f"🎯 {ticker} ({timeframe})", end=" ")

            # Sinyal üret
            result = generator.generate_combined_signal(ticker, timeframe)

            # Veritabanına kaydet
            db.add_signal(
                ticker=ticker,
                timeframe=timeframe,
                signal=result['signal'],
                score=result['score'],
                details=json.dumps(result['details'])
            )

            signals_count[result['signal']] += 1

            # Güçlü sinyalleri kaydet
            if result['score'] >= 65 or result['score'] <= 35:
                strong_signals.append({
                    'ticker': ticker,
                    'timeframe': timeframe,
                    'signal': result['signal'],
                    'score': result['score'],
                    'details': result['details']
                })

            # Sonucu göster
            emoji = "🟢" if result['signal'] == 'BUY' else ("🔴" if result['signal'] == 'SELL' else "🟡")
            print(f"{emoji} {result['signal']} ({result['score']:.1f}/100)")

    # Özet
    print("\n" + "="*80)
    print("📊 SİNYAL ÖZETİ")
    print("="*80)

    total = sum(signals_count.values())
    print(f"\n✅ Toplam Sinyal: {total}")
    print(f"🟢 AL (BUY): {signals_count['BUY']} ({signals_count['BUY']/total*100:.1f}%)")
    print(f"🔴 SAT (SELL): {signals_count['SELL']} ({signals_count['SELL']/total*100:.1f}%)")
    print(f"🟡 BEKLE (HOLD): {signals_count['HOLD']} ({signals_count['HOLD']/total*100:.1f}%)")

    # Güçlü sinyaller
    if strong_signals:
        print(f"\n💪 GÜÇLÜ SİNYALLER (Score >=65 or <=35):")
        for sig in strong_signals:
            emoji = "🟢" if sig['signal'] == 'BUY' else "🔴"
            print(f"{emoji} {sig['ticker']} ({sig['timeframe']}): {sig['score']:.1f}/100")

            # Detayları göster
            trend = sig['details']['trend']
            momentum = sig['details']['momentum']
            volatility = sig['details']['volatility']

            details = []
            if trend['signal'] != 'HOLD':
                details.append(f"Trend:{trend['signal']}({trend['score']:.1f})")
            if momentum['signal'] != 'HOLD':
                details.append(f"Momentum:{momentum['signal']}({momentum['score']:.1f})")
            if volatility['signal'] != 'HOLD':
                details.append(f"Volatility:{volatility['signal']}({volatility['score']:.1f})")

            if details:
                print(f"   → {', '.join(details)}")

    print("\n" + "="*80)
    print("📊 Backtest için: python backtest_all.py (Bir sonraki faz)")
    print("="*80)

if __name__ == "__main__":
    main()
