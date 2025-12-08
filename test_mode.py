"""
Quick Test Mode - Forces trades every 1 minute for testing
WARNING: Only for testing! Not for real trading!
"""
import time
from datetime import datetime
from exchange.binance_client import BinanceClient
from utils.logger import setup_logger
from utils.trade_manager import TradeManager
import config

logger = setup_logger('TestMode')

class QuickTestBot:
    """Bot that alternates BUY/SELL every minute for testing"""
    
    def __init__(self):
        self.client = BinanceClient()
        self.symbol = config.TRADE_SYMBOL
        self.quantity = config.TRADE_QUANTITY
        self.trade_manager = TradeManager()
        self.in_position = False
        self.entry_price = 0.0
        self.current_trade_id = None
        self.trade_count = 0
        
        logger.info("🧪 QUICK TEST MODE - Will trade every 1 minute!")
        logger.info(f"   Symbol: {self.symbol}")
        logger.info(f"   Quantity: {self.quantity}")
        logger.warning("⚠️ This is TEST MODE only! Not for real trading!")
    
    def get_current_price(self):
        """Get current price"""
        return self.client.get_current_price(self.symbol)
    
    def execute_test_buy(self):
        """Execute a test buy"""
        try:
            current_price = self.get_current_price()
            
            logger.info(f"🟢 TEST BUY @ ${current_price:,.2f}")
            
            # Create simulated order
            order = {
                'orderId': f'TEST_{int(time.time())}',
                'symbol': self.symbol,
                'price': current_price,
                'executedQty': self.quantity,
                'status': 'FILLED'
            }
            
            # Record trade
            self.current_trade_id = self.trade_manager.open_trade(
                symbol=self.symbol,
                side='BUY',
                quantity=self.quantity,
                entry_price=current_price,
                order_id=str(order['orderId']),
                strategy='TEST_MODE'
            )
            
            self.entry_price = current_price
            self.in_position = True
            self.trade_count += 1
            
            logger.info(f"✅ TEST BUY completed - Trade ID: {self.current_trade_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error in test buy: {e}")
            return False
    
    def execute_test_sell(self):
        """Execute a test sell"""
        try:
            current_price = self.get_current_price()
            
            # Calculate P&L
            profit_loss = (current_price - self.entry_price) * self.quantity
            profit_pct = ((current_price - self.entry_price) / self.entry_price) * 100
            
            logger.info(f"🔴 TEST SELL @ ${current_price:,.2f}")
            logger.info(f"   P/L: ${profit_loss:,.2f} ({profit_pct:+.2f}%)")
            
            # Create simulated order
            order = {
                'orderId': f'TEST_{int(time.time())}',
                'symbol': self.symbol,
                'price': current_price,
                'executedQty': self.quantity,
                'status': 'FILLED'
            }
            
            # Close trade
            if self.current_trade_id:
                self.trade_manager.close_trade(
                    trade_id=self.current_trade_id,
                    exit_price=current_price,
                    order_id=str(order['orderId'])
                )
            
            emoji = "💰" if profit_loss >= 0 else "📉"
            logger.info(f"{emoji} TEST SELL completed")
            
            self.in_position = False
            self.entry_price = 0.0
            self.current_trade_id = None
            self.trade_count += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Error in test sell: {e}")
            return False
    
    def run(self):
        """Run test bot - alternates BUY/SELL every minute"""
        logger.info("🚀 Starting QUICK TEST MODE")
        logger.info("📊 Will alternate BUY/SELL every 60 seconds")
        logger.info("⏰ Press Ctrl+C to stop\n")
        
        iteration = 0
        
        try:
            while True:
                iteration += 1
                current_price = self.get_current_price()
                
                logger.info(f"{'='*60}")
                logger.info(f"Iteration #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
                logger.info(f"💵 Current Price: ${current_price:,.2f}")
                logger.info(f"📊 Total Trades: {self.trade_count}")
                
                # Alternate between BUY and SELL
                if not self.in_position:
                    logger.info("🎯 Action: BUY")
                    self.execute_test_buy()
                else:
                    logger.info("🎯 Action: SELL")
                    self.execute_test_sell()
                
                logger.info(f"⏳ Waiting 60 seconds for next trade...")
                logger.info(f"{'='*60}\n")
                
                time.sleep(60)  # Wait 1 minute
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Test mode stopped by user")
            logger.info(f"📊 Total trades executed: {self.trade_count}")
            
            # Close any open position
            if self.in_position:
                logger.info("🔄 Closing open position...")
                self.execute_test_sell()

if __name__ == '__main__':
    bot = QuickTestBot()
    bot.run()
