#!/usr/bin/env python3
"""
Dashboard Launcher - Web-based monitoring interface başlatıcı
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard.app import run_dashboard
import argparse


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description='Live Trading Dashboard')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                       help='Host address (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port number (default: 5000)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')

    args = parser.parse_args()

    # Dashboard'u başlat
    run_dashboard(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
