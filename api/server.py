"""
Flask API Server for Trading Bot
Provides REST API endpoints for the frontend
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exchange.binance_client import BinanceClient
from bot.trading_bot import TradingBot
from strategies.rsi_strategy import RSIStrategy
from strategies.ema_crossover_strategy import EMACrossoverStrategy
from strategies.combined_strategy import CombinedStrategy
from utils.trade_manager import TradeManager, ProfitLossAnalyzer
import config

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global instances
client = None
bot = None
price_thread = None
running = False
trade_manager = None
pl_analyzer = None

def init_client():
    global client, trade_manager, pl_analyzer
    try:
        client = BinanceClient()
        trade_manager = TradeManager()
        pl_analyzer = ProfitLossAnalyzer(trade_manager)
        return True
    except Exception as e:
        print(f"Error initializing client: {e}")
        return False

# Initialize on startup
init_client()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/prices', methods=['GET'])
def get_prices():
    """Get current prices for popular cryptos"""
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT', 'ADAUSDT']
    prices = {}
    
    if client:
        for symbol in symbols:
            try:
                price = client.get_current_price(symbol)
                prices[symbol] = {
                    'price': price,
                    'symbol': symbol,
                    'base': symbol.replace('USDT', ''),
                    'quote': 'USDT'
                }
            except:
                prices[symbol] = {'price': 0, 'symbol': symbol}
    
    return jsonify(prices)

@app.route('/api/price/<symbol>', methods=['GET'])
def get_single_price(symbol):
    """Get price for a single symbol"""
    if client:
        price = client.get_current_price(symbol.upper())
        return jsonify({'symbol': symbol.upper(), 'price': price})
    return jsonify({'error': 'Client not initialized'}), 500

@app.route('/api/klines/<symbol>', methods=['GET'])
def get_klines(symbol):
    """Get historical candlestick data"""
    interval = request.args.get('interval', '1h')
    limit = int(request.args.get('limit', 100))
    
    if client:
        df = client.get_historical_klines(symbol.upper(), interval, limit)
        if not df.empty:
            data = df.reset_index().to_dict('records')
            # Convert timestamps to strings
            for item in data:
                item['timestamp'] = item['timestamp'].isoformat()
            return jsonify(data)
    
    return jsonify([])

@app.route('/api/analysis/<symbol>', methods=['GET'])
def get_analysis(symbol):
    """Get technical analysis for a symbol"""
    if not client:
        return jsonify({'error': 'Client not initialized'}), 500
    
    try:
        import ta
        
        df = client.get_historical_klines(symbol.upper(), '1h', 100)
        
        if df.empty:
            return jsonify({'error': 'No data available'}), 404
        
        # Calculate indicators
        df['rsi'] = ta.momentum.RSIIndicator(close=df['close']).rsi()
        df['ema_9'] = ta.trend.EMAIndicator(close=df['close'], window=9).ema_indicator()
        df['ema_21'] = ta.trend.EMAIndicator(close=df['close'], window=21).ema_indicator()
        
        macd = ta.trend.MACD(close=df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        
        bollinger = ta.volatility.BollingerBands(close=df['close'])
        df['bb_upper'] = bollinger.bollinger_hband()
        df['bb_lower'] = bollinger.bollinger_lband()
        df['bb_middle'] = bollinger.bollinger_mavg()
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Determine signal
        signal = 'NEUTRAL'
        signal_strength = 0
        
        if latest['rsi'] < 30:
            signal = 'BUY'
            signal_strength += 2
        elif latest['rsi'] > 70:
            signal = 'SELL'
            signal_strength += 2
        
        if prev['ema_9'] <= prev['ema_21'] and latest['ema_9'] > latest['ema_21']:
            signal = 'BUY'
            signal_strength += 1
        elif prev['ema_9'] >= prev['ema_21'] and latest['ema_9'] < latest['ema_21']:
            signal = 'SELL'
            signal_strength += 1
        
        return jsonify({
            'symbol': symbol.upper(),
            'price': float(latest['close']),
            'rsi': float(latest['rsi']) if not pd.isna(latest['rsi']) else None,
            'ema_9': float(latest['ema_9']) if not pd.isna(latest['ema_9']) else None,
            'ema_21': float(latest['ema_21']) if not pd.isna(latest['ema_21']) else None,
            'macd': float(latest['macd']) if not pd.isna(latest['macd']) else None,
            'macd_signal': float(latest['macd_signal']) if not pd.isna(latest['macd_signal']) else None,
            'bb_upper': float(latest['bb_upper']) if not pd.isna(latest['bb_upper']) else None,
            'bb_lower': float(latest['bb_lower']) if not pd.isna(latest['bb_lower']) else None,
            'bb_middle': float(latest['bb_middle']) if not pd.isna(latest['bb_middle']) else None,
            'signal': signal,
            'signal_strength': signal_strength,
            'trend': 'UP' if latest['ema_9'] > latest['ema_21'] else 'DOWN'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/balance', methods=['GET'])
def get_balance():
    """Get account balances"""
    if client:
        balances = client.get_all_balances()
        return jsonify(balances)
    return jsonify({})

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """Start the trading bot"""
    global bot, running
    
    data = request.json or {}
    symbol = data.get('symbol', config.TRADE_SYMBOL)
    strategy = data.get('strategy', 'combined')
    quantity = float(data.get('quantity', config.TRADE_QUANTITY))
    
    if bot and running:
        return jsonify({'error': 'Bot already running'}), 400
    
    try:
        bot = TradingBot(symbol=symbol, quantity=quantity, strategy=strategy)
        running = True
        
        # Run bot in background thread
        def run_bot():
            global running
            while running:
                try:
                    result = bot.run_once()
                    socketio.emit('bot_update', {
                        'status': 'running',
                        'last_action': result,
                        'in_position': bot.in_position,
                        'entry_price': bot.entry_price,
                        'trades': len(bot.trades)
                    })
                    time.sleep(60)
                except Exception as e:
                    print(f"Bot error: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=run_bot, daemon=True)
        thread.start()
        
        return jsonify({'status': 'started', 'symbol': symbol, 'strategy': strategy})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """Stop the trading bot"""
    global bot, running
    
    running = False
    if bot:
        bot.stop()
        summary = {
            'trades': len(bot.trades),
            'in_position': bot.in_position
        }
        bot = None
        return jsonify({'status': 'stopped', 'summary': summary})
    
    return jsonify({'status': 'not running'})

@app.route('/api/bot/status', methods=['GET'])
def bot_status():
    """Get bot status"""
    global bot, running
    
    if bot and running:
        return jsonify({
            'running': True,
            'symbol': bot.symbol,
            'strategy': bot.strategy.name,
            'in_position': bot.in_position,
            'entry_price': bot.entry_price,
            'trades': len(bot.trades),
            'trade_history': bot.trades[-10:]  # Last 10 trades
        })
    
    return jsonify({'running': False})

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify({
        'trade_symbol': config.TRADE_SYMBOL,
        'trade_quantity': config.TRADE_QUANTITY,
        'use_testnet': config.USE_TESTNET,
        'stop_loss_percent': config.STOP_LOSS_PERCENT,
        'take_profit_percent': config.TAKE_PROFIT_PERCENT,
        'rsi_period': config.RSI_PERIOD,
        'rsi_overbought': config.RSI_OVERBOUGHT,
        'rsi_oversold': config.RSI_OVERSOLD,
        'ema_short': config.EMA_SHORT_PERIOD,
        'ema_long': config.EMA_LONG_PERIOD
    })

# ==================== TRADE HISTORY & ANALYTICS ====================

@app.route('/api/trades', methods=['GET'])
def get_all_trades():
    """Get all trades (open and closed)"""
    global trade_manager
    if not trade_manager:
        return jsonify({'error': 'Trade manager not initialized'}), 500
    
    status_filter = request.args.get('status', None)  # 'open', 'closed', or None for all
    limit = int(request.args.get('limit', 50))
    
    if status_filter == 'open':
        trades = trade_manager.get_open_trades()
    elif status_filter == 'closed':
        trades = trade_manager.get_closed_trades()
    else:
        trades = trade_manager.get_all_trades()
    
    # Sort by entry time descending (most recent first)
    trades_sorted = sorted(trades, key=lambda t: t.entry_time, reverse=True)[:limit]
    
    return jsonify({
        'total': len(trades),
        'trades': [t.to_dict() for t in trades_sorted]
    })

@app.route('/api/trades/open', methods=['GET'])
def get_open_trades():
    """Get all currently open/running trades"""
    global trade_manager, client
    if not trade_manager:
        return jsonify({'error': 'Trade manager not initialized'}), 500
    
    open_trades = trade_manager.get_open_trades()
    trades_with_current = []
    
    for trade in open_trades:
        trade_dict = trade.to_dict()
        # Get current price and calculate unrealized P&L
        if client:
            try:
                current_price = client.get_current_price(trade.symbol)
                trade_dict['current_price'] = current_price
                
                if trade.side == "BUY":
                    unrealized_pl = (current_price - trade.entry_price) * trade.quantity
                    unrealized_pl_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
                else:
                    unrealized_pl = (trade.entry_price - current_price) * trade.quantity
                    unrealized_pl_pct = ((trade.entry_price - current_price) / trade.entry_price) * 100
                
                trade_dict['unrealized_pl'] = round(unrealized_pl, 2)
                trade_dict['unrealized_pl_pct'] = round(unrealized_pl_pct, 2)
            except:
                pass
        
        trades_with_current.append(trade_dict)
    
    return jsonify({
        'count': len(trades_with_current),
        'trades': trades_with_current
    })

@app.route('/api/trades/closed', methods=['GET'])
def get_closed_trades():
    """Get all closed trades with P&L"""
    global trade_manager
    if not trade_manager:
        return jsonify({'error': 'Trade manager not initialized'}), 500
    
    limit = int(request.args.get('limit', 50))
    closed_trades = trade_manager.get_closed_trades()
    
    # Sort by exit time descending
    trades_sorted = sorted(closed_trades, key=lambda t: t.exit_time or '', reverse=True)[:limit]
    
    return jsonify({
        'total': len(closed_trades),
        'trades': [t.to_dict() for t in trades_sorted]
    })

@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get comprehensive P&L analytics summary"""
    global pl_analyzer
    if not pl_analyzer:
        return jsonify({'error': 'Analyzer not initialized'}), 500
    
    return jsonify(pl_analyzer.get_summary())

@app.route('/api/analytics/hourly', methods=['GET'])
def get_hourly_analytics():
    """Get hourly P&L stats"""
    global pl_analyzer
    if not pl_analyzer:
        return jsonify({'error': 'Analyzer not initialized'}), 500
    
    hours = int(request.args.get('hours', 1))
    return jsonify(pl_analyzer.get_hourly_stats(hours))

@app.route('/api/analytics/daily', methods=['GET'])
def get_daily_analytics():
    """Get daily P&L stats"""
    global pl_analyzer
    if not pl_analyzer:
        return jsonify({'error': 'Analyzer not initialized'}), 500
    
    days = int(request.args.get('days', 1))
    return jsonify(pl_analyzer.get_daily_stats(days))

@app.route('/api/analytics/weekly', methods=['GET'])
def get_weekly_analytics():
    """Get weekly P&L stats"""
    global pl_analyzer
    if not pl_analyzer:
        return jsonify({'error': 'Analyzer not initialized'}), 500
    
    weeks = int(request.args.get('weeks', 1))
    return jsonify(pl_analyzer.get_weekly_stats(weeks))

@app.route('/api/analytics/monthly', methods=['GET'])
def get_monthly_analytics():
    """Get monthly P&L stats"""
    global pl_analyzer
    if not pl_analyzer:
        return jsonify({'error': 'Analyzer not initialized'}), 500
    
    months = int(request.args.get('months', 1))
    return jsonify(pl_analyzer.get_monthly_stats(months))

@app.route('/api/analytics/breakdown', methods=['GET'])
def get_daily_breakdown():
    """Get day-by-day breakdown"""
    global pl_analyzer
    if not pl_analyzer:
        return jsonify({'error': 'Analyzer not initialized'}), 500
    
    days = int(request.args.get('days', 7))
    return jsonify({
        'breakdown': pl_analyzer.get_daily_breakdown(days)
    })

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'status': 'ok'})

@socketio.on('subscribe_prices')
def handle_subscribe_prices(data):
    """Subscribe to price updates"""
    symbols = data.get('symbols', ['BTCUSDT', 'ETHUSDT'])
    
    def send_prices():
        while True:
            prices = {}
            for symbol in symbols:
                if client:
                    price = client.get_current_price(symbol)
                    prices[symbol] = price
            emit('price_update', prices)
            time.sleep(5)
    
    thread = threading.Thread(target=send_prices, daemon=True)
    thread.start()

# Import pandas for analysis endpoint
import pandas as pd

if __name__ == '__main__':
    print("🚀 Starting API Server on http://localhost:5001")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
