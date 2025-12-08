"""
Super Fast Test Mode - 5 trades in 5 minutes (1 trade per minute)
For quick testing of trade history, analytics, etc.
"""
import time
from datetime import datetime
from exchange.binance_client import BinanceClient
from utils.logger import setup_logger
from utils.trade_manager import TradeManager
import config
import random

logger = setup_logger('FastTest')

class FastTestBot:
    """Bot that executes 5 trades quickly for testing"""
    
    def __init__(self):
        self.client = BinanceClient()
        self.symbol = config.TRADE_SYMBOL
        self.quantity = config.TRADE_QUANTITY
        self.trade_manager = TradeManager()
        
        logger.info("⚡ FAST TEST MODE - 5 Trades in 5 Minutes!")
        logger.info(f"   Symbol: {self.symbol}")
        logger.info(f"   Quantity: {self.quantity}")
    
    def get_current_price(self):
        return self.client.get_current_price(self.symbol)
    
    def execute_trade_pair(self, trade_num):
        """Execute one BUY + SELL pair"""
        try:
            # BUY
            buy_price = self.get_current_price()
            logger.info(f"\n{'='*60}")
            logger.info(f"Trade #{trade_num} - BUY")
            logger.info(f"{'='*60}")
            logger.info(f"🟢 Buying @ ${buy_price:,.2f}")
            
            trade_id = self.trade_manager.open_trade(
                symbol=self.symbol,
                side='BUY',
                quantity=self.quantity,
                entry_price=buy_price,
                order_id=f'TEST_BUY_{int(time.time())}',
                strategy='FAST_TEST'
            )
            
            logger.info(f"✅ BUY completed - Trade ID: {trade_id}")
            logger.info(f"⏳ Waiting 30 seconds before SELL...")
            time.sleep(30)
            
            # SELL
            sell_price = self.get_current_price()
            # Add some random variation to make it interesting
            price_variation = random.uniform(-0.005, 0.015)  # -0.5% to +1.5%
            sell_price = sell_price * (1 + price_variation)
            
            profit = (sell_price - buy_price) * self.quantity
            profit_pct = ((sell_price - buy_price) / buy_price) * 100
            
            logger.info(f"\n🔴 Selling @ ${sell_price:,.2f}")
            logger.info(f"💰 P/L: ${profit:,.2f} ({profit_pct:+.2f}%)")
            
            self.trade_manager.close_trade(
                trade_id=trade_id,
                exit_price=sell_price,
                order_id=f'TEST_SELL_{int(time.time())}'
            )
            
            emoji = "✅" if profit >= 0 else "❌"
            logger.info(f"{emoji} SELL completed")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in trade: {e}")
            return False
    
    def run(self):
        """Execute 5 quick trades"""
        logger.info("\n🚀 Starting FAST TEST MODE")
        logger.info("📊 Will execute 5 complete trades (BUY + SELL pairs)")
        logger.info("⏰ Each trade takes ~1 minute\n")
        
        start_time = datetime.now()
        
        for i in range(1, 6):  # 5 trades
            logger.info(f"\n{'#'*60}")
            logger.info(f"TRADE PAIR {i}/5")
            logger.info(f"{'#'*60}")
            
            success = self.execute_trade_pair(i)
            
            if success and i < 5:
                logger.info(f"\n⏳ Waiting 30 seconds before next trade...\n")
                time.sleep(30)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ FAST TEST COMPLETED!")
        logger.info(f"{'='*60}")
        logger.info(f"⏱️  Duration: {duration:.0f} seconds")
        logger.info(f"📊 Total Trades: 5 pairs (10 orders)")
        logger.info(f"🎯 Check your dashboard for:")
        logger.info(f"   - Trade History (closed trades)")
        logger.info(f"   - Analytics (P&L summary)")
        logger.info(f"   - Wallet (balance)")
        logger.info(f"{'='*60}\n")

if __name__ == '__main__':
    bot = FastTestBot()
    bot.run()
