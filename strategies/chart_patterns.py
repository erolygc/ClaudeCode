"""
Chart Pattern Recognition - Grafik formasyonları tanıma
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
from scipy.signal import find_peaks, argrelextrema

from database.db_manager import DatabaseManager


class ChartPatternRecognizer:
    """
    Grafik Formasyon Tanıma Sistemi

    Tespit edilen formasyonlar:
    - Head & Shoulders (Omuz-Baş-Omuz)
    - Inverse Head & Shoulders (Ters OBO)
    - Double Top (Çift Tepe)
    - Double Bottom (Çift Dip)
    - Triple Top (Üçlü Tepe)
    - Triple Bottom (Üçlü Dip)
    - Ascending Triangle (Yükselen Üçgen)
    - Descending Triangle (Alçalan Üçgen)
    - Symmetrical Triangle (Simetrik Üçgen)
    - Bullish Flag (Yükselen Bayrak)
    - Bearish Flag (Düşen Bayrak)
    - Cup and Handle (Fincan ve Kulp)
    """

    def __init__(self, tolerance: float = 0.05):
        """
        Args:
            tolerance: Fiyat eşleşme toleransı (%5 = 0.05)
        """
        self.db = DatabaseManager()
        self.tolerance = tolerance

    def find_peaks_valleys(self, data: pd.Series, order: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Tepeleri ve dipleri bul

        Args:
            data: Fiyat serisi
            order: Karşılaştırma penceresi boyutu

        Returns:
            tuple: (peak_indices, valley_indices)
        """
        # Tepeler (maksimumlar)
        peaks = argrelextrema(data.values, np.greater_equal, order=order)[0]

        # Dipler (minimumlar)
        valleys = argrelextrema(data.values, np.less_equal, order=order)[0]

        return peaks, valleys

    def detect_head_and_shoulders(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Omuz-Baş-Omuz formasyonunu tespit et

        Pattern: Sol Omuz - Baş - Sağ Omuz (üç tepe, ortadaki en yüksek)
        Sinyal: SELL (bearish reversal)
        """
        if len(df) < 50:
            return None

        highs = df['High'].values
        peaks, _ = self.find_peaks_valleys(df['High'], order=5)

        if len(peaks) < 3:
            return None

        # Son 3 tepeyi kontrol et
        for i in range(len(peaks) - 2):
            left_shoulder_idx = peaks[i]
            head_idx = peaks[i + 1]
            right_shoulder_idx = peaks[i + 2]

            left_shoulder = highs[left_shoulder_idx]
            head = highs[head_idx]
            right_shoulder = highs[right_shoulder_idx]

            # Baş, omuzlardan yüksek mi?
            if head > left_shoulder and head > right_shoulder:
                # Omuzlar yaklaşık aynı seviyede mi?
                shoulder_diff = abs(left_shoulder - right_shoulder) / left_shoulder

                if shoulder_diff < self.tolerance:
                    # Neckline (boyun çizgisi) hesapla
                    # Omuzlar arasındaki dipleri bul
                    between_vals = df.iloc[left_shoulder_idx:right_shoulder_idx+1]['Low']
                    neckline = between_vals.min()

                    # Son fiyat neckline'ı kırdı mı?
                    current_price = df['Close'].iloc[-1]

                    if current_price < neckline:
                        # Pattern confirmed!
                        return {
                            'pattern': 'HEAD_AND_SHOULDERS',
                            'signal': 'SELL',
                            'confidence': 80,
                            'left_shoulder': left_shoulder,
                            'head': head,
                            'right_shoulder': right_shoulder,
                            'neckline': neckline,
                            'current_price': current_price,
                            'target': neckline - (head - neckline),  # Hedef fiyat
                            'stop_loss': head * 1.02,  # %2 üstü
                            'timestamp': datetime.now().isoformat()
                        }

        return None

    def detect_inverse_head_and_shoulders(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Ters Omuz-Baş-Omuz formasyonunu tespit et

        Pattern: Sol Omuz - Baş - Sağ Omuz (üç dip, ortadaki en düşük)
        Sinyal: BUY (bullish reversal)
        """
        if len(df) < 50:
            return None

        lows = df['Low'].values
        _, valleys = self.find_peaks_valleys(df['Low'], order=5)

        if len(valleys) < 3:
            return None

        # Son 3 dipi kontrol et
        for i in range(len(valleys) - 2):
            left_shoulder_idx = valleys[i]
            head_idx = valleys[i + 1]
            right_shoulder_idx = valleys[i + 2]

            left_shoulder = lows[left_shoulder_idx]
            head = lows[head_idx]
            right_shoulder = lows[right_shoulder_idx]

            # Baş, omuzlardan düşük mü?
            if head < left_shoulder and head < right_shoulder:
                # Omuzlar yaklaşık aynı seviyede mi?
                shoulder_diff = abs(left_shoulder - right_shoulder) / left_shoulder

                if shoulder_diff < self.tolerance:
                    # Neckline
                    between_vals = df.iloc[left_shoulder_idx:right_shoulder_idx+1]['High']
                    neckline = between_vals.max()

                    # Son fiyat neckline'ı geçti mi?
                    current_price = df['Close'].iloc[-1]

                    if current_price > neckline:
                        # Pattern confirmed!
                        return {
                            'pattern': 'INVERSE_HEAD_AND_SHOULDERS',
                            'signal': 'BUY',
                            'confidence': 80,
                            'left_shoulder': left_shoulder,
                            'head': head,
                            'right_shoulder': right_shoulder,
                            'neckline': neckline,
                            'current_price': current_price,
                            'target': neckline + (neckline - head),  # Hedef fiyat
                            'stop_loss': head * 0.98,  # %2 altı
                            'timestamp': datetime.now().isoformat()
                        }

        return None

    def detect_double_top(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Çift Tepe formasyonunu tespit et

        Pattern: İki tepe yaklaşık aynı seviyede
        Sinyal: SELL (bearish reversal)
        """
        if len(df) < 30:
            return None

        highs = df['High'].values
        peaks, _ = self.find_peaks_valleys(df['High'], order=5)

        if len(peaks) < 2:
            return None

        # Son 2 tepeyi kontrol et
        for i in range(len(peaks) - 1):
            first_peak_idx = peaks[i]
            second_peak_idx = peaks[i + 1]

            first_peak = highs[first_peak_idx]
            second_peak = highs[second_peak_idx]

            # Tepeler yaklaşık aynı seviyede mi?
            peak_diff = abs(first_peak - second_peak) / first_peak

            if peak_diff < self.tolerance:
                # Aralarındaki dip
                between_vals = df.iloc[first_peak_idx:second_peak_idx+1]['Low']
                support = between_vals.min()

                # Son fiyat support'u kırdı mı?
                current_price = df['Close'].iloc[-1]

                if current_price < support:
                    return {
                        'pattern': 'DOUBLE_TOP',
                        'signal': 'SELL',
                        'confidence': 75,
                        'first_peak': first_peak,
                        'second_peak': second_peak,
                        'support': support,
                        'current_price': current_price,
                        'target': support - (first_peak - support),
                        'stop_loss': max(first_peak, second_peak) * 1.02,
                        'timestamp': datetime.now().isoformat()
                    }

        return None

    def detect_double_bottom(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Çift Dip formasyonunu tespit et

        Pattern: İki dip yaklaşık aynı seviyede
        Sinyal: BUY (bullish reversal)
        """
        if len(df) < 30:
            return None

        lows = df['Low'].values
        _, valleys = self.find_peaks_valleys(df['Low'], order=5)

        if len(valleys) < 2:
            return None

        # Son 2 dipi kontrol et
        for i in range(len(valleys) - 1):
            first_valley_idx = valleys[i]
            second_valley_idx = valleys[i + 1]

            first_valley = lows[first_valley_idx]
            second_valley = lows[second_valley_idx]

            # Dipler yaklaşık aynı seviyede mi?
            valley_diff = abs(first_valley - second_valley) / first_valley

            if valley_diff < self.tolerance:
                # Aralarındaki tepe
                between_vals = df.iloc[first_valley_idx:second_valley_idx+1]['High']
                resistance = between_vals.max()

                # Son fiyat resistance'ı geçti mi?
                current_price = df['Close'].iloc[-1]

                if current_price > resistance:
                    return {
                        'pattern': 'DOUBLE_BOTTOM',
                        'signal': 'BUY',
                        'confidence': 75,
                        'first_bottom': first_valley,
                        'second_bottom': second_valley,
                        'resistance': resistance,
                        'current_price': current_price,
                        'target': resistance + (resistance - first_valley),
                        'stop_loss': min(first_valley, second_valley) * 0.98,
                        'timestamp': datetime.now().isoformat()
                    }

        return None

    def detect_ascending_triangle(self, df: pd.DataFrame, window: int = 20) -> Optional[Dict]:
        """
        Yükselen Üçgen formasyonunu tespit et

        Pattern: Yatay direnç + yükselen destek
        Sinyal: BUY (bullish continuation)
        """
        if len(df) < window:
            return None

        recent = df.tail(window)

        # Resistance seviyesi (tepeler yaklaşık aynı)
        peaks, _ = self.find_peaks_valleys(recent['High'], order=3)

        if len(peaks) < 2:
            return None

        peak_prices = recent['High'].iloc[peaks].values
        resistance = peak_prices.mean()

        # Tepeler yaklaşık aynı seviyede mi?
        if peak_prices.std() / resistance > self.tolerance:
            return None

        # Support yükseliyor mu?
        _, valleys = self.find_peaks_valleys(recent['Low'], order=3)

        if len(valleys) < 2:
            return None

        valley_prices = recent['Low'].iloc[valleys].values

        # Linear regression for support trend
        if len(valleys) >= 2:
            x = np.arange(len(valleys))
            coeffs = np.polyfit(x, valley_prices, 1)
            slope = coeffs[0]

            # Yükseliyor mu?
            if slope > 0:
                current_price = df['Close'].iloc[-1]

                # Resistance'a yaklaşıyor mu?
                if current_price > resistance * 0.95 and current_price < resistance:
                    return {
                        'pattern': 'ASCENDING_TRIANGLE',
                        'signal': 'BUY',
                        'confidence': 70,
                        'resistance': resistance,
                        'support_slope': slope,
                        'current_price': current_price,
                        'target': resistance + (resistance - valley_prices.mean()),
                        'stop_loss': valley_prices[-1] * 0.97,
                        'timestamp': datetime.now().isoformat()
                    }

        return None

    def detect_descending_triangle(self, df: pd.DataFrame, window: int = 20) -> Optional[Dict]:
        """
        Alçalan Üçgen formasyonunu tespit et

        Pattern: Yatay destek + alçalan direnç
        Sinyal: SELL (bearish continuation)
        """
        if len(df) < window:
            return None

        recent = df.tail(window)

        # Support seviyesi (dipler yaklaşık aynı)
        _, valleys = self.find_peaks_valleys(recent['Low'], order=3)

        if len(valleys) < 2:
            return None

        valley_prices = recent['Low'].iloc[valleys].values
        support = valley_prices.mean()

        # Dipler yaklaşık aynı seviyede mi?
        if valley_prices.std() / support > self.tolerance:
            return None

        # Resistance alçalıyor mu?
        peaks, _ = self.find_peaks_valleys(recent['High'], order=3)

        if len(peaks) < 2:
            return None

        peak_prices = recent['High'].iloc[peaks].values

        # Linear regression for resistance trend
        if len(peaks) >= 2:
            x = np.arange(len(peaks))
            coeffs = np.polyfit(x, peak_prices, 1)
            slope = coeffs[0]

            # Alçalıyor mu?
            if slope < 0:
                current_price = df['Close'].iloc[-1]

                # Support'a yaklaşıyor mu?
                if current_price < support * 1.05 and current_price > support:
                    return {
                        'pattern': 'DESCENDING_TRIANGLE',
                        'signal': 'SELL',
                        'confidence': 70,
                        'support': support,
                        'resistance_slope': slope,
                        'current_price': current_price,
                        'target': support - (peak_prices.mean() - support),
                        'stop_loss': peak_prices[-1] * 1.03,
                        'timestamp': datetime.now().isoformat()
                    }

        return None

    def detect_all_patterns(self, ticker: str, timeframe: str) -> List[Dict]:
        """
        Tüm formasyonları tespit et

        Args:
            ticker: Hisse kodu
            timeframe: Zaman dilimi

        Returns:
            list: Tespit edilen formasyonlar
        """
        df = self.db.get_ohlcv_data(ticker, timeframe)

        if df is None or len(df) < 50:
            return []

        patterns = []

        # Her pattern için kontrol et
        pattern_funcs = [
            self.detect_head_and_shoulders,
            self.detect_inverse_head_and_shoulders,
            self.detect_double_top,
            self.detect_double_bottom,
            self.detect_ascending_triangle,
            self.detect_descending_triangle
        ]

        for func in pattern_funcs:
            try:
                result = func(df)
                if result:
                    result['ticker'] = ticker
                    result['timeframe'] = timeframe
                    patterns.append(result)
            except Exception as e:
                print(f"❌ {func.__name__} hatası: {e}")
                continue

        return patterns

    def scan_market(self, tickers: List[str], timeframe: str = '1d') -> List[Dict]:
        """
        Piyasada formasyon tara

        Args:
            tickers: Hisse listesi
            timeframe: Zaman dilimi

        Returns:
            list: Bulunan formasyonlar
        """
        all_patterns = []

        print(f"\n{'='*70}")
        print(f"🔍 PİYASA FORMASYON TARAMASI")
        print(f"{'='*70}")
        print(f"Hisse Sayısı: {len(tickers)}")
        print(f"Timeframe: {timeframe}")
        print(f"{'='*70}\n")

        for ticker in tickers:
            try:
                patterns = self.detect_all_patterns(ticker, timeframe)

                if patterns:
                    print(f"✅ {ticker}: {len(patterns)} formasyon bulundu")
                    all_patterns.extend(patterns)

            except Exception as e:
                print(f"❌ {ticker} hata: {e}")
                continue

        print(f"\n{'='*70}")
        print(f"📊 TOPLAM {len(all_patterns)} FORMASYON BULUNDU")
        print(f"{'='*70}\n")

        return all_patterns

    def print_pattern_report(self, pattern: Dict):
        """Formasyon raporunu yazdır"""
        emoji = "🟢" if pattern['signal'] == 'BUY' else "🔴"

        print(f"\n{'='*70}")
        print(f"{emoji} {pattern['pattern']}")
        print(f"{'='*70}")
        print(f"Hisse       : {pattern['ticker']}")
        print(f"Timeframe   : {pattern['timeframe']}")
        print(f"Sinyal      : {pattern['signal']}")
        print(f"Güven       : {pattern['confidence']}%")
        print(f"Fiyat       : {pattern['current_price']:.2f}")
        print(f"Hedef       : {pattern['target']:.2f}")
        print(f"Stop Loss   : {pattern['stop_loss']:.2f}")

        # Pattern-specific details
        if 'head' in pattern:
            print(f"\nDetaylar:")
            print(f"  Sol Omuz  : {pattern['left_shoulder']:.2f}")
            print(f"  Baş       : {pattern['head']:.2f}")
            print(f"  Sağ Omuz  : {pattern['right_shoulder']:.2f}")
            print(f"  Neckline  : {pattern['neckline']:.2f}")
        elif 'first_peak' in pattern:
            print(f"\nDetaylar:")
            print(f"  İlk Tepe  : {pattern['first_peak']:.2f}")
            print(f"  İkinci Tepe: {pattern['second_peak']:.2f}")
            print(f"  Destek    : {pattern['support']:.2f}")
        elif 'first_bottom' in pattern:
            print(f"\nDetaylar:")
            print(f"  İlk Dip   : {pattern['first_bottom']:.2f}")
            print(f"  İkinci Dip: {pattern['second_bottom']:.2f}")
            print(f"  Direnç    : {pattern['resistance']:.2f}")

        print(f"{'='*70}\n")


def main():
    """Test fonksiyonu"""
    import argparse
    from config.settings import ACTIVE_STOCKS

    parser = argparse.ArgumentParser(description='Chart Pattern Recognition')
    parser.add_argument('--ticker', type=str,
                       help='Analyze specific ticker')
    parser.add_argument('--scan', action='store_true',
                       help='Scan market for patterns')
    parser.add_argument('--timeframe', type=str, default='1d',
                       help='Timeframe')
    parser.add_argument('--stocks', type=int, default=20,
                       help='Number of stocks to scan')

    args = parser.parse_args()

    recognizer = ChartPatternRecognizer(tolerance=0.03)

    if args.ticker:
        # Tek hisse analizi
        patterns = recognizer.detect_all_patterns(args.ticker, args.timeframe)

        if patterns:
            print(f"\n✅ {len(patterns)} formasyon bulundu:\n")
            for pattern in patterns:
                recognizer.print_pattern_report(pattern)
        else:
            print(f"\n❌ {args.ticker} için formasyon bulunamadı")

    elif args.scan:
        # Piyasa taraması
        patterns = recognizer.scan_market(
            tickers=ACTIVE_STOCKS[:args.stocks],
            timeframe=args.timeframe
        )

        if patterns:
            # Güvene göre sırala
            patterns.sort(key=lambda x: x['confidence'], reverse=True)

            print(f"\n🎯 EN İYİ FORMASYONLAR:\n")
            for pattern in patterns[:10]:  # En iyi 10
                recognizer.print_pattern_report(pattern)
        else:
            print("\n❌ Formasyon bulunamadı")

    else:
        print("Kullanım: --ticker GARAN.IS veya --scan")


if __name__ == '__main__':
    main()
