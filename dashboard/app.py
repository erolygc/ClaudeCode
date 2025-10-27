"""
Web Dashboard - Flask tabanlı canlı izleme paneli
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from datetime import datetime, timedelta
import pandas as pd


app = Flask(__name__)
CORS(app)  # Cross-origin requests için

# Global database manager
db = DatabaseManager()


@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('index.html')


@app.route('/api/portfolio')
def get_portfolio():
    """Portföy durumunu getir - GERÇEK ZAMANLI"""
    try:
        import json

        # Live trading engine'den JSON dosyasını oku
        portfolio_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'live_portfolio.json')

        if os.path.exists(portfolio_file):
            with open(portfolio_file, 'r', encoding='utf-8') as f:
                portfolio_data = json.load(f)
        else:
            # Dosya yoksa varsayılan değerler
            portfolio_data = {
                'total_capital': 100000,
                'cash': 100000,
                'positions_value': 0,
                'positions_count': 0,
                'daily_pnl': 0,
                'total_pnl': 0,
                'return_percent': 0,
                'last_update': datetime.now().isoformat()
            }

        return jsonify({
            'status': 'ok',
            'portfolio': portfolio_data
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/signals')
def get_signals():
    """Son sinyalleri getir"""
    try:
        hours = int(request.args.get('hours', 24))

        conn = db.get_connection()
        cutoff_time = datetime.now() - timedelta(hours=hours)

        df = pd.read_sql_query("""
            SELECT
                ticker,
                timeframe,
                signal,
                score,
                created_at
            FROM signals
            WHERE created_at >= ?
            ORDER BY created_at DESC
            LIMIT 100
        """, conn, params=(cutoff_time.strftime('%Y-%m-%d %H:%M:%S'),))

        conn.close()

        signals = df.to_dict('records')

        return jsonify({
            'status': 'ok',
            'signals': signals,
            'count': len(signals)
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/performance')
def get_performance():
    """Performans metriklerini getir"""
    try:
        # Bu normalde risk manager'dan gelecek
        # Şimdilik örnek veri

        return jsonify({
            'status': 'ok',
            'metrics': {
                'sharpe_ratio': 1.85,
                'sortino_ratio': 2.10,
                'max_drawdown': -5.2,
                'win_rate': 62.5,
                'profit_factor': 1.95,
                'avg_win': 2.8,
                'avg_loss': -1.4,
                'total_trades': 45,
                'winning_trades': 28,
                'losing_trades': 17
            },
            'equity_curve': [
                {'date': '2024-01-01', 'value': 100000},
                {'date': '2024-01-02', 'value': 101200},
                {'date': '2024-01-03', 'value': 102500},
                {'date': '2024-01-04', 'value': 101800},
                {'date': '2024-01-05', 'value': 103500},
            ]
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/positions')
def get_positions():
    """Açık pozisyonları getir - GERÇEK ZAMANLI"""
    try:
        import json

        # Live trading engine'den JSON dosyasını oku
        positions_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'live_positions.json')

        if os.path.exists(positions_file):
            with open(positions_file, 'r', encoding='utf-8') as f:
                positions_data = json.load(f)
        else:
            positions_data = []

        return jsonify({
            'status': 'ok',
            'positions': positions_data
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    """İstatistikleri getir"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        # Sinyal dağılımı
        cursor.execute("""
            SELECT signal, COUNT(*) as count, AVG(score) as avg_score
            FROM signals
            WHERE created_at >= datetime('now', '-24 hours')
            GROUP BY signal
        """)

        signal_distribution = {}
        for row in cursor.fetchall():
            signal_distribution[row[0]] = {
                'count': row[1],
                'avg_score': round(row[2], 1) if row[2] else 0
            }

        # Timeframe dağılımı
        cursor.execute("""
            SELECT timeframe, COUNT(DISTINCT ticker) as ticker_count
            FROM ohlcv_data
            GROUP BY timeframe
        """)

        timeframe_stats = {}
        for row in cursor.fetchall():
            timeframe_stats[row[0]] = row[1]

        conn.close()

        return jsonify({
            'status': 'ok',
            'signal_distribution': signal_distribution,
            'timeframe_stats': timeframe_stats
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def run_dashboard(host='127.0.0.1', port=5000, debug=True):
    """Dashboard'u başlat"""
    print(f"""
    ╔════════════════════════════════════════════════════════════════╗
    ║                 🌐 WEB DASHBOARD BAŞLATILDI                    ║
    ╠════════════════════════════════════════════════════════════════╣
    ║                                                                ║
    ║  📊 Dashboard URL: http://{host}:{port}                    ║
    ║                                                                ║
    ║  🔹 Ana Sayfa:     http://{host}:{port}/                   ║
    ║  🔹 API Portföy:   http://{host}:{port}/api/portfolio     ║
    ║  🔹 API Sinyaller: http://{host}:{port}/api/signals       ║
    ║  🔹 API Performans:http://{host}:{port}/api/performance   ║
    ║                                                                ║
    ║  💡 Tarayıcınızda açmak için Ctrl+Click                       ║
    ║  🛑 Durdurmak için Ctrl+C                                      ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_dashboard()
