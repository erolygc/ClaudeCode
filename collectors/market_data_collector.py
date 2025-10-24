"""
Market Data Collector - yfinance ile hisse verisi topla
"""
import yfinance as yf
import pandas as pd

class MarketDataCollector:
    """Piyasa verilerini toplayan sınıf"""

    def __init__(self):
        pass

    def collect_data(self, ticker, timeframe='1d', period=None):
        """
        Bir hisse için veri topla

        Args:
            ticker: Hisse sembolü (ör: "GARAN.IS")
            timeframe: Zaman dilimi ('1d', '1h')
            period: Veri periyodu (ör: '2y', '60d')

        Returns:
            DataFrame: OHLCV verisi
        """
        try:
            print(f"  {ticker} ({timeframe}) indiriliyor...", end=" ")

            # Veriyi indir
            data = yf.download(
                ticker,
                period=period,
                interval=timeframe,
                auto_adjust=True,
                progress=False
            )

            # MultiIndex durumunu kontrol et ve düzelt
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            if len(data) == 0:
                print("❌ Veri yok")
                return None

            # Gerekli sütunları kontrol et
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in data.columns for col in required_cols):
                print(f"❌ Eksik sütunlar")
                return None

            print(f"✅ {len(data)} bar")
            return data

        except Exception as e:
            print(f"❌ Hata: {e}")
            return None
