"""
Binance Exchange Client - Handles all API interactions
"""
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
from typing import Optional, Dict, List
import config
from utils.logger import setup_logger

logger = setup_logger('BinanceClient')

class BinanceClient:
    """Wrapper class for Binance API interactions"""
    
    def __init__(self):
        """Initialize the Binance client"""
        self.api_key = config.BINANCE_API_KEY
        self.api_secret = config.BINANCE_API_SECRET
        
        if config.USE_TESTNET:
            self.client = Client(
                self.api_key, 
                self.api_secret,
                testnet=True
            )
            logger.info("🧪 Connected to Binance TESTNET")
        else:
            self.client = Client(self.api_key, self.api_secret)
            logger.info("🔴 Connected to Binance LIVE")
    
    def get_account_balance(self, asset: str = 'USDT') -> float:
        """Get balance for a specific asset"""
        try:
            account = self.client.get_account()
            for balance in account['balances']:
                if balance['asset'] == asset:
                    return float(balance['free'])
            return 0.0
        except BinanceAPIException as e:
            logger.error(f"Error getting balance: {e}")
            return 0.0
    
    def get_all_balances(self) -> Dict[str, float]:
        """Get all non-zero balances"""
        try:
            account = self.client.get_account()
            balances = {}
            for balance in account['balances']:
                free = float(balance['free'])
                locked = float(balance['locked'])
                if free > 0 or locked > 0:
                    balances[balance['asset']] = {
                        'free': free,
                        'locked': locked,
                        'total': free + locked
                    }
            return balances
        except BinanceAPIException as e:
            logger.error(f"Error getting balances: {e}")
            return {}
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return 0.0
    
    def get_historical_klines(
        self, 
        symbol: str, 
        interval: str = '1h',
        limit: int = 100
    ) -> pd.DataFrame:
        """Get historical candlestick data"""
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert to proper types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            df.set_index('timestamp', inplace=True)
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except BinanceAPIException as e:
            logger.error(f"Error getting klines: {e}")
            return pd.DataFrame()
    
    def place_market_buy(self, symbol: str, quantity: float) -> Optional[Dict]:
        """Place a market buy order"""
        try:
            order = self.client.order_market_buy(
                symbol=symbol,
                quantity=quantity
            )
            logger.info(f"✅ BUY Order placed: {quantity} {symbol}")
            return order
        except BinanceAPIException as e:
            logger.error(f"Error placing buy order: {e}")
            return None
    
    def place_market_sell(self, symbol: str, quantity: float) -> Optional[Dict]:
        """Place a market sell order"""
        try:
            order = self.client.order_market_sell(
                symbol=symbol,
                quantity=quantity
            )
            logger.info(f"✅ SELL Order placed: {quantity} {symbol}")
            return order
        except BinanceAPIException as e:
            logger.error(f"Error placing sell order: {e}")
            return None
    
    def place_limit_buy(
        self, 
        symbol: str, 
        quantity: float, 
        price: float
    ) -> Optional[Dict]:
        """Place a limit buy order"""
        try:
            order = self.client.order_limit_buy(
                symbol=symbol,
                quantity=quantity,
                price=str(price)
            )
            logger.info(f"✅ LIMIT BUY Order placed: {quantity} {symbol} @ {price}")
            return order
        except BinanceAPIException as e:
            logger.error(f"Error placing limit buy order: {e}")
            return None
    
    def place_limit_sell(
        self, 
        symbol: str, 
        quantity: float, 
        price: float
    ) -> Optional[Dict]:
        """Place a limit sell order"""
        try:
            order = self.client.order_limit_sell(
                symbol=symbol,
                quantity=quantity,
                price=str(price)
            )
            logger.info(f"✅ LIMIT SELL Order placed: {quantity} {symbol} @ {price}")
            return order
        except BinanceAPIException as e:
            logger.error(f"Error placing limit sell order: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """Cancel an existing order"""
        try:
            self.client.cancel_order(symbol=symbol, orderId=order_id)
            logger.info(f"❌ Order {order_id} cancelled")
            return True
        except BinanceAPIException as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """Get all open orders"""
        try:
            if symbol:
                return self.client.get_open_orders(symbol=symbol)
            return self.client.get_open_orders()
        except BinanceAPIException as e:
            logger.error(f"Error getting open orders: {e}")
            return []
    
    def get_order_status(self, symbol: str, order_id: int) -> Optional[Dict]:
        """Get status of a specific order"""
        try:
            return self.client.get_order(symbol=symbol, orderId=order_id)
        except BinanceAPIException as e:
            logger.error(f"Error getting order status: {e}")
            return None
