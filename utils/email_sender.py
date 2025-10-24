"""
Email Notification System - SendGrid / SMTP ile email gönderimi
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging


class EmailSender:
    """Email gönderimi için utility class"""

    def __init__(self):
        # Environment variables'dan ayarları al
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        self.to_emails = os.getenv('TO_EMAILS', '').split(',')  # Comma-separated

        # SendGrid alternatifi (premium)
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY', '')
        self.use_sendgrid = bool(self.sendgrid_api_key)

    def send_daily_report(self, results):
        """
        Günlük pipeline raporu gönder

        Args:
            results: Pipeline execution results dictionary
        """
        subject = f"📊 Trading System Daily Report - {datetime.now().strftime('%Y-%m-%d')}"

        # HTML email body oluştur
        html_body = self._generate_daily_report_html(results)

        # Email gönder
        self._send_email(subject, html_body, is_html=True)

        logging.info('Daily report email sent successfully')

    def send_error_alert(self, error):
        """
        Hata bildirimi gönder

        Args:
            error: Exception object
        """
        subject = f"🚨 Trading System ERROR - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #dc3545;">🚨 System Error Alert</h2>

            <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #721c24; margin-top: 0;">Error Details:</h3>
                <pre style="color: #721c24; white-space: pre-wrap;">{str(error)}</pre>
            </div>

            <p style="color: #666; margin-top: 30px;">
                <em>This is an automated message from Trading System. Please check the logs for more details.</em>
            </p>
        </body>
        </html>
        """

        self._send_email(subject, html_body, is_html=True, priority='high')

        logging.info('Error alert email sent successfully')

    def send_strong_signal_alert(self, signals):
        """
        Güçlü sinyal bildirimi gönder

        Args:
            signals: List of strong signals
        """
        if not signals:
            return

        subject = f"💪 Strong Trading Signals Detected - {len(signals)} signals"

        html_body = self._generate_signal_alert_html(signals)

        self._send_email(subject, html_body, is_html=True, priority='high')

        logging.info(f'Strong signal alert sent for {len(signals)} signals')

    def _generate_daily_report_html(self, results):
        """Günlük rapor HTML'i oluştur"""

        status_emoji = "✅" if results.get('status') == 'completed' else "❌"
        status_color = "#28a745" if results.get('status') == 'completed' else "#dc3545"

        phases = results.get('phases', {})
        data_phase = phases.get('data_collection', {})
        indicator_phase = phases.get('indicator_calculation', {})
        signal_phase = phases.get('signal_generation', {})
        backtest_phase = phases.get('backtest', {})

        # Güçlü sinyaller
        strong_signals = signal_phase.get('strong_signals', [])
        strong_signals_html = ""

        if strong_signals:
            strong_signals_html = "<h3 style='color: #ff9800;'>💪 Strong Signals:</h3><ul>"
            for sig in strong_signals:
                emoji = "🟢" if sig['signal'] == 'BUY' else "🔴"
                strong_signals_html += f"<li>{emoji} <strong>{sig['ticker']}</strong> ({sig['timeframe']}): {sig['signal']} - Score: {sig['score']}/100</li>"
            strong_signals_html += "</ul>"

        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                }}
                .status {{
                    background-color: {status_color};
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    display: inline-block;
                    margin: 10px 0;
                }}
                .phase {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    margin: 15px 0;
                    border-left: 4px solid #667eea;
                    border-radius: 5px;
                }}
                .phase h3 {{
                    margin-top: 0;
                    color: #667eea;
                }}
                .metric {{
                    display: inline-block;
                    margin: 10px 15px 10px 0;
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .metric-label {{
                    font-size: 12px;
                    color: #666;
                    text-transform: uppercase;
                }}
                .footer {{
                    text-align: center;
                    color: #999;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Trading System Daily Report</h1>
                    <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
                    <div class="status">{status_emoji} Pipeline Status: {results.get('status', 'unknown').upper()}</div>
                </div>

                <div class="phase">
                    <h3>📊 Phase 6: Data Collection</h3>
                    <div class="metric">
                        <div class="metric-value">{data_phase.get('total_bars', 0):,}</div>
                        <div class="metric-label">Total Bars</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{data_phase.get('successful_stocks', 0)}/{data_phase.get('total_stocks', 0)}</div>
                        <div class="metric-label">Success Rate</div>
                    </div>
                </div>

                <div class="phase">
                    <h3>📐 Phase 7: Indicator Calculation</h3>
                    <div class="metric">
                        <div class="metric-value">{indicator_phase.get('total_indicators', 0):,}</div>
                        <div class="metric-label">Indicators Calculated</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{indicator_phase.get('successful_calculations', 0)}</div>
                        <div class="metric-label">Successful Calculations</div>
                    </div>
                </div>

                <div class="phase">
                    <h3>🎯 Phase 8: Signal Generation</h3>
                    <div class="metric">
                        <div class="metric-value">{signal_phase.get('total_signals', 0)}</div>
                        <div class="metric-label">Total Signals</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" style="color: #28a745;">{signal_phase.get('buy_signals', 0)}</div>
                        <div class="metric-label">🟢 BUY</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" style="color: #dc3545;">{signal_phase.get('sell_signals', 0)}</div>
                        <div class="metric-label">🔴 SELL</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" style="color: #ffc107;">{signal_phase.get('hold_signals', 0)}</div>
                        <div class="metric-label">🟡 HOLD</div>
                    </div>

                    {strong_signals_html}
                </div>

                <div class="phase">
                    <h3>📈 Phase 9: Backtest Results</h3>
                    <div class="metric">
                        <div class="metric-value">{backtest_phase.get('total_trades', 0)}</div>
                        <div class="metric-label">Total Trades</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{backtest_phase.get('win_rate', 0):.1f}%</div>
                        <div class="metric-label">Win Rate</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{backtest_phase.get('avg_return', 0):.2f}%</div>
                        <div class="metric-label">Avg Return</div>
                    </div>
                </div>

                <div class="footer">
                    <p><em>Generated by Trading System</em></p>
                    <p style="font-size: 11px;">Timestamp: {results.get('timestamp', 'N/A')}</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _generate_signal_alert_html(self, signals):
        """Sinyal alert HTML'i oluştur"""

        signals_html = ""
        for sig in signals:
            emoji = "🟢" if sig['signal'] == 'BUY' else "🔴"
            bg_color = "#d4edda" if sig['signal'] == 'BUY' else "#f8d7da"
            border_color = "#c3e6cb" if sig['signal'] == 'BUY' else "#f5c6cb"

            signals_html += f"""
            <div style="background-color: {bg_color}; border: 1px solid {border_color}; padding: 15px; margin: 10px 0; border-radius: 5px;">
                <h3 style="margin-top: 0;">{emoji} {sig['ticker']} ({sig['timeframe']})</h3>
                <p><strong>Signal:</strong> {sig['signal']}</p>
                <p><strong>Score:</strong> {sig['score']}/100</p>
            </div>
            """

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>💪 Strong Trading Signals Detected!</h2>
            <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>The following strong signals have been generated:</p>

            {signals_html}

            <p style="color: #666; margin-top: 30px;">
                <em>⚠️ This is an automated alert. Please verify signals before trading.</em>
            </p>
        </body>
        </html>
        """

        return html

    def _send_email(self, subject, body, is_html=False, priority='normal'):
        """
        Email gönder (SMTP veya SendGrid)

        Args:
            subject: Email subject
            body: Email body (text or HTML)
            is_html: Is body HTML?
            priority: 'normal' or 'high'
        """
        if not self.to_emails or not self.to_emails[0]:
            logging.warning('No recipient emails configured, skipping email send')
            return

        if self.use_sendgrid:
            self._send_via_sendgrid(subject, body, is_html, priority)
        else:
            self._send_via_smtp(subject, body, is_html, priority)

    def _send_via_smtp(self, subject, body, is_html, priority):
        """SMTP ile email gönder"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)

            if priority == 'high':
                msg['X-Priority'] = '1'
                msg['X-MSMail-Priority'] = 'High'

            # Email body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # SMTP connection
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logging.info(f'Email sent via SMTP to {len(self.to_emails)} recipients')

        except Exception as e:
            logging.error(f'SMTP email sending failed: {str(e)}')
            raise

    def _send_via_sendgrid(self, subject, body, is_html, priority):
        """SendGrid API ile email gönder"""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Email, To, Content

            message = Mail(
                from_email=Email(self.from_email),
                to_emails=[To(email) for email in self.to_emails],
                subject=subject,
                html_content=Content("text/html", body) if is_html else Content("text/plain", body)
            )

            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)

            logging.info(f'Email sent via SendGrid, status code: {response.status_code}')

        except Exception as e:
            logging.error(f'SendGrid email sending failed: {str(e)}')
            raise
