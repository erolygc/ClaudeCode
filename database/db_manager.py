"""
Veritabanı Yöneticisi - SQLite ile veri yönetimi
"""
import sqlite3
import pandas as pd
from config.settings import DATABASE_PATH

class DatabaseManager:
    """SQLite veritabanı yönetimi"""

    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()

    def get_connection(self):
        """Veritabanı bağlantısı oluştur"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Veritabanı tablolarını oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Hisseler tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hisseler (
                ticker TEXT PRIMARY KEY,
                name TEXT,
                sector TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # OHLCV verisi tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ohlcv_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, timeframe, date)
            )
        """)

        # İndikatörler tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                date TEXT NOT NULL,
                indicator_name TEXT NOT NULL,
                value REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, timeframe, date, indicator_name)
            )
        """)

        # Sinyaller tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                signal TEXT NOT NULL,
                score REAL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Performans için index'ler oluştur
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ohlcv_ticker_timeframe
            ON ohlcv_data(ticker, timeframe)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_indicators_ticker_timeframe
            ON indicators(ticker, timeframe, indicator_name)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_signals_ticker_timeframe
            ON signals(ticker, timeframe, created_at DESC)
        """)

        conn.commit()
        conn.close()

    def add_stock(self, ticker, name=None, sector=None):
        """Hisse ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO hisseler (ticker, name, sector)
                VALUES (?, ?, ?)
            """, (ticker, name, sector))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Zaten var

        conn.close()

    def add_ohlcv_data(self, ticker, timeframe, df):
        """OHLCV verisi ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        added = 0
        for idx, row in df.iterrows():
            try:
                # Timestamp'i string'e çevir
                date_str = idx.strftime('%Y-%m-%d %H:%M:%S') if hasattr(idx, 'strftime') else str(idx)

                cursor.execute("""
                    INSERT INTO ohlcv_data (ticker, timeframe, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (ticker, timeframe, date_str,
                      float(row['Open']), float(row['High']),
                      float(row['Low']), float(row['Close']),
                      int(row['Volume'])))
                added += 1
            except sqlite3.IntegrityError:
                # Zaten var, güncelle
                cursor.execute("""
                    UPDATE ohlcv_data
                    SET open=?, high=?, low=?, close=?, volume=?
                    WHERE ticker=? AND timeframe=? AND date=?
                """, (float(row['Open']), float(row['High']),
                      float(row['Low']), float(row['Close']),
                      int(row['Volume']), ticker, timeframe, date_str))

        conn.commit()
        conn.close()
        return added

    def get_ohlcv_data(self, ticker, timeframe):
        """OHLCV verisini getir"""
        conn = self.get_connection()

        df = pd.read_sql_query("""
            SELECT date, open, high, low, close, volume
            FROM ohlcv_data
            WHERE ticker = ? AND timeframe = ?
            ORDER BY date ASC
        """, conn, params=(ticker, timeframe))

        conn.close()

        if len(df) == 0:
            return None

        # Date sütununu datetime'a çevir ve index yap
        df['date'] = pd.to_datetime(df['date'], format='mixed', utc=True)
        df = df.set_index('date')

        # Sütun isimlerini düzelt (ilk harf büyük)
        df.columns = [col.capitalize() for col in df.columns]

        return df

    def add_indicator_value(self, ticker, timeframe, date, indicator_name, value):
        """
        İndikatör değeri ekle (tek değer için)

        NOT: Bulk insert için add_indicator_values_bulk kullanın (çok daha hızlı!)
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Timestamp'i string'e çevir
        date_str = date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(date, 'strftime') else str(date)

        try:
            cursor.execute("""
                INSERT INTO indicators (ticker, timeframe, date, indicator_name, value)
                VALUES (?, ?, ?, ?, ?)
            """, (ticker, timeframe, date_str, indicator_name, value))
        except sqlite3.IntegrityError:
            # Zaten var, güncelle
            cursor.execute("""
                UPDATE indicators
                SET value = ?
                WHERE ticker=? AND timeframe=? AND date=? AND indicator_name=?
            """, (value, ticker, timeframe, date_str, indicator_name))

        conn.commit()
        conn.close()

    def add_indicator_values_bulk(self, ticker, timeframe, indicators_dict, dates):
        """
        İndikatör değerlerini toplu ekle (BULK INSERT - ÇOK HIZLI!)

        Args:
            ticker: Hisse kodu
            timeframe: Zaman dilimi
            indicators_dict: {indicator_name: numpy_array} formatında indikatörler
            dates: Tarih array'i (pandas DatetimeIndex)

        Returns:
            int: Eklenen kayıt sayısı

        Example:
            indicators = {
                'RSI_14': array([45.2, 52.1, ...]),
                'SMA_20': array([100.5, 101.2, ...])
            }
            db.add_indicator_values_bulk('GARAN.IS', '1d', indicators, dates)
        """
        import numpy as np

        conn = self.get_connection()
        cursor = conn.cursor()

        # Toplu INSERT için veri hazırla
        bulk_data = []

        for ind_name, ind_values in indicators_dict.items():
            for date_idx, value in zip(dates, ind_values):
                # NaN değerleri atla
                if not np.isnan(value):
                    # Timestamp'i string'e çevir
                    date_str = date_idx.strftime('%Y-%m-%d %H:%M:%S') if hasattr(date_idx, 'strftime') else str(date_idx)
                    bulk_data.append((ticker, timeframe, date_str, ind_name, float(value)))

        # Toplu INSERT (executemany ile)
        if bulk_data:
            cursor.executemany("""
                INSERT OR REPLACE INTO indicators (ticker, timeframe, date, indicator_name, value)
                VALUES (?, ?, ?, ?, ?)
            """, bulk_data)

            conn.commit()

        count = len(bulk_data)
        conn.close()

        return count

    def get_latest_indicator_value(self, ticker, timeframe, indicator_name):
        """En son indikatör değerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT value FROM indicators
            WHERE ticker=? AND timeframe=? AND indicator_name=?
            ORDER BY date DESC
            LIMIT 1
        """, (ticker, timeframe, indicator_name))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None

    def add_signal(self, ticker, timeframe, signal, score, details=None):
        """Sinyal ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO signals (ticker, timeframe, signal, score, details)
            VALUES (?, ?, ?, ?, ?)
        """, (ticker, timeframe, signal, score, details))

        conn.commit()
        conn.close()

    def get_all_tickers(self):
        """Tüm hisseleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT ticker FROM ohlcv_data")
        tickers = [row[0] for row in cursor.fetchall()]

        conn.close()
        return tickers

    def get_all_timeframes_for_ticker(self, ticker):
        """Bir hisse için tüm zaman dilimlerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT timeframe FROM ohlcv_data
            WHERE ticker = ?
        """, (ticker,))
        timeframes = [row[0] for row in cursor.fetchall()]

        conn.close()
        return timeframes
