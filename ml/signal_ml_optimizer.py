"""
ML Signal Optimizer - Machine Learning ile sinyal optimizasyonu
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import warnings
warnings.filterwarnings('ignore')

# ML kütüphaneleri (opsiyonel)
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  scikit-learn kurulu değil. ML özellikleri devre dışı.")

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️  XGBoost kurulu değil. XGBoost özellikleri devre dışı.")

from database.db_manager import DatabaseManager


class MLSignalOptimizer:
    """
    Machine Learning Sinyal Optimizasyonu

    Teknik indikatörlerden öğrenip gelecek fiyat hareketlerini tahmin eder:
    - Random Forest Classifier
    - XGBoost Classifier
    - Feature importance analizi
    - Sinyal güvenilirlik skoru
    """

    def __init__(self, model_type: str = 'random_forest'):
        """
        Args:
            model_type: 'random_forest', 'xgboost', veya 'gradient_boosting'
        """
        if not ML_AVAILABLE:
            raise ImportError("scikit-learn kurulu değil. pip install scikit-learn")

        self.db = DatabaseManager()
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False

        # Model oluştur
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=20,
                min_samples_leaf=10,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'xgboost' and XGBOOST_AVAILABLE:
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Desteklenmeyen model tipi: {model_type}")

    def prepare_training_data(self,
                             ticker: str,
                             timeframe: str,
                             lookforward_bars: int = 5,
                             min_return_threshold: float = 0.02) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Eğitim verisini hazırla

        Args:
            ticker: Hisse kodu
            timeframe: Zaman dilimi
            lookforward_bars: Kaç bar sonraya bakalım
            min_return_threshold: Minimum getiri eşiği (%2 = 0.02)

        Returns:
            tuple: (X features, y labels)
        """
        # OHLCV verisini al
        ohlcv = self.db.get_ohlcv_data(ticker, timeframe)
        if ohlcv is None or len(ohlcv) < 100:
            raise ValueError(f"Yetersiz veri: {ticker} {timeframe}")

        # İndikatörleri al
        indicators = self.db.get_indicator_values(ticker, timeframe)
        if indicators is None or len(indicators) < 100:
            raise ValueError(f"Yetersiz indikatör verisi: {ticker} {timeframe}")

        # Birleştir
        df = ohlcv.copy()

        # İndikatörleri ekle
        for indicator in indicators['indicator_name'].unique():
            ind_data = indicators[indicators['indicator_name'] == indicator]
            ind_data = ind_data.set_index('timestamp')
            df[indicator] = ind_data['value']

        # NaN temizle
        df = df.dropna()

        if len(df) < 100:
            raise ValueError("NaN temizliğinden sonra yetersiz veri")

        # Feature'ları hazırla
        feature_cols = [col for col in df.columns
                       if col not in ['Open', 'High', 'Low', 'Close', 'Volume']]

        # Fazla ekle: price momentum, volume ratio
        df['price_momentum'] = df['Close'].pct_change(5) * 100
        df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()

        feature_cols.extend(['price_momentum', 'volume_ratio'])

        # Label oluştur: N bar sonra fiyat değişimi
        df['future_return'] = df['Close'].pct_change(lookforward_bars).shift(-lookforward_bars) * 100

        # Label encode: BUY (1), SELL (-1), HOLD (0)
        df['label'] = 0  # HOLD
        df.loc[df['future_return'] > min_return_threshold * 100, 'label'] = 1  # BUY
        df.loc[df['future_return'] < -min_return_threshold * 100, 'label'] = -1  # SELL

        # Son satırları at (future_return için)
        df = df[:-lookforward_bars]

        # NaN temizle
        df = df.dropna()

        X = df[feature_cols]
        y = df['label']

        self.feature_names = feature_cols

        return X, y

    def train(self,
             tickers: List[str],
             timeframe: str = '1d',
             test_size: float = 0.2) -> Dict:
        """
        Modeli eğit

        Args:
            tickers: Eğitim için hisse listesi
            timeframe: Zaman dilimi
            test_size: Test seti oranı

        Returns:
            dict: Eğitim sonuçları
        """
        print(f"\n{'='*70}")
        print(f"🤖 ML MODELİ EĞİTİMİ BAŞLIYOR")
        print(f"{'='*70}")
        print(f"Model: {self.model_type}")
        print(f"Timeframe: {timeframe}")
        print(f"Hisse Sayısı: {len(tickers)}")
        print(f"{'='*70}\n")

        # Tüm hisselerden veri topla
        all_X = []
        all_y = []

        for ticker in tickers:
            try:
                print(f"📊 {ticker} verisi hazırlanıyor...")
                X, y = self.prepare_training_data(ticker, timeframe)

                all_X.append(X)
                all_y.append(y)

                print(f"   ✅ {len(X)} örnek eklendi")

            except Exception as e:
                print(f"   ❌ Hata: {e}")
                continue

        if not all_X:
            raise ValueError("Hiç eğitim verisi hazırlanamadı")

        # Birleştir
        X = pd.concat(all_X, axis=0)
        y = pd.concat(all_y, axis=0)

        print(f"\n📊 Toplam {len(X)} örnek, {len(self.feature_names)} feature")
        print(f"   BUY: {(y == 1).sum()} | SELL: {(y == -1).sum()} | HOLD: {(y == 0).sum()}")

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        print(f"\n🔧 Eğitim seti: {len(X_train)} | Test seti: {len(X_test)}")

        # XGBoost için label'ları remap et ([-1,0,1] -> [0,1,2])
        if self.model_type == 'xgboost':
            # Label mapping: SELL(-1)->0, HOLD(0)->1, BUY(1)->2
            label_map = {-1: 0, 0: 1, 1: 2}
            y_train_remapped = y_train.map(label_map)
            y_test_remapped = y_test.map(label_map)
        else:
            y_train_remapped = y_train
            y_test_remapped = y_test

        # Normalize
        print(f"📏 Feature'lar normalize ediliyor...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Eğit
        print(f"\n🚀 Model eğitiliyor...")
        self.model.fit(X_train_scaled, y_train_remapped)

        # Performans değerlendir
        train_score = self.model.score(X_train_scaled, y_train_remapped)
        test_score = self.model.score(X_test_scaled, y_test_remapped)

        print(f"\n✅ Eğitim tamamlandı!")
        print(f"   Eğitim Accuracy: {train_score*100:.2f}%")
        print(f"   Test Accuracy: {test_score*100:.2f}%")

        # Predictions
        y_pred = self.model.predict(X_test_scaled)

        # XGBoost için prediction'ları geri map et ([0,1,2] -> [-1,0,1])
        if self.model_type == 'xgboost':
            reverse_map = {0: -1, 1: 0, 2: 1}
            y_pred_original = pd.Series(y_pred).map(reverse_map).values
        else:
            y_pred_original = y_pred

        # Classification report
        print(f"\n📊 SINIFLANDIRMA RAPORU:")
        print(classification_report(
            y_test, y_pred_original,
            target_names=['SELL', 'HOLD', 'BUY'],
            zero_division=0
        ))

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred_original)
        print(f"\n🔢 CONFUSION MATRIX:")
        print(cm)

        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)

            print(f"\n📈 EN ÖNEMLİ 10 FEATURE:")
            for i, row in feature_importance.head(10).iterrows():
                print(f"   {row['feature']:30s}: {row['importance']:.4f}")

        self.is_trained = True

        return {
            'train_score': train_score,
            'test_score': test_score,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'features': len(self.feature_names)
        }

    def predict_signal(self,
                      ticker: str,
                      timeframe: str) -> Optional[Dict]:
        """
        ML modeli ile sinyal tahmini yap

        Args:
            ticker: Hisse kodu
            timeframe: Zaman dilimi

        Returns:
            dict: Tahmin sonucu
        """
        if not self.is_trained:
            raise ValueError("Model henüz eğitilmedi. Önce train() çağırın.")

        try:
            # Son veriyi al
            ohlcv = self.db.get_ohlcv_data(ticker, timeframe)
            indicators = self.db.get_indicator_values(ticker, timeframe)

            if ohlcv is None or indicators is None:
                return None

            # Feature'ları hazırla
            df = ohlcv.copy()

            for indicator in indicators['indicator_name'].unique():
                ind_data = indicators[indicators['indicator_name'] == indicator]
                ind_data = ind_data.set_index('timestamp')
                df[indicator] = ind_data['value']

            # Ekstra feature'lar
            df['price_momentum'] = df['Close'].pct_change(5) * 100
            df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()

            # Son satırı al
            latest = df.iloc[[-1]][self.feature_names]

            # NaN kontrolü
            if latest.isna().any().any():
                return None

            # Normalize
            latest_scaled = self.scaler.transform(latest)

            # Tahmin
            prediction = self.model.predict(latest_scaled)[0]
            probabilities = self.model.predict_proba(latest_scaled)[0]

            # XGBoost için prediction'ı geri map et ([0,1,2] -> [-1,0,1])
            if self.model_type == 'xgboost':
                reverse_map = {0: -1, 1: 0, 2: 1}
                prediction = reverse_map[prediction]
                # Probabilities'i de yeniden sırala [SELL, HOLD, BUY]
                probabilities = [probabilities[0], probabilities[1], probabilities[2]]
            else:
                # Diğer modeller için probabilities'i [-1,0,1] sırasına göre düzenle
                probabilities = [probabilities[0], probabilities[1], probabilities[2]]

            # Label'ı signal'e çevir
            signal_map = {-1: 'SELL', 0: 'HOLD', 1: 'BUY'}
            signal = signal_map[prediction]

            # Confidence score
            confidence = max(probabilities) * 100

            return {
                'ticker': ticker,
                'timeframe': timeframe,
                'signal': signal,
                'confidence': confidence,
                'probabilities': {
                    'SELL': probabilities[0] * 100,
                    'HOLD': probabilities[1] * 100,
                    'BUY': probabilities[2] * 100
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"❌ {ticker} tahmin hatası: {e}")
            return None

    def save_model(self, filepath: str):
        """Modeli kaydet"""
        if not self.is_trained:
            raise ValueError("Model henüz eğitilmedi")

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"✅ Model kaydedildi: {filepath}")

    def load_model(self, filepath: str):
        """Modeli yükle"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.model_type = model_data['model_type']
        self.is_trained = True

        print(f"✅ Model yüklendi: {filepath}")


def main():
    """Test fonksiyonu"""
    import argparse
    from config.settings import ACTIVE_STOCKS

    parser = argparse.ArgumentParser(description='ML Signal Optimizer')
    parser.add_argument('--train', action='store_true',
                       help='Train the model')
    parser.add_argument('--predict', type=str,
                       help='Predict signal for ticker')
    parser.add_argument('--model', type=str, default='random_forest',
                       choices=['random_forest', 'xgboost', 'gradient_boosting'],
                       help='Model type')
    parser.add_argument('--timeframe', type=str, default='1d',
                       help='Timeframe')
    parser.add_argument('--stocks', type=int, default=50,
                       help='Number of stocks to train on (default: 50)')
    parser.add_argument('--save', type=str,
                       help='Save model to file')
    parser.add_argument('--load', type=str,
                       help='Load model from file')

    args = parser.parse_args()

    optimizer = MLSignalOptimizer(model_type=args.model)

    if args.load:
        # Model yükle
        optimizer.load_model(args.load)

    if args.train:
        # Model eğit
        results = optimizer.train(
            tickers=ACTIVE_STOCKS[:args.stocks],  # İlk N hisse
            timeframe=args.timeframe
        )

        print(f"\n{'='*70}")
        print(f"✅ EĞİTİM SONUÇLARI")
        print(f"{'='*70}")
        for key, value in results.items():
            print(f"{key:20s}: {value}")

        if args.save:
            optimizer.save_model(args.save)

    if args.predict:
        # Tahmin yap
        if not optimizer.is_trained:
            print("❌ Model yüklenmedi veya eğitilmedi")
            return

        prediction = optimizer.predict_signal(args.predict, args.timeframe)

        if prediction:
            print(f"\n{'='*70}")
            print(f"🎯 ML TAHMİNİ: {prediction['ticker']}")
            print(f"{'='*70}")
            print(f"Sinyal: {prediction['signal']}")
            print(f"Güvenilirlik: {prediction['confidence']:.1f}%")
            print(f"\nOlasılıklar:")
            for signal, prob in prediction['probabilities'].items():
                print(f"  {signal:4s}: {prob:5.1f}%")
        else:
            print(f"❌ {args.predict} için tahmin yapılamadı")


if __name__ == '__main__':
    if not ML_AVAILABLE:
        print("❌ scikit-learn kurulu değil")
        print("Kurulum: pip install scikit-learn xgboost")
    else:
        main()
