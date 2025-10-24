"""
Technical Indicators - TA-Lib kullanarak indikatörleri hesapla
"""
import numpy as np
import talib as ta

class TechnicalIndicators:
    """Teknik indikatör hesaplayıcı"""

    def __init__(self, df):
        """
        Args:
            df: OHLCV DataFrame (columns: Open, High, Low, Close, Volume)
        """
        self.df = df.copy()

        # TA-Lib için numpy array'lere çevir (float64 olmalı!)
        self.close = self.df['Close'].squeeze().values.astype(np.float64)
        self.high = self.df['High'].squeeze().values.astype(np.float64)
        self.low = self.df['Low'].squeeze().values.astype(np.float64)
        self.open = self.df['Open'].squeeze().values.astype(np.float64)
        self.volume = self.df['Volume'].squeeze().values.astype(np.float64)

    def calculate_all(self):
        """Tüm indikatörleri hesapla"""
        indicators = {}

        # Trend İndikatörleri
        indicators.update(self.calculate_sma())
        indicators.update(self.calculate_ema())
        indicators.update(self.calculate_macd())
        indicators.update(self.calculate_adx())

        # Momentum İndikatörleri
        indicators.update(self.calculate_rsi())
        indicators.update(self.calculate_stoch())
        indicators.update(self.calculate_williams_r())

        # Volatilite İndikatörleri
        indicators.update(self.calculate_bbands())
        indicators.update(self.calculate_atr())

        # Volume İndikatörleri
        indicators.update(self.calculate_obv())

        return indicators

    def calculate_sma(self):
        """Simple Moving Average"""
        return {
            'SMA_20': ta.SMA(self.close, timeperiod=20),
            'SMA_50': ta.SMA(self.close, timeperiod=50),
            'SMA_200': ta.SMA(self.close, timeperiod=200)
        }

    def calculate_ema(self):
        """Exponential Moving Average"""
        return {
            'EMA_12': ta.EMA(self.close, timeperiod=12),
            'EMA_26': ta.EMA(self.close, timeperiod=26),
            'EMA_50': ta.EMA(self.close, timeperiod=50)
        }

    def calculate_rsi(self):
        """Relative Strength Index"""
        return {
            'RSI_14': ta.RSI(self.close, timeperiod=14)
        }

    def calculate_macd(self):
        """MACD"""
        macd, signal, hist = ta.MACD(
            self.close,
            fastperiod=12,
            slowperiod=26,
            signalperiod=9
        )
        return {
            'MACD': macd,
            'MACD_SIGNAL': signal,
            'MACD_HIST': hist
        }

    def calculate_bbands(self):
        """Bollinger Bands"""
        upper, middle, lower = ta.BBANDS(
            self.close,
            timeperiod=20,
            nbdevup=2,
            nbdevdn=2
        )
        return {
            'BB_UPPER': upper,
            'BB_MIDDLE': middle,
            'BB_LOWER': lower
        }

    def calculate_stoch(self):
        """Stochastic Oscillator"""
        slowk, slowd = ta.STOCH(
            self.high,
            self.low,
            self.close,
            fastk_period=14,
            slowk_period=3,
            slowd_period=3
        )
        return {
            'STOCH_K': slowk,
            'STOCH_D': slowd
        }

    def calculate_atr(self):
        """Average True Range"""
        return {
            'ATR_14': ta.ATR(self.high, self.low, self.close, timeperiod=14)
        }

    def calculate_adx(self):
        """Average Directional Index"""
        return {
            'ADX_14': ta.ADX(self.high, self.low, self.close, timeperiod=14)
        }

    def calculate_obv(self):
        """On Balance Volume"""
        return {
            'OBV': ta.OBV(self.close, self.volume)
        }

    def calculate_williams_r(self):
        """Williams %R"""
        return {
            'WILLR_14': ta.WILLR(self.high, self.low, self.close, timeperiod=14)
        }
