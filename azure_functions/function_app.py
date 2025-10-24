"""
Azure Functions App - Otomatik Trading System Execution
"""
import azure.functions as func
import logging
import json
import os
from datetime import datetime
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors.market_data_collector import MarketDataCollector
from indicators.technical_indicators import TechnicalIndicators
from strategies.signal_generator import SignalGenerator
from strategies.backtest_engine import BacktestEngine
from database.db_manager import DatabaseManager
from config.settings import TEST_HISSELER, TIMEFRAMES

app = func.FunctionApp()


@app.timer_trigger(schedule="0 0 18 * * 1-5", arg_name="myTimer", run_on_startup=False,
                   use_monitor=False)
def daily_trading_pipeline(myTimer: func.TimerRequest) -> None:
    """
    Ana trading pipeline - Her iş günü saat 18:00'de çalışır

    Schedule: "0 0 18 * * 1-5" = Pazartesi-Cuma 18:00
    (BIST kapanış: 18:00, veri toplanır)
    """
    if myTimer.past_due:
        logging.info('Timer is past due!')

    logging.info('🚀 Trading Pipeline başlatıldı: %s', datetime.now())

    results = {
        'timestamp': datetime.now().isoformat(),
        'status': 'started',
        'phases': {}
    }

    try:
        # FAZ 6: Veri Toplama
        logging.info('📊 FAZ 6: Veri toplama başlatıldı...')
        data_results = collect_market_data()
        results['phases']['data_collection'] = data_results
        logging.info(f'✅ FAZ 6 tamamlandı: {data_results}')

        # FAZ 7: İndikatör Hesaplama
        logging.info('📐 FAZ 7: İndikatör hesaplama başlatıldı...')
        indicator_results = calculate_indicators()
        results['phases']['indicator_calculation'] = indicator_results
        logging.info(f'✅ FAZ 7 tamamlandı: {indicator_results}')

        # FAZ 8: Sinyal Üretimi
        logging.info('🎯 FAZ 8: Sinyal üretimi başlatıldı...')
        signal_results = generate_signals()
        results['phases']['signal_generation'] = signal_results
        logging.info(f'✅ FAZ 8 tamamlandı: {signal_results}')

        # FAZ 9: Backtest
        logging.info('📈 FAZ 9: Backtest başlatıldı...')
        backtest_results = run_backtest()
        results['phases']['backtest'] = backtest_results
        logging.info(f'✅ FAZ 9 tamamlandı: {backtest_results}')

        results['status'] = 'completed'

        # Email bildirimi gönder
        send_email_notification(results)

        logging.info('✅ Trading Pipeline başarıyla tamamlandı!')

    except Exception as e:
        logging.error(f'❌ Pipeline hatası: {str(e)}', exc_info=True)
        results['status'] = 'failed'
        results['error'] = str(e)

        # Hata bildirimi gönder
        send_error_notification(e)


def collect_market_data():
    """Piyasa verilerini topla"""
    collector = MarketDataCollector()
    db = DatabaseManager()

    total_bars = 0
    successful_stocks = 0

    for ticker in TEST_HISSELER:
        db.add_stock(ticker)

        for tf_name, tf_config in TIMEFRAMES.items():
            try:
                data = collector.collect_data(
                    ticker=ticker,
                    timeframe=tf_config['interval'],
                    period=tf_config['period']
                )

                if data is not None:
                    added = db.add_ohlcv_data(ticker, tf_name, data)
                    total_bars += len(data)
                    successful_stocks += 1

            except Exception as e:
                logging.error(f'Veri toplama hatası {ticker} {tf_name}: {str(e)}')

    return {
        'total_bars': total_bars,
        'successful_stocks': successful_stocks,
        'total_stocks': len(TEST_HISSELER) * len(TIMEFRAMES)
    }


def calculate_indicators():
    """Teknik indikatörleri hesapla"""
    import numpy as np
    db = DatabaseManager()

    total_indicators = 0
    successful_calculations = 0

    tickers = db.get_all_tickers()

    for ticker in tickers:
        timeframes = db.get_all_timeframes_for_ticker(ticker)

        for timeframe in timeframes:
            try:
                df = db.get_ohlcv_data(ticker, timeframe)

                if df is None or len(df) < 200:
                    continue

                calc = TechnicalIndicators(df)
                indicators = calc.calculate_all()

                saved = 0
                for ind_name, ind_values in indicators.items():
                    for date_idx, value in zip(df.index, ind_values):
                        if not np.isnan(value):
                            db.add_indicator_value(ticker, timeframe, date_idx, ind_name, float(value))
                            saved += 1

                total_indicators += saved
                successful_calculations += 1

            except Exception as e:
                logging.error(f'İndikatör hesaplama hatası {ticker} {tf_name}: {str(e)}')

    return {
        'total_indicators': total_indicators,
        'successful_calculations': successful_calculations
    }


def generate_signals():
    """Trading sinyalleri üret"""
    generator = SignalGenerator()
    db = DatabaseManager()

    signals_count = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
    strong_signals = []

    tickers = db.get_all_tickers()

    for ticker in tickers:
        timeframes = db.get_all_timeframes_for_ticker(ticker)

        for timeframe in timeframes:
            try:
                result = generator.generate_combined_signal(ticker, timeframe)

                db.add_signal(
                    ticker=ticker,
                    timeframe=timeframe,
                    signal=result['signal'],
                    score=result['score'],
                    details=json.dumps(result['details'])
                )

                signals_count[result['signal']] += 1

                if result['score'] >= 65 or result['score'] <= 35:
                    strong_signals.append({
                        'ticker': ticker,
                        'timeframe': timeframe,
                        'signal': result['signal'],
                        'score': result['score']
                    })

            except Exception as e:
                logging.error(f'Sinyal üretim hatası {ticker} {timeframe}: {str(e)}')

    return {
        'total_signals': sum(signals_count.values()),
        'buy_signals': signals_count['BUY'],
        'sell_signals': signals_count['SELL'],
        'hold_signals': signals_count['HOLD'],
        'strong_signals': strong_signals
    }


def run_backtest():
    """Backtest çalıştır"""
    engine = BacktestEngine()

    results = engine.backtest_all_signals()

    if results is not None:
        # Özet metrikleri hesapla
        total_trades = len(results)
        winning_trades = len(results[results['win'] == 1])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        avg_return = results['net_return_pct'].mean() if total_trades > 0 else 0

        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': round(win_rate, 2),
            'avg_return': round(avg_return, 2)
        }

    return {
        'total_trades': 0,
        'message': 'No testable signals found'
    }


def send_email_notification(results):
    """Email bildirimi gönder"""
    # Email gönderme fonksiyonu - ayrı modülde implement edilecek
    from utils.email_sender import EmailSender

    try:
        email_sender = EmailSender()
        email_sender.send_daily_report(results)
        logging.info('📧 Email bildirimi gönderildi')
    except Exception as e:
        logging.error(f'Email gönderme hatası: {str(e)}')


def send_error_notification(error):
    """Hata bildirimi gönder"""
    from utils.email_sender import EmailSender

    try:
        email_sender = EmailSender()
        email_sender.send_error_alert(error)
        logging.info('🚨 Hata bildirimi gönderildi')
    except Exception as e:
        logging.error(f'Hata bildirimi gönderme hatası: {str(e)}')


@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    logging.info('Health check request received')

    return func.HttpResponse(
        json.dumps({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'Trading System'
        }),
        mimetype="application/json",
        status_code=200
    )


@app.route(route="manual-trigger", auth_level=func.AuthLevel.FUNCTION)
def manual_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """Manuel pipeline tetikleme (admin only)"""
    logging.info('Manual trigger request received')

    try:
        # Pipeline'ı çalıştır
        timer = func.TimerRequest(None, None)
        daily_trading_pipeline(timer)

        return func.HttpResponse(
            json.dumps({'status': 'Pipeline triggered successfully'}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({'status': 'error', 'message': str(e)}),
            mimetype="application/json",
            status_code=500
        )
