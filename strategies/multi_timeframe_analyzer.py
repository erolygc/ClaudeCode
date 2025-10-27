"""
Multi-Timeframe Analyzer - Çoklu zaman dilimi analizi
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

from database.db_manager import DatabaseManager
from strategies.signal_generator import SignalGenerator


class MultiTimeframeAnalyzer:
    """
    Çoklu Zaman Dilimi Analiz Sistemi

    Farklı zaman dilimlerindeki sinyalleri birleştirerek
    daha güvenilir işlem kararları üretir.

    Temel Prensipler:
    - Uzun timeframe trend belirleme için (1d, 4h)
    - Orta timeframe momentum için (1h, 15m)
    - Kısa timeframe giriş noktası için (5m, 1m)
    - Tüm timeframe'ler uyuşuyorsa → Güçlü sinyal
    - Çoğunluk uyuşuyorsa → Orta sinyal
    - Karışık sinyaller → Zayıf sinyal / HOLD
    """

    def __init__(self):
        self.db = DatabaseManager()
        self.signal_gen = SignalGenerator()

        # Timeframe kategorileri
        self.timeframe_groups = {
            'long': ['1w', '1d'],      # Trend belirleme
            'medium': ['4h', '1h'],    # Momentum
            'short': ['15m', '5m', '1m']  # Giriş noktası
        }

        # Timeframe ağırlıkları (uzun timeframe daha önemli)
        self.timeframe_weights = {
            '1w': 5.0,
            '1d': 4.0,
            '4h': 3.0,
            '1h': 2.5,
            '15m': 2.0,
            '5m': 1.5,
            '1m': 1.0
        }

    def analyze_ticker(self,
                       ticker: str,
                       timeframes: List[str] = None) -> Optional[Dict]:
        """
        Bir hisse için çoklu timeframe analizi yap

        Args:
            ticker: Hisse kodu
            timeframes: Analiz edilecek timeframe'ler (None = hepsi)

        Returns:
            dict: Birleştirilmiş analiz sonucu
        """
        if timeframes is None:
            timeframes = ['1d', '1h', '15m']

        # Her timeframe için sinyal üret
        signals = {}
        for tf in timeframes:
            signal = self.signal_gen.generate_combined_signal(ticker, tf)
            if signal:
                signals[tf] = signal

        if not signals:
            return None

        # Sinyalleri birleştir
        combined = self._combine_signals(ticker, signals)

        return combined

    def _combine_signals(self, ticker: str, signals: Dict[str, Dict]) -> Dict:
        """
        Farklı timeframe'lerden gelen sinyalleri birleştir

        Args:
            ticker: Hisse kodu
            signals: Timeframe -> signal dict'i

        Returns:
            dict: Birleştirilmiş sinyal
        """
        # Sinyal sayılarını hesapla
        buy_count = sum(1 for s in signals.values() if s['signal'] == 'BUY')
        sell_count = sum(1 for s in signals.values() if s['signal'] == 'SELL')
        hold_count = sum(1 for s in signals.values() if s['signal'] == 'HOLD')

        total_signals = len(signals)

        # Ağırlıklı skor hesapla
        weighted_score = 0
        total_weight = 0

        for tf, signal in signals.items():
            weight = self.timeframe_weights.get(tf, 1.0)

            # Sinyal yönüne göre skor
            if signal['signal'] == 'BUY':
                weighted_score += signal['score'] * weight
            elif signal['signal'] == 'SELL':
                weighted_score -= signal['score'] * weight
            # HOLD için 0 ekle

            total_weight += weight

        # Normalize et
        if total_weight > 0:
            final_score = weighted_score / total_weight
        else:
            final_score = 0

        # Final sinyal belirle
        if abs(final_score) < 30:
            final_signal = 'HOLD'
        elif final_score > 0:
            final_signal = 'BUY'
        else:
            final_signal = 'SELL'

        # Güvenilirlik skoru (tüm timeframe'ler uyuşuyorsa yüksek)
        agreement_ratio = max(buy_count, sell_count, hold_count) / total_signals
        confidence = agreement_ratio * 100  # 0-100 arası

        # Trend analizi (uzun timeframe'lerden)
        trend = self._determine_trend(signals)

        # Momentum analizi (orta timeframe'lerden)
        momentum = self._determine_momentum(signals)

        return {
            'ticker': ticker,
            'signal': final_signal,
            'score': abs(final_score),
            'confidence': confidence,
            'timeframe_signals': {tf: s['signal'] for tf, s in signals.items()},
            'timeframe_scores': {tf: s['score'] for tf, s in signals.items()},
            'buy_count': buy_count,
            'sell_count': sell_count,
            'hold_count': hold_count,
            'total_timeframes': total_signals,
            'agreement_ratio': agreement_ratio,
            'trend': trend,
            'momentum': momentum,
            'timestamp': datetime.now().isoformat()
        }

    def _determine_trend(self, signals: Dict[str, Dict]) -> str:
        """Uzun timeframe'lerden trend belirle"""
        long_tf_signals = []

        for tf in self.timeframe_groups['long']:
            if tf in signals:
                long_tf_signals.append(signals[tf]['signal'])

        if not long_tf_signals:
            return 'NEUTRAL'

        buy_count = long_tf_signals.count('BUY')
        sell_count = long_tf_signals.count('SELL')

        if buy_count > sell_count:
            return 'BULLISH'
        elif sell_count > buy_count:
            return 'BEARISH'
        else:
            return 'NEUTRAL'

    def _determine_momentum(self, signals: Dict[str, Dict]) -> str:
        """Orta timeframe'lerden momentum belirle"""
        medium_tf_signals = []

        for tf in self.timeframe_groups['medium']:
            if tf in signals:
                medium_tf_signals.append(signals[tf]['signal'])

        if not medium_tf_signals:
            return 'NEUTRAL'

        buy_count = medium_tf_signals.count('BUY')
        sell_count = medium_tf_signals.count('SELL')

        if buy_count > sell_count:
            return 'POSITIVE'
        elif sell_count > buy_count:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'

    def find_best_entry_points(self,
                               ticker: str,
                               target_signal: str = 'BUY',
                               min_confidence: float = 70.0) -> Optional[Dict]:
        """
        En iyi giriş noktalarını bul

        Args:
            ticker: Hisse kodu
            target_signal: Hedef sinyal ('BUY' veya 'SELL')
            min_confidence: Minimum güvenilirlik skoru

        Returns:
            dict: En iyi giriş noktası bilgisi veya None
        """
        # Tüm timeframe'leri analiz et
        analysis = self.analyze_ticker(
            ticker,
            timeframes=['1d', '4h', '1h', '15m', '5m']
        )

        if not analysis:
            return None

        # Hedef sinyalle uyuşuyor mu?
        if analysis['signal'] != target_signal:
            return None

        # Güvenilirlik yeterli mi?
        if analysis['confidence'] < min_confidence:
            return None

        # Trend ve momentum uyumlu mu?
        if target_signal == 'BUY':
            if analysis['trend'] == 'BEARISH' or analysis['momentum'] == 'NEGATIVE':
                return None
        elif target_signal == 'SELL':
            if analysis['trend'] == 'BULLISH' or analysis['momentum'] == 'POSITIVE':
                return None

        return analysis

    def scan_market(self,
                   tickers: List[str],
                   target_signal: str = 'BUY',
                   min_confidence: float = 70.0,
                   top_n: int = 10) -> List[Dict]:
        """
        Piyasayı tara ve en iyi fırsatları bul

        Args:
            tickers: Taranacak hisse listesi
            target_signal: Hedef sinyal
            min_confidence: Minimum güvenilirlik
            top_n: En iyi N adet sonuç

        Returns:
            list: En iyi fırsatlar (skora göre sıralı)
        """
        opportunities = []

        for ticker in tickers:
            try:
                entry_point = self.find_best_entry_points(
                    ticker=ticker,
                    target_signal=target_signal,
                    min_confidence=min_confidence
                )

                if entry_point:
                    opportunities.append(entry_point)

            except Exception as e:
                print(f"❌ {ticker} analiz hatası: {e}")
                continue

        # Skora göre sırala (en yüksek önce)
        opportunities.sort(key=lambda x: x['score'] * x['confidence'], reverse=True)

        return opportunities[:top_n]

    def get_confirmation_status(self,
                               ticker: str,
                               min_timeframes: int = 3) -> Dict:
        """
        Sinyal onay durumunu kontrol et

        Args:
            ticker: Hisse kodu
            min_timeframes: Minimum onay gereken timeframe sayısı

        Returns:
            dict: Onay durumu bilgisi
        """
        analysis = self.analyze_ticker(ticker, timeframes=['1d', '4h', '1h', '15m'])

        if not analysis:
            return {
                'confirmed': False,
                'reason': 'Analiz başarısız',
                'status': 'ERROR'
            }

        signal = analysis['signal']

        if signal == 'HOLD':
            return {
                'confirmed': False,
                'reason': 'HOLD sinyali',
                'status': 'HOLD',
                'analysis': analysis
            }

        # Aynı yöndeki sinyal sayısı
        agreeing_count = (analysis['buy_count'] if signal == 'BUY'
                         else analysis['sell_count'])

        confirmed = agreeing_count >= min_timeframes

        return {
            'confirmed': confirmed,
            'signal': signal,
            'agreeing_timeframes': agreeing_count,
            'total_timeframes': analysis['total_timeframes'],
            'confidence': analysis['confidence'],
            'trend': analysis['trend'],
            'momentum': analysis['momentum'],
            'status': 'CONFIRMED' if confirmed else 'WEAK',
            'analysis': analysis
        }

    def print_analysis_report(self, analysis: Dict):
        """Analiz raporunu yazdır"""
        print(f"\n{'='*70}")
        print(f"📊 ÇOKLU TIMEFRAME ANALİZİ: {analysis['ticker']}")
        print(f"{'='*70}")

        # Ana sinyal
        signal_emoji = "🟢" if analysis['signal'] == 'BUY' else "🔴" if analysis['signal'] == 'SELL' else "🟡"
        print(f"\n{signal_emoji} FİNAL SİNYAL: {analysis['signal']}")
        print(f"   Skor: {analysis['score']:.1f}")
        print(f"   Güvenilirlik: {analysis['confidence']:.1f}%")
        print(f"   Trend: {analysis['trend']}")
        print(f"   Momentum: {analysis['momentum']}")

        # Timeframe detayları
        print(f"\n📈 TIMEFRAME SİNYALLERİ:")
        print(f"   BUY:  {analysis['buy_count']}/{analysis['total_timeframes']}")
        print(f"   SELL: {analysis['sell_count']}/{analysis['total_timeframes']}")
        print(f"   HOLD: {analysis['hold_count']}/{analysis['total_timeframes']}")
        print(f"   Uyum Oranı: {analysis['agreement_ratio']*100:.1f}%")

        # Her timeframe'in detayı
        print(f"\n🔍 DETAYLAR:")
        for tf in sorted(analysis['timeframe_signals'].keys(),
                        key=lambda x: self.timeframe_weights.get(x, 0),
                        reverse=True):
            signal = analysis['timeframe_signals'][tf]
            score = analysis['timeframe_scores'][tf]
            weight = self.timeframe_weights.get(tf, 1.0)

            emoji = "🟢" if signal == 'BUY' else "🔴" if signal == 'SELL' else "🟡"
            print(f"   {tf:6s} {emoji} {signal:4s} | Skor: {score:5.1f} | Ağırlık: {weight:.1f}")

        print(f"{'='*70}\n")


def main():
    """Test fonksiyonu"""
    import argparse
    from config.settings import ACTIVE_STOCKS

    parser = argparse.ArgumentParser(description='Multi-Timeframe Analyzer')
    parser.add_argument('--ticker', type=str, default=None,
                       help='Analyze specific ticker')
    parser.add_argument('--scan', action='store_true',
                       help='Scan market for opportunities')
    parser.add_argument('--signal', type=str, default='BUY',
                       choices=['BUY', 'SELL'],
                       help='Target signal for scanning')
    parser.add_argument('--confidence', type=float, default=70.0,
                       help='Minimum confidence score')
    parser.add_argument('--top', type=int, default=10,
                       help='Top N opportunities')

    args = parser.parse_args()

    analyzer = MultiTimeframeAnalyzer()

    if args.ticker:
        # Tek hisse analizi
        print(f"\n🔍 {args.ticker} analiz ediliyor...\n")
        analysis = analyzer.analyze_ticker(args.ticker, timeframes=['1d', '4h', '1h', '15m'])

        if analysis:
            analyzer.print_analysis_report(analysis)

            # Onay durumu
            confirmation = analyzer.get_confirmation_status(args.ticker)
            print(f"✅ Onay Durumu: {confirmation['status']}")
            if confirmation['confirmed']:
                print(f"   {confirmation['agreeing_timeframes']}/{confirmation['total_timeframes']} timeframe onayladı")
        else:
            print("❌ Analiz başarısız")

    elif args.scan:
        # Piyasa taraması
        print(f"\n🔍 Piyasa taranıyor ({args.signal} sinyalleri)...\n")
        opportunities = analyzer.scan_market(
            tickers=ACTIVE_STOCKS[:20],  # İlk 20 hisse
            target_signal=args.signal,
            min_confidence=args.confidence,
            top_n=args.top
        )

        if opportunities:
            print(f"\n{'='*70}")
            print(f"🎯 EN İYİ {len(opportunities)} FIRSAT ({args.signal})")
            print(f"{'='*70}\n")

            for i, opp in enumerate(opportunities, 1):
                signal_emoji = "🟢" if opp['signal'] == 'BUY' else "🔴"
                print(f"{i:2d}. {signal_emoji} {opp['ticker']:12s} | "
                      f"Skor: {opp['score']:5.1f} | "
                      f"Güven: {opp['confidence']:5.1f}% | "
                      f"Uyum: {opp['agreement_ratio']*100:5.1f}% | "
                      f"Trend: {opp['trend']:8s}")
        else:
            print(f"❌ {args.signal} sinyali için uygun fırsat bulunamadı")

    else:
        print("Kullanım: --ticker GARAN.IS veya --scan")


if __name__ == '__main__':
    main()
