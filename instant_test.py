"""
Instant Test Mode - 5 trades immediately for quick testing
No waiting between trades
"""
import time
from datetime import datetime
from exchange.binance_client import BinanceClient
from utils.logger import setup_logger
from utils.trade_manager import TradeManager
import config
import random

logger = setup_logger('InstantTest')

class InstantTestBot:
    """Bot that executes trades instantly"""
    
    def __init__(self):
        self.client = BinanceClient()
        self.symbol = config.TRADE_SYMBOL
        self.quantity = config.TRADE_QUANTITY
        self.trade_manager = TradeManager()
        
        logger.info("⚡ INSTANT TEST MODE")
        logger.info(f"   Symbol: {self.symbol}")
        logger.info(f"   Quantity: {self.quantity}")
    
    def get_current_price(self):
        return self.client.get_current_price(self.symbol)
    
    def execute_trade_pair(self, trade_num):
        """Execute one BUY + SELL pair instantly"""
        try:
            # BUY
            buy_price = self.get_current_price()
            logger.info(f"\n{'='*60}")
            logger.info(f"Trade #{trade_num} - BUY @ ${buy_price:,.2f}")
            
            trade_id = self.trade_manager.open_trade(
                symbol=self.symbol,
                side='BUY',
                quantity=self.quantity,
                entry_price=buy_price,
                order_id=f'TEST_BUY_{int(time.time())}_{trade_num}',
                strategy='INSTANT_TEST'
            )
            
            logger.info(f"✅ BUY completed - Trade ID: {trade_id}")
            
            # Small delay to get different price
            time.sleep(2)
            
            # SELL with simulated price change
            sell_price = self.get_current_price()
            price_variation = random.uniform(-0.003, 0.008)  # -0.3% to +0.8%
            sell_price = sell_price * (1 + price_variation)
            
            profit = (sell_price - buy_price) * self.quantity
            profit_pct = ((sell_price - buy_price) / buy_price) * 100
            
            logger.info(f"🔴 SELL @ ${sell_price:,.2f} | P/L: ${profit:,.4f} ({profit_pct:+.2f}%)")
            
            self.trade_manager.close_trade(
                trade_id=trade_id,
                exit_price=sell_price,
                order_id=f'TEST_SELL_{int(time.time())}_{trade_num}'
            )
            
            emoji = "💰" if profit >= 0 else "📉"
            logger.info(f"{emoji} Trade #{trade_num} completed")
            logger.info(f"{'='*60}")
            
            return profit, profit_pct
            
        except Exception as e:
            logger.error(f"Error in trade: {e}")
            return 0, 0
    
    def run(self, num_trades=5):
        """Execute multiple quick trades"""
        logger.info("\n🚀 Starting INSTANT TEST MODE")
        logger.info(f"📊 Will execute {num_trades} complete trades immediately\n")
        
        start_time = datetime.now()
        total_profit = 0
        profits = []
        
        for i in range(1, num_trades + 1):
            profit, profit_pct = self.execute_trade_pair(i)
            total_profit += profit
            profits.append(profit)
            time.sleep(1)  # Small delay between trades
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Summary
        logger.info(f"\n{'#'*60}")
        logger.info("✅ INSTANT TEST COMPLETED!")
        logger.info(f"{'#'*60}")
        logger.info(f"⏱️  Duration: {duration:.0f} seconds")
        logger.info(f"📊 Total Trades: {num_trades} pairs")
        logger.info(f"💰 Total P/L: ${total_profit:,.4f}")
        logger.info(f"📈 Average P/L: ${(total_profit/num_trades):,.4f}")
        logger.info(f"{'#'*60}")
        logger.info(f"\n🎯 Now check your dashboard:")
        logger.info(f"   ✅ Trade History - {num_trades} closed trades")
        logger.info(f"   ✅ Analytics - P/L breakdown")
        logger.info(f"   ✅ Wallet - Updated balance")
        logger.info(f"\n{'#'*60}\n")
        
        return total_profit

if __name__ == '__main__':
    import sys
    
    # Get number of trades from command line or default to 5
    num_trades = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    
    logger.info(f"🎯 Will execute {num_trades} test trades")
    
    bot = InstantTestBot()
    bot.run(num_trades)
