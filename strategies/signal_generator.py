"""
Signal Generator - İndikatörlerden sinyal üret
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from config.settings import SIGNAL_SETTINGS

class SignalGenerator:
    """Sinyal üretici - İndikatörleri analiz eder ve AL/SAT/BEKLE sinyali üretir"""

    def __init__(self):
        self.db = DatabaseManager()

    def generate_combined_signal(self, ticker, timeframe):
        """
        Tüm indikatörleri analiz ederek kombine sinyal üretir

        Returns:
            dict: {
                'signal': 'BUY'/'SELL'/'HOLD',
                'score': 0-100,
                'details': {...}
            }
        """
        # Trend analizi
        trend = self.analyze_trend_indicators(ticker, timeframe)

        # Momentum analizi
        momentum = self.analyze_momentum_indicators(ticker, timeframe)

        # Volatilite analizi
        volatility = self.analyze_volatility_indicators(ticker, timeframe)

        # Ağırlıklı skor hesapla
        final_score = (
            trend['score'] * SIGNAL_SETTINGS['trend_weight'] +
            momentum['score'] * SIGNAL_SETTINGS['momentum_weight'] +
            volatility['score'] * SIGNAL_SETTINGS['volatility_weight']
        )

        # Sinyal belirle
        if final_score >= SIGNAL_SETTINGS['strong_threshold']:
            signal = 'BUY'
        elif final_score <= SIGNAL_SETTINGS['weak_threshold']:
            signal = 'SELL'
        else:
            signal = 'HOLD'

        return {
            'signal': signal,
            'score': round(final_score, 1),
            'details': {
                'trend': trend,
                'momentum': momentum,
                'volatility': volatility
            }
        }

    def analyze_trend_indicators(self, ticker, timeframe):
        """Trend indikatörlerini analiz et"""
        signals = []

        # SMA analizi
        sma_20 = self.db.get_latest_indicator_value(ticker, timeframe, 'SMA_20')
        sma_50 = self.db.get_latest_indicator_value(ticker, timeframe, 'SMA_50')
        sma_200 = self.db.get_latest_indicator_value(ticker, timeframe, 'SMA_200')
        close = self.db.get_ohlcv_data(ticker, timeframe)

        if close is not None and len(close) > 0:
            current_price = close['Close'].iloc[-1]

            if sma_20 and sma_50:
                if sma_20 > sma_50 and current_price > sma_20:
                    signals.append(100)  # Güçlü AL
                elif sma_20 < sma_50 and current_price < sma_20:
                    signals.append(0)   # Güçlü SAT
                else:
                    signals.append(50)  # Nötr

        # MACD analizi
        macd = self.db.get_latest_indicator_value(ticker, timeframe, 'MACD')
        macd_signal = self.db.get_latest_indicator_value(ticker, timeframe, 'MACD_SIGNAL')

        if macd and macd_signal:
            if macd > macd_signal:
                signals.append(100)  # AL
            else:
                signals.append(0)    # SAT

        # ADX analizi
        adx = self.db.get_latest_indicator_value(ticker, timeframe, 'ADX_14')

        if adx:
            if adx > 25:
                # Güçlü trend var, yön SMA'dan al
                if signals:
                    signals.append(signals[0])
            else:
                signals.append(50)  # Zayıf trend, nötr

        # Ortalama skor
        avg_score = sum(signals) / len(signals) if signals else 50

        return {
            'score': avg_score,
            'signal': 'BUY' if avg_score > 65 else ('SELL' if avg_score < 35 else 'HOLD')
        }

    def analyze_momentum_indicators(self, ticker, timeframe):
        """Momentum indikatörlerini analiz et"""
        signals = []

        # RSI analizi
        rsi = self.db.get_latest_indicator_value(ticker, timeframe, 'RSI_14')

        if rsi:
            if rsi < 30:
                signals.append(100)  # Aşırı satım, AL
            elif rsi > 70:
                signals.append(0)    # Aşırı alım, SAT
            elif rsi < 50:
                signals.append(25)   # Zayıf, SAT eğilimi
            else:
                signals.append(75)   # Güçlü, AL eğilimi

        # Stochastic analizi
        stoch_k = self.db.get_latest_indicator_value(ticker, timeframe, 'STOCH_K')
        stoch_d = self.db.get_latest_indicator_value(ticker, timeframe, 'STOCH_D')

        if stoch_k and stoch_d:
            if stoch_k < 20:
                signals.append(100)  # Aşırı satım, AL
            elif stoch_k > 80:
                signals.append(0)    # Aşırı alım, SAT
            elif stoch_k > stoch_d:
                signals.append(75)   # Yükseliş
            else:
                signals.append(25)   # Düşüş

        # Williams %R analizi
        willr = self.db.get_latest_indicator_value(ticker, timeframe, 'WILLR_14')

        if willr:
            if willr < -80:
                signals.append(100)  # Aşırı satım, AL
            elif willr > -20:
                signals.append(0)    # Aşırı alım, SAT
            elif willr < -50:
                signals.append(25)   # Düşüş eğilimi
            else:
                signals.append(75)   # Yükseliş eğilimi

        # Ortalama skor
        avg_score = sum(signals) / len(signals) if signals else 50

        return {
            'score': avg_score,
            'signal': 'BUY' if avg_score > 65 else ('SELL' if avg_score < 35 else 'HOLD')
        }

    def analyze_volatility_indicators(self, ticker, timeframe):
        """Volatilite indikatörlerini analiz et"""
        signals = []

        # Bollinger Bands analizi
        bb_upper = self.db.get_latest_indicator_value(ticker, timeframe, 'BB_UPPER')
        bb_lower = self.db.get_latest_indicator_value(ticker, timeframe, 'BB_LOWER')
        bb_middle = self.db.get_latest_indicator_value(ticker, timeframe, 'BB_MIDDLE')
        close = self.db.get_ohlcv_data(ticker, timeframe)

        if close is not None and len(close) > 0 and bb_upper and bb_lower and bb_middle:
            current_price = close['Close'].iloc[-1]

            if current_price <= bb_lower:
                signals.append(100)  # Alt banda dokundu, AL
            elif current_price >= bb_upper:
                signals.append(0)    # Üst banda dokundu, SAT
            elif current_price < bb_middle:
                signals.append(25)   # Orta bandın altında
            else:
                signals.append(75)   # Orta bandın üstünde

        # ATR analizi (volatilite seviyesi)
        atr = self.db.get_latest_indicator_value(ticker, timeframe, 'ATR_14')

        if atr and close is not None and len(close) > 0:
            current_price = close['Close'].iloc[-1]
            atr_ratio = (atr / current_price) * 100

            # Yüksek volatilite = risk, orta skor
            if atr_ratio > 3:
                signals.append(50)  # Çok volatil, bekle
            else:
                # Düşük volatilite, diğer sinyalleri takip et
                if signals:
                    signals.append(signals[0])
                else:
                    signals.append(50)

        # Ortalama skor
        avg_score = sum(signals) / len(signals) if signals else 50

        return {
            'score': avg_score,
            'signal': 'BUY' if avg_score > 65 else ('SELL' if avg_score < 35 else 'HOLD')
        }
