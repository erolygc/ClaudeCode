"""
System Status Checker - Trading System Sağlık Kontrolü

Bu script sisteminizin durumunu kontrol eder:
- Database bağlantısı
- Veri miktarları
- Son güncelleme tarihleri
- Performans metrikleri
- Potansiyel sorunlar
"""
import os
import sys
import time
from datetime import datetime

# Proje kök dizinini Python path'e ekle
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.db_manager import DatabaseManager
import pandas as pd


class SystemStatusChecker:
    """Sistem durumu kontrolcüsü"""

    def __init__(self):
        self.db = DatabaseManager()
        self.issues = []
        self.warnings = []

    def run_all_checks(self):
        """Tüm kontrolleri çalıştır"""
        print("="*80)
        print("🔍 SİSTEM DURUMU KONTROLÜ")
        print("="*80)
        print(f"📅 Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Kontrolleri çalıştır
        self.check_database()
        self.check_data_quality()
        self.check_indicators()
        self.check_signals()
        self.check_performance()

        # Özet
        self.print_summary()

    def check_database(self):
        """Database bağlantısı ve dosya kontrolü"""
        print("📁 DATABASE KONTROLÜ")
        print("-" * 80)

        try:
            # Database dosyası var mı?
            from config.settings import DATABASE_PATH
            if os.path.exists(DATABASE_PATH):
                size = os.path.getsize(DATABASE_PATH)
                print(f"✅ Database dosyası: {DATABASE_PATH}")
                print(f"   Boyut: {size / 1024 / 1024:.2f} MB")

                # Bağlantı testi
                conn = self.db.get_connection()
                conn.close()
                print(f"✅ Database bağlantısı: OK")
            else:
                print(f"❌ Database dosyası bulunamadı: {DATABASE_PATH}")
                self.issues.append("Database dosyası bulunamadı")

        except Exception as e:
            print(f"❌ Database hatası: {e}")
            self.issues.append(f"Database hatası: {e}")

        print()

    def check_data_quality(self):
        """Veri kalitesi kontrolü"""
        print("📊 VERİ KALİTESİ KONTROLÜ")
        print("-" * 80)

        conn = self.db.get_connection()

        try:
            # Hisse sayısı
            stocks = pd.read_sql_query("SELECT COUNT(DISTINCT ticker) as count FROM ohlcv_data", conn)
            stock_count = stocks['count'].iloc[0]
            print(f"📈 Toplam hisse sayısı: {stock_count}")

            if stock_count == 0:
                self.issues.append("Hiç hisse verisi yok!")
            elif stock_count < 3:
                self.warnings.append(f"Az sayıda hisse var: {stock_count}")

            # OHLCV bar sayısı
            bars = pd.read_sql_query("SELECT COUNT(*) as count FROM ohlcv_data", conn)
            bar_count = bars['count'].iloc[0]
            print(f"📊 Toplam OHLCV bar: {bar_count:,}")

            if bar_count < 1000:
                self.warnings.append(f"Az sayıda bar var: {bar_count}")

            # Hisse bazında detay
            stock_details = pd.read_sql_query("""
                SELECT ticker, timeframe, COUNT(*) as bar_count,
                       MIN(date) as first_date, MAX(date) as last_date
                FROM ohlcv_data
                GROUP BY ticker, timeframe
                ORDER BY ticker, timeframe
            """, conn)

            print(f"\n📋 Hisse Detayları:")
            for _, row in stock_details.iterrows():
                print(f"   {row['ticker']} ({row['timeframe']}): {row['bar_count']:,} bar "
                      f"({row['first_date'][:10]} → {row['last_date'][:10]})")

                # Kontroller
                if row['bar_count'] < 200:
                    self.warnings.append(f"{row['ticker']} ({row['timeframe']}): Yetersiz veri ({row['bar_count']} bar)")

        except Exception as e:
            print(f"❌ Veri kalitesi kontrolü hatası: {e}")
            self.issues.append(f"Veri kalitesi hatası: {e}")

        finally:
            conn.close()

        print()

    def check_indicators(self):
        """İndikatör kontrolü"""
        print("📐 İNDİKATÖR KONTROLÜ")
        print("-" * 80)

        conn = self.db.get_connection()

        try:
            # Toplam indikatör sayısı
            ind_count = pd.read_sql_query("SELECT COUNT(*) as count FROM indicators", conn)
            total_indicators = ind_count['count'].iloc[0]
            print(f"📈 Toplam indikatör değeri: {total_indicators:,}")

            if total_indicators == 0:
                self.issues.append("Hiç indikatör hesaplanmamış!")
            elif total_indicators < 10000:
                self.warnings.append(f"Az sayıda indikatör: {total_indicators:,}")

            # İndikatör türleri
            ind_types = pd.read_sql_query("""
                SELECT indicator_name, COUNT(*) as count
                FROM indicators
                GROUP BY indicator_name
                ORDER BY indicator_name
            """, conn)

            print(f"\n📊 İndikatör Türleri ({len(ind_types)} tür):")
            for _, row in ind_types.iterrows():
                print(f"   {row['indicator_name']}: {row['count']:,} değer")

            # Beklenen indikatör türleri
            expected_indicators = ['SMA_20', 'SMA_50', 'SMA_200', 'EMA_12', 'EMA_26',
                                  'RSI_14', 'MACD', 'BB_UPPER', 'BB_LOWER', 'STOCH_K',
                                  'ATR_14', 'ADX_14', 'OBV', 'WILLR_14']

            missing = set(expected_indicators) - set(ind_types['indicator_name'].tolist())
            if missing:
                self.warnings.append(f"Eksik indikatörler: {', '.join(missing)}")

            # En son güncelleme
            last_update = pd.read_sql_query("""
                SELECT MAX(created_at) as last_update FROM indicators
            """, conn)

            if not last_update.empty and last_update['last_update'].iloc[0]:
                print(f"\n⏰ Son güncelleme: {last_update['last_update'].iloc[0]}")

        except Exception as e:
            print(f"❌ İndikatör kontrolü hatası: {e}")
            self.issues.append(f"İndikatör hatası: {e}")

        finally:
            conn.close()

        print()

    def check_signals(self):
        """Sinyal kontrolü"""
        print("🎯 SİNYAL KONTROLÜ")
        print("-" * 80)

        conn = self.db.get_connection()

        try:
            # Toplam sinyal sayısı
            sig_count = pd.read_sql_query("SELECT COUNT(*) as count FROM signals", conn)
            total_signals = sig_count['count'].iloc[0]
            print(f"📊 Toplam sinyal: {total_signals}")

            if total_signals == 0:
                self.warnings.append("Hiç sinyal üretilmemiş!")

            # Sinyal dağılımı
            sig_dist = pd.read_sql_query("""
                SELECT signal, COUNT(*) as count
                FROM signals
                GROUP BY signal
            """, conn)

            print(f"\n📈 Sinyal Dağılımı:")
            for _, row in sig_dist.iterrows():
                emoji = "🟢" if row['signal'] == 'BUY' else ("🔴" if row['signal'] == 'SELL' else "🟡")
                pct = (row['count'] / total_signals * 100) if total_signals > 0 else 0
                print(f"   {emoji} {row['signal']}: {row['count']} ({pct:.1f}%)")

            # Güçlü sinyaller
            strong_signals = pd.read_sql_query("""
                SELECT ticker, timeframe, signal, score, created_at
                FROM signals
                WHERE score >= 65 OR score <= 35
                ORDER BY created_at DESC
                LIMIT 5
            """, conn)

            if not strong_signals.empty:
                print(f"\n💪 Son Güçlü Sinyaller:")
                for _, row in strong_signals.iterrows():
                    emoji = "🟢" if row['signal'] == 'BUY' else "🔴"
                    print(f"   {emoji} {row['ticker']} ({row['timeframe']}): {row['signal']} - {row['score']:.1f}/100")

            # En son sinyal
            last_signal = pd.read_sql_query("""
                SELECT MAX(created_at) as last_signal FROM signals
            """, conn)

            if not last_signal.empty and last_signal['last_signal'].iloc[0]:
                print(f"\n⏰ Son sinyal üretimi: {last_signal['last_signal'].iloc[0]}")

        except Exception as e:
            print(f"❌ Sinyal kontrolü hatası: {e}")
            self.issues.append(f"Sinyal hatası: {e}")

        finally:
            conn.close()

        print()

    def check_performance(self):
        """Performans kontrolü"""
        print("⚡ PERFORMANS KONTROLÜ")
        print("-" * 80)

        # Hızlı performans testi
        conn = self.db.get_connection()

        try:
            # Query performance test
            start = time.time()
            result = pd.read_sql_query("""
                SELECT ticker, timeframe, COUNT(*) as count
                FROM indicators
                WHERE ticker = (SELECT ticker FROM ohlcv_data LIMIT 1)
                GROUP BY ticker, timeframe
            """, conn)
            query_time = time.time() - start

            print(f"🔍 Query hızı: {query_time*1000:.2f} ms")

            if query_time > 1.0:
                self.warnings.append(f"Yavaş query performansı: {query_time:.2f}s")
            else:
                print(f"✅ Query performansı: İyi")

            # Index kontrolü
            indexes = pd.read_sql_query("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND name LIKE 'idx_%'
            """, conn)

            print(f"\n📊 Database Index'leri: {len(indexes)}")
            for _, row in indexes.iterrows():
                print(f"   ✅ {row['name']}")

            if len(indexes) < 3:
                self.warnings.append("Eksik database index'leri")

        except Exception as e:
            print(f"❌ Performans kontrolü hatası: {e}")

        finally:
            conn.close()

        print()

    def print_summary(self):
        """Özet rapor"""
        print("="*80)
        print("📋 ÖZET")
        print("="*80)

        if not self.issues and not self.warnings:
            print("✅ Sistem durumu: MÜKEMMEL!")
            print("   Hiçbir sorun veya uyarı yok.")
        else:
            if self.issues:
                print(f"❌ KRİTİK SORUNLAR ({len(self.issues)}):")
                for issue in self.issues:
                    print(f"   • {issue}")
                print()

            if self.warnings:
                print(f"⚠️  UYARILAR ({len(self.warnings)}):")
                for warning in self.warnings:
                    print(f"   • {warning}")
                print()

        print("="*80)


def main():
    checker = SystemStatusChecker()
    checker.run_all_checks()


if __name__ == "__main__":
    main()
