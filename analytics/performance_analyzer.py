"""
Performance Analyzer - Gelişmiş performans metrikleri
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

from database.db_manager import DatabaseManager


@dataclass
class PerformanceMetrics:
    """Performans metrikleri"""
    # Temel metrikler
    total_return: float
    annual_return: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float

    # Risk metrikleri
    max_drawdown: float
    max_drawdown_duration: int  # gün
    volatility: float
    downside_deviation: float

    # İşlem metrikleri
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    avg_trade: float
    largest_win: float
    largest_loss: float

    # Risk/Ödül
    risk_reward_ratio: float
    expectancy: float

    # Zaman bazlı
    avg_holding_period: float  # gün
    avg_bars_in_trade: int

    # İlave metrikler
    recovery_factor: float
    ulcer_index: float
    value_at_risk_95: float  # VaR 95%
    conditional_var_95: float  # CVaR 95%


class PerformanceAnalyzer:
    """
    Gelişmiş Performans Analizi Sistemi

    Portföyün performansını detaylı olarak analiz eder:
    - Sharpe, Sortino, Calmar oranları
    - Maximum drawdown ve recovery analizi
    - Win rate, profit factor
    - Risk-adjusted returns
    - VaR ve CVaR hesaplama
    """

    def __init__(self, risk_free_rate: float = 0.10):
        """
        Args:
            risk_free_rate: Risksiz getiri oranı (yıllık, örn: 0.10 = %10)
        """
        self.db = DatabaseManager()
        self.risk_free_rate = risk_free_rate

    def calculate_metrics(self,
                         equity_curve: pd.Series,
                         trades: List[Dict]) -> PerformanceMetrics:
        """
        Tüm performans metriklerini hesapla

        Args:
            equity_curve: Sermaye eğrisi (index: datetime, value: capital)
            trades: İşlem listesi [{entry_date, exit_date, pnl, pnl_percent, ...}]

        Returns:
            PerformanceMetrics: Hesaplanan metrikler
        """
        if len(equity_curve) < 2:
            raise ValueError("Equity curve en az 2 veri noktası içermeli")

        # Günlük getiriler
        returns = equity_curve.pct_change().dropna()

        # Temel metrikler
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0] - 1) * 100
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
        annual_return = ((1 + total_return/100) ** (365/max(days, 1)) - 1) * 100

        # Risk metrikleri
        volatility = returns.std() * np.sqrt(252) * 100  # Annualized
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252) * 100

        # Sharpe Ratio
        excess_return = annual_return - self.risk_free_rate * 100
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0

        # Sortino Ratio
        sortino_ratio = excess_return / downside_deviation if downside_deviation > 0 else 0

        # Maximum Drawdown
        max_dd, max_dd_duration = self._calculate_max_drawdown(equity_curve)

        # Calmar Ratio
        calmar_ratio = annual_return / abs(max_dd) if max_dd != 0 else 0

        # İşlem metrikleri
        trade_metrics = self._calculate_trade_metrics(trades)

        # Recovery Factor
        recovery_factor = total_return / abs(max_dd) if max_dd != 0 else 0

        # Ulcer Index
        ulcer_index = self._calculate_ulcer_index(equity_curve)

        # VaR ve CVaR
        var_95 = self._calculate_var(returns, confidence=0.95)
        cvar_95 = self._calculate_cvar(returns, confidence=0.95)

        return PerformanceMetrics(
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=max_dd,
            max_drawdown_duration=max_dd_duration,
            volatility=volatility,
            downside_deviation=downside_deviation,
            **trade_metrics,
            recovery_factor=recovery_factor,
            ulcer_index=ulcer_index,
            value_at_risk_95=var_95,
            conditional_var_95=cvar_95
        )

    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> Tuple[float, int]:
        """Maximum drawdown ve süresini hesapla"""
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax * 100

        max_dd = drawdown.min()

        # Drawdown süresi
        dd_duration = 0
        current_duration = 0
        in_drawdown = False

        for dd in drawdown:
            if dd < 0:
                in_drawdown = True
                current_duration += 1
            else:
                if in_drawdown:
                    dd_duration = max(dd_duration, current_duration)
                    current_duration = 0
                    in_drawdown = False

        if in_drawdown:
            dd_duration = max(dd_duration, current_duration)

        return max_dd, dd_duration

    def _calculate_trade_metrics(self, trades: List[Dict]) -> Dict:
        """İşlem metriklerini hesapla"""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'avg_trade': 0,
                'largest_win': 0,
                'largest_loss': 0,
                'risk_reward_ratio': 0,
                'expectancy': 0,
                'avg_holding_period': 0,
                'avg_bars_in_trade': 0
            }

        pnls = [t['pnl'] for t in trades]
        winning = [p for p in pnls if p > 0]
        losing = [p for p in pnls if p < 0]

        total_trades = len(trades)
        winning_trades = len(winning)
        losing_trades = len(losing)

        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        avg_win = np.mean(winning) if winning else 0
        avg_loss = np.mean(losing) if losing else 0
        avg_trade = np.mean(pnls)

        largest_win = max(pnls) if pnls else 0
        largest_loss = min(pnls) if pnls else 0

        # Profit Factor
        gross_profit = sum(winning) if winning else 0
        gross_loss = abs(sum(losing)) if losing else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Risk/Reward Ratio
        risk_reward_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0

        # Expectancy
        expectancy = (win_rate/100 * avg_win) + ((1 - win_rate/100) * avg_loss)

        # Holding period
        holding_periods = []
        for t in trades:
            if 'entry_date' in t and 'exit_date' in t:
                entry = pd.to_datetime(t['entry_date'])
                exit = pd.to_datetime(t['exit_date'])
                holding_periods.append((exit - entry).days)

        avg_holding_period = np.mean(holding_periods) if holding_periods else 0

        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_trade': avg_trade,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'risk_reward_ratio': risk_reward_ratio,
            'expectancy': expectancy,
            'avg_holding_period': avg_holding_period,
            'avg_bars_in_trade': 0  # Placeholder
        }

    def _calculate_ulcer_index(self, equity_curve: pd.Series) -> float:
        """
        Ulcer Index - Drawdown'ların şiddeti ve süresini birleştirir
        Düşük değer = daha iyi
        """
        cummax = equity_curve.cummax()
        drawdown = (equity_curve - cummax) / cummax * 100

        # Squared drawdowns
        squared_dd = drawdown ** 2

        # Ulcer Index = sqrt(mean(squared_dd))
        ulcer_index = np.sqrt(squared_dd.mean())

        return ulcer_index

    def _calculate_var(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """
        Value at Risk (VaR) - Belirli güven aralığında maksimum beklenen kayıp
        """
        if len(returns) < 2:
            return 0

        var = np.percentile(returns, (1 - confidence) * 100)
        return var * 100  # Yüzde olarak

    def _calculate_cvar(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """
        Conditional Value at Risk (CVaR) - VaR'ı aşan kayıpların ortalaması
        """
        if len(returns) < 2:
            return 0

        var = np.percentile(returns, (1 - confidence) * 100)
        cvar = returns[returns <= var].mean()
        return cvar * 100  # Yüzde olarak

    def generate_report(self, metrics: PerformanceMetrics) -> str:
        """Detaylı performans raporu oluştur"""
        report = f"""
╔════════════════════════════════════════════════════════════════════╗
║                    📊 PERFORMANS RAPORU                            ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  💰 GETİRİ METRİKLERİ                                             ║
║  {'─'*68} ║
║  Toplam Getiri          : {metrics.total_return:>10.2f}%                         ║
║  Yıllık Getiri          : {metrics.annual_return:>10.2f}%                         ║
║                                                                    ║
║  📈 RİSK-AYARLI GETİRİ                                            ║
║  {'─'*68} ║
║  Sharpe Ratio           : {metrics.sharpe_ratio:>10.2f}                            ║
║  Sortino Ratio          : {metrics.sortino_ratio:>10.2f}                            ║
║  Calmar Ratio           : {metrics.calmar_ratio:>10.2f}                            ║
║                                                                    ║
║  ⚠️  RİSK METRİKLERİ                                              ║
║  {'─'*68} ║
║  Maximum Drawdown       : {metrics.max_drawdown:>10.2f}%                         ║
║  Drawdown Süresi        : {metrics.max_drawdown_duration:>10d} gün                       ║
║  Volatilite (Yıllık)    : {metrics.volatility:>10.2f}%                         ║
║  Downside Deviation     : {metrics.downside_deviation:>10.2f}%                         ║
║  Ulcer Index            : {metrics.ulcer_index:>10.2f}                            ║
║  VaR (95%)              : {metrics.value_at_risk_95:>10.2f}%                         ║
║  CVaR (95%)             : {metrics.conditional_var_95:>10.2f}%                         ║
║                                                                    ║
║  📊 İŞLEM İSTATİSTİKLERİ                                          ║
║  {'─'*68} ║
║  Toplam İşlem           : {metrics.total_trades:>10d}                            ║
║  Kazanan İşlem          : {metrics.winning_trades:>10d} ({metrics.win_rate:>5.1f}%)                   ║
║  Kaybeden İşlem         : {metrics.losing_trades:>10d}                            ║
║  Profit Factor          : {metrics.profit_factor:>10.2f}                            ║
║                                                                    ║
║  💵 İŞLEM BAŞINA METRİKLER                                        ║
║  {'─'*68} ║
║  Ortalama Kazanç        : {metrics.avg_win:>10.2f} TL                        ║
║  Ortalama Kayıp         : {metrics.avg_loss:>10.2f} TL                        ║
║  Ortalama İşlem         : {metrics.avg_trade:>10.2f} TL                        ║
║  En Büyük Kazanç        : {metrics.largest_win:>10.2f} TL                        ║
║  En Büyük Kayıp         : {metrics.largest_loss:>10.2f} TL                        ║
║                                                                    ║
║  🎯 RİSK/ÖDÜL ANALİZİ                                             ║
║  {'─'*68} ║
║  Risk/Reward Ratio      : {metrics.risk_reward_ratio:>10.2f}                            ║
║  Expectancy             : {metrics.expectancy:>10.2f} TL                        ║
║  Recovery Factor        : {metrics.recovery_factor:>10.2f}                            ║
║  Ort. Holding Period    : {metrics.avg_holding_period:>10.1f} gün                       ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

📋 PERFORMANS DEĞERLENDİRMESİ:
"""

        # Değerlendirme
        evaluations = []

        if metrics.sharpe_ratio > 2:
            evaluations.append("✅ Mükemmel Sharpe Ratio (>2.0)")
        elif metrics.sharpe_ratio > 1:
            evaluations.append("✅ İyi Sharpe Ratio (>1.0)")
        elif metrics.sharpe_ratio > 0:
            evaluations.append("⚠️  Düşük Sharpe Ratio")
        else:
            evaluations.append("❌ Negatif Sharpe Ratio")

        if metrics.win_rate >= 60:
            evaluations.append("✅ Yüksek Win Rate (≥60%)")
        elif metrics.win_rate >= 50:
            evaluations.append("✅ İyi Win Rate (≥50%)")
        else:
            evaluations.append("⚠️  Düşük Win Rate (<50%)")

        if metrics.profit_factor > 2:
            evaluations.append("✅ Mükemmel Profit Factor (>2.0)")
        elif metrics.profit_factor > 1.5:
            evaluations.append("✅ İyi Profit Factor (>1.5)")
        elif metrics.profit_factor > 1:
            evaluations.append("⚠️  Zayıf Profit Factor")
        else:
            evaluations.append("❌ Kötü Profit Factor (<1.0)")

        if abs(metrics.max_drawdown) < 10:
            evaluations.append("✅ Düşük Maximum Drawdown (<10%)")
        elif abs(metrics.max_drawdown) < 20:
            evaluations.append("⚠️  Orta Maximum Drawdown (<20%)")
        else:
            evaluations.append("❌ Yüksek Maximum Drawdown (≥20%)")

        report += "\n".join(evaluations)
        report += "\n"

        return report

    def export_to_json(self, metrics: PerformanceMetrics, filepath: str):
        """Metrikleri JSON olarak dışa aktar"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'return': {
                    'total_return': metrics.total_return,
                    'annual_return': metrics.annual_return
                },
                'risk_adjusted': {
                    'sharpe_ratio': metrics.sharpe_ratio,
                    'sortino_ratio': metrics.sortino_ratio,
                    'calmar_ratio': metrics.calmar_ratio
                },
                'risk': {
                    'max_drawdown': metrics.max_drawdown,
                    'max_drawdown_duration': metrics.max_drawdown_duration,
                    'volatility': metrics.volatility,
                    'downside_deviation': metrics.downside_deviation,
                    'ulcer_index': metrics.ulcer_index,
                    'var_95': metrics.value_at_risk_95,
                    'cvar_95': metrics.conditional_var_95
                },
                'trades': {
                    'total_trades': metrics.total_trades,
                    'winning_trades': metrics.winning_trades,
                    'losing_trades': metrics.losing_trades,
                    'win_rate': metrics.win_rate,
                    'profit_factor': metrics.profit_factor,
                    'avg_win': metrics.avg_win,
                    'avg_loss': metrics.avg_loss,
                    'avg_trade': metrics.avg_trade,
                    'largest_win': metrics.largest_win,
                    'largest_loss': metrics.largest_loss
                },
                'risk_reward': {
                    'risk_reward_ratio': metrics.risk_reward_ratio,
                    'expectancy': metrics.expectancy,
                    'recovery_factor': metrics.recovery_factor,
                    'avg_holding_period': metrics.avg_holding_period
                }
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    """Test fonksiyonu"""
    # Örnek equity curve oluştur
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, 100)  # Ortalama %0.1, std %2
    equity = 100000 * (1 + returns).cumprod()
    equity_curve = pd.Series(equity, index=dates)

    # Örnek işlemler
    trades = [
        {'entry_date': '2024-01-05', 'exit_date': '2024-01-10', 'pnl': 500},
        {'entry_date': '2024-01-12', 'exit_date': '2024-01-15', 'pnl': -200},
        {'entry_date': '2024-01-18', 'exit_date': '2024-01-22', 'pnl': 800},
        {'entry_date': '2024-01-25', 'exit_date': '2024-01-30', 'pnl': 300},
        {'entry_date': '2024-02-02', 'exit_date': '2024-02-08', 'pnl': -150},
    ]

    # Analiz et
    analyzer = PerformanceAnalyzer()
    metrics = analyzer.calculate_metrics(equity_curve, trades)

    # Rapor yazdır
    print(analyzer.generate_report(metrics))

    # JSON'a aktar
    analyzer.export_to_json(metrics, 'performance_report.json')
    print("📄 Rapor 'performance_report.json' dosyasına kaydedildi")


if __name__ == '__main__':
    main()
