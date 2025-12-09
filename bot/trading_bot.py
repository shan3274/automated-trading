"""
Main Trading Bot - Orchestrates the entire trading process
"""
import time
from datetime import datetime
from typing import Optional
import config
from exchange.binance_client import BinanceClient
from strategies.base_strategy import BaseStrategy, Signal
from strategies.rsi_strategy import RSIStrategy
from strategies.ema_crossover_strategy import EMACrossoverStrategy
from strategies.combined_strategy import CombinedStrategy
from strategies.one_minute_strategy import OneMinuteStrategy
from strategies.momentum_pulse_strategy import MomentumPulseStrategy
from strategies.mtf_impulse_strategy import MTFImpulseStrategy
from utils.logger import setup_logger
from utils.trade_manager import TradeManager

logger = setup_logger('TradingBot')

class TradingBot:
    """Main trading bot class"""
    
    def __init__(
        self,
        symbol: str = None,
        quantity: float = None,
        strategy: str = 'combined',
        interval: str = '1h'
    ):
        self.symbol = symbol or config.TRADE_SYMBOL
        self.quantity = quantity or config.TRADE_QUANTITY
        self.client = BinanceClient()
        self.running = False
        self.strategy_name = strategy.lower()
        self.interval = interval  # Timeframe for candles
        
        # Select strategy
        self.strategy = self._get_strategy(self.strategy_name)

        # Pulse / MTF strategies work best on lower timeframe; default to 5m if not provided
        if self.strategy_name in ['pulse', 'momentum', 'mtf', 'mtfpulse', 'mtf-pulse'] and interval == '1h':
            self.interval = '5m'
        
        # Trade tracking with persistent storage
        self.trade_manager = TradeManager()
        self.trades = []
        self.entry_price = 0.0
        self.in_position = False
        self.current_trade_id = None
        
        # Check for existing open trade
        open_trade = self.trade_manager.get_running_trade(self.symbol)
        if open_trade:
            self.in_position = True
            self.entry_price = open_trade.entry_price
            self.current_trade_id = open_trade.id
            logger.info(f"📌 Resuming open trade: {open_trade.id} @ ${open_trade.entry_price:,.2f}")
        
        logger.info(f"🤖 Trading Bot initialized")
        logger.info(f"   Symbol: {self.symbol}")
        logger.info(f"   Quantity: {self.quantity}")
        logger.info(f"   Strategy: {self.strategy.name}")
        logger.info(f"   Timeframe: {self.interval}")
    
    def _get_strategy(self, strategy_name: str) -> BaseStrategy:
        """Get strategy instance by name"""
        strategies = {
            'rsi': RSIStrategy(),
            'ema': EMACrossoverStrategy(),
            'combined': CombinedStrategy(),
            '1min': OneMinuteStrategy(),
            'pulse': MomentumPulseStrategy(),
            'momentum': MomentumPulseStrategy(),
            'mtf': MTFImpulseStrategy(),
            'mtfpulse': MTFImpulseStrategy(),
            'mtf-pulse': MTFImpulseStrategy()
        }
        return strategies.get(strategy_name.lower(), CombinedStrategy())
    
    def check_balance(self) -> dict:
        """Check and display account balance"""
        balances = self.client.get_all_balances()
        logger.info("💰 Account Balances:")
        for asset, balance in balances.items():
            if balance['total'] > 0:
                logger.info(f"   {asset}: {balance['total']:.8f}")
        return balances
    
    def get_current_price(self) -> float:
        """Get current price of trading symbol"""
        return self.client.get_current_price(self.symbol)
    
    def execute_buy(self) -> bool:
        """Execute a buy order"""
        try:
            current_price = self.get_current_price()
            
            # Check if we have enough balance
            base_asset = self.symbol.replace('USDT', '').replace('BTC', '')
            quote_asset = 'USDT' if 'USDT' in self.symbol else 'BTC'
            
            quote_balance = self.client.get_account_balance(quote_asset)
            required_amount = self.quantity * current_price
            
            if quote_balance < required_amount:
                logger.warning(f"⚠️ Insufficient balance. Need {required_amount:.2f} {quote_asset}, "
                             f"have {quote_balance:.2f}")
                return False
            
            # Place market buy order
            order = self.client.place_market_buy(self.symbol, self.quantity)
            
            if order:
                self.in_position = True
                self.entry_price = current_price
                self.strategy.update_position('LONG', current_price)
                
                # Save to persistent trade manager
                # Pre-calc TP/SL levels based on config
                take_profit = current_price * (1 + config.TAKE_PROFIT_PERCENT / 100)
                stop_loss = current_price * (1 - config.STOP_LOSS_PERCENT / 100)

                new_trade = self.trade_manager.open_trade(
                    symbol=self.symbol,
                    side='BUY',
                    quantity=self.quantity,
                    entry_price=current_price,
                    order_id=str(order.get('orderId')),
                    strategy=self.strategy.name,
                    take_profit=take_profit,
                    stop_loss=stop_loss
                )
                self.current_trade_id = new_trade.id
                
                trade = {
                    'type': 'BUY',
                    'symbol': self.symbol,
                    'quantity': self.quantity,
                    'price': current_price,
                    'timestamp': datetime.now(),
                    'order_id': order.get('orderId'),
                    'trade_id': new_trade.id
                }
                self.trades.append(trade)
                
                logger.info(f"📈 Bought {self.quantity} {self.symbol} @ ${current_price:,.2f}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error executing buy: {e}")
            return False
    
    def execute_sell(self) -> bool:
        """Execute a sell order"""
        try:
            current_price = self.get_current_price()
            
            # Place market sell order
            order = self.client.place_market_sell(self.symbol, self.quantity)
            
            if order:
                profit_loss = (current_price - self.entry_price) * self.quantity
                profit_pct = ((current_price - self.entry_price) / self.entry_price) * 100
                
                self.in_position = False
                self.strategy.clear_position()
                
                # Close trade in persistent storage
                if self.current_trade_id:
                    self.trade_manager.close_trade(
                        trade_id=self.current_trade_id,
                        exit_price=current_price,
                        order_id=str(order.get('orderId'))
                    )
                
                trade = {
                    'type': 'SELL',
                    'symbol': self.symbol,
                    'quantity': self.quantity,
                    'price': current_price,
                    'timestamp': datetime.now(),
                    'order_id': order.get('orderId'),
                    'profit_loss': profit_loss,
                    'profit_pct': profit_pct,
                    'trade_id': self.current_trade_id
                }
                self.trades.append(trade)
                self.current_trade_id = None
                
                emoji = "💰" if profit_loss >= 0 else "📉"
                logger.info(f"{emoji} Sold {self.quantity} {self.symbol} @ ${current_price:,.2f}")
                logger.info(f"   P/L: ${profit_loss:,.2f} ({profit_pct:+.2f}%)")
                
                self.entry_price = 0.0
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error executing sell: {e}")
            return False
    
    def check_stop_loss_take_profit(self, current_price: float) -> Optional[str]:
        """Check if stop loss or take profit is triggered"""
        if not self.in_position:
            return None
        
        price_change_pct = ((current_price - self.entry_price) / self.entry_price) * 100
        
        # Stop Loss
        if price_change_pct <= -config.STOP_LOSS_PERCENT:
            logger.warning(f"⚠️ STOP LOSS triggered at {price_change_pct:.2f}%")
            return 'STOP_LOSS'
        
        # Take Profit
        if price_change_pct >= config.TAKE_PROFIT_PERCENT:
            logger.info(f"🎯 TAKE PROFIT triggered at {price_change_pct:.2f}%")
            return 'TAKE_PROFIT'
        
        return None
    
    def run_once(self) -> Optional[str]:
        """Run one iteration of the trading logic"""
        try:
            # Get current price
            current_price = self.get_current_price()
            logger.info(f"💵 {self.symbol}: ${current_price:,.2f}")
            
            # Check stop loss / take profit first
            if self.in_position:
                sl_tp = self.check_stop_loss_take_profit(current_price)
                if sl_tp:
                    self.execute_sell()
                    return sl_tp
            # Get historical data for strategy
            if getattr(self.strategy, 'requires_multi_tf', False):
                htf_interval = getattr(self.strategy, 'htf_interval', '1h')
                ltf_interval = getattr(self.strategy, 'ltf_interval', '5m')
                htf_limit = 150 if htf_interval.endswith('h') else 200
                ltf_limit = 120 if ltf_interval.endswith('m') else 100

                df_htf = self.client.get_historical_klines(
                    self.symbol,
                    interval=htf_interval,
                    limit=htf_limit
                )

                df_ltf = self.client.get_historical_klines(
                    self.symbol,
                    interval=ltf_interval,
                    limit=ltf_limit
                )

                if df_htf.empty or df_ltf.empty:
                    logger.warning("No historical data available (multi-TF)")
                    return None

                signal = self.strategy.generate_signal({'htf': df_htf, 'ltf': df_ltf})
            else:
                # Use 1m candles for 1min strategy, otherwise configured interval
                interval = '1m' if isinstance(self.strategy, OneMinuteStrategy) else self.interval
                limit = 100 if interval == '1h' else 50  # Less data for 1m
                
                df = self.client.get_historical_klines(
                    self.symbol,
                    interval=interval,
                    limit=limit
                )
                
                if df.empty:
                    logger.warning("No historical data available")
                    return None
                
                # Generate trading signal
                signal = self.strategy.generate_signal(df)
            
            # Log signal analysis
            if signal == Signal.BUY:
                logger.info("📊 Signal: BUY 🟢")
            elif signal == Signal.SELL:
                logger.info("📊 Signal: SELL 🔴")
            else:
                logger.info("📊 Signal: HOLD ⏸️")
            
            # Execute based on signal
            if signal == Signal.BUY and not self.in_position:
                self.execute_buy()
                return 'BUY'
            elif signal == Signal.SELL and self.in_position:
                self.execute_sell()
                return 'SELL'
            
            return 'HOLD'
            
        except Exception as e:
            logger.error(f"Error in run_once: {e}")
            return None
    
    def run(self, interval_seconds: int = 60):
        """Run the bot continuously"""
        self.running = True
        logger.info(f"🚀 Starting bot - checking every {interval_seconds} seconds")
        
        # Initial balance check
        self.check_balance()
        
        while self.running:
            try:
                self.run_once()
                
                # Wait for next iteration
                logger.debug(f"Sleeping for {interval_seconds} seconds...")
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                self.stop()
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(10)  # Wait before retrying
    
    def close_all_positions(self):
        """Close all open positions before shutdown"""
        if self.in_position:
            logger.warning("🔴 Closing open position before shutdown...")
            try:
                self.execute_sell()
                logger.info("✅ Position closed successfully")
            except Exception as e:
                logger.error(f"❌ Failed to close position: {e}")
        else:
            logger.info("✅ No open positions to close")
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        logger.info("🛑 Stopping bot...")
        
        # Close all open positions first
        self.close_all_positions()
        
        logger.info("🛑 Bot stopped")
        self.print_summary()
    
    def print_summary(self):
        """Print trading summary"""
        if not self.trades:
            logger.info("No trades executed")
            return
        
        logger.info("\n" + "="*50)
        logger.info("📊 TRADING SUMMARY")
        logger.info("="*50)
        
        total_profit = 0
        wins = 0
        losses = 0
        
        for trade in self.trades:
            if trade['type'] == 'SELL':
                pl = trade.get('profit_loss', 0)
                total_profit += pl
                if pl >= 0:
                    wins += 1
                else:
                    losses += 1
        
        logger.info(f"Total Trades: {len(self.trades)}")
        logger.info(f"Wins: {wins}, Losses: {losses}")
        logger.info(f"Win Rate: {(wins/(wins+losses)*100) if (wins+losses) > 0 else 0:.1f}%")
        logger.info(f"Total P/L: ${total_profit:,.2f}")
        logger.info("="*50 + "\n")
