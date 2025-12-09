"""
Trade Manager - Persistent storage and analysis for trade history
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TradeStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class Trade:
    """Represents a single trade"""
    id: str
    symbol: str
    side: str  # BUY or SELL
    quantity: float
    entry_price: float
    entry_time: str
    exit_price: Optional[float] = None
    exit_time: Optional[str] = None
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    status: str = "open"
    order_id: Optional[str] = None
    strategy: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Trade':
        defaults = {
            'exit_price': None,
            'exit_time': None,
            'profit_loss': None,
            'profit_loss_pct': None,
            'take_profit': None,
            'stop_loss': None,
            'order_id': None,
            'strategy': None,
        }
        merged = {**defaults, **data}
        return cls(**merged)


class TradeManager:
    """Manages trade history with persistent storage"""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'trades.json'
        )
        self.trades: List[Trade] = []
        self._ensure_storage_dir()
        self._load_trades()
    
    def _ensure_storage_dir(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
    
    def _load_trades(self):
        """Load trades from JSON file"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.trades = [Trade.from_dict(t) for t in data]
            except Exception as e:
                print(f"Error loading trades: {e}")
                self.trades = []
        else:
            self.trades = []
    
    def _save_trades(self):
        """Save trades to JSON file"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump([t.to_dict() for t in self.trades], f, indent=2)
        except Exception as e:
            print(f"Error saving trades: {e}")
    
    def _generate_trade_id(self) -> str:
        """Generate unique trade ID"""
        return f"TRD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.trades) + 1}"
    
    def open_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        entry_price: float,
        order_id: str = None,
        strategy: str = None,
        take_profit: float = None,
        stop_loss: float = None
    ) -> Trade:
        """Open a new trade"""
        trade = Trade(
            id=self._generate_trade_id(),
            symbol=symbol,
            side=side,
            quantity=quantity,
            entry_price=entry_price,
            entry_time=datetime.now().isoformat(),
            order_id=order_id,
            strategy=strategy,
            take_profit=take_profit,
            stop_loss=stop_loss,
            status=TradeStatus.OPEN.value
        )
        self.trades.append(trade)
        self._save_trades()
        return trade
    
    def close_trade(
        self,
        trade_id: str,
        exit_price: float,
        order_id: str = None
    ) -> Optional[Trade]:
        """Close an existing trade"""
        for trade in self.trades:
            if trade.id == trade_id and trade.status == TradeStatus.OPEN.value:
                trade.exit_price = exit_price
                trade.exit_time = datetime.now().isoformat()
                trade.status = TradeStatus.CLOSED.value
                
                # Calculate P&L
                if trade.side == "BUY":
                    trade.profit_loss = (exit_price - trade.entry_price) * trade.quantity
                    trade.profit_loss_pct = ((exit_price - trade.entry_price) / trade.entry_price) * 100
                else:  # SHORT
                    trade.profit_loss = (trade.entry_price - exit_price) * trade.quantity
                    trade.profit_loss_pct = ((trade.entry_price - exit_price) / trade.entry_price) * 100
                
                self._save_trades()
                return trade
        return None
    
    def get_open_trades(self) -> List[Trade]:
        """Get all open trades"""
        self._load_trades()  # Reload to get latest trades from file
        return [t for t in self.trades if t.status == TradeStatus.OPEN.value]
    
    def get_closed_trades(self) -> List[Trade]:
        """Get all closed trades"""
        self._load_trades()  # Reload to get latest trades from file
        return [t for t in self.trades if t.status == TradeStatus.CLOSED.value]
    
    def get_all_trades(self) -> List[Trade]:
        """Get all trades"""
        self._load_trades()  # Reload to get latest trades from file
        return self.trades
    
    def get_running_trade(self, symbol: str = None) -> Optional[Trade]:
        """Get currently running trade for a symbol"""
        open_trades = self.get_open_trades()
        if symbol:
            for trade in open_trades:
                if trade.symbol == symbol:
                    return trade
        return open_trades[0] if open_trades else None
    
    def get_trade_by_id(self, trade_id: str) -> Optional[Trade]:
        """Get trade by ID"""
        self._load_trades()  # Reload to get latest trades from file
        for trade in self.trades:
            if trade.id == trade_id:
                return trade
        return None


class ProfitLossAnalyzer:
    """Analyzes profit/loss over different time periods"""
    
    def __init__(self, trade_manager: TradeManager):
        self.trade_manager = trade_manager
    
    def _filter_trades_by_period(
        self,
        trades: List[Trade],
        start_time: datetime,
        end_time: datetime = None
    ) -> List[Trade]:
        """Filter closed trades by time period"""
        end_time = end_time or datetime.now()
        filtered = []
        
        for trade in trades:
            if trade.exit_time:
                exit_dt = datetime.fromisoformat(trade.exit_time)
                if start_time <= exit_dt <= end_time:
                    filtered.append(trade)
        
        return filtered
    
    def _calculate_stats(self, trades: List[Trade]) -> Dict:
        """Calculate statistics for a list of trades"""
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_profit_loss': 0.0,
                'total_profit_loss_pct': 0.0,
                'win_rate': 0.0,
                'avg_profit': 0.0,
                'avg_loss': 0.0,
                'best_trade': None,
                'worst_trade': None,
                'trades': []
            }
        
        wins = [t for t in trades if t.profit_loss and t.profit_loss > 0]
        losses = [t for t in trades if t.profit_loss and t.profit_loss < 0]
        
        total_pl = sum(t.profit_loss or 0 for t in trades)
        total_pl_pct = sum(t.profit_loss_pct or 0 for t in trades)
        
        best_trade = max(trades, key=lambda t: t.profit_loss or 0) if trades else None
        worst_trade = min(trades, key=lambda t: t.profit_loss or 0) if trades else None
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'total_profit_loss': round(total_pl, 2),
            'total_profit_loss_pct': round(total_pl_pct, 2),
            'win_rate': round((len(wins) / len(trades)) * 100, 2) if trades else 0,
            'avg_profit': round(sum(t.profit_loss for t in wins) / len(wins), 2) if wins else 0,
            'avg_loss': round(sum(t.profit_loss for t in losses) / len(losses), 2) if losses else 0,
            'best_trade': best_trade.to_dict() if best_trade else None,
            'worst_trade': worst_trade.to_dict() if worst_trade else None,
            'trades': [t.to_dict() for t in trades]
        }
    
    def get_hourly_stats(self, hours: int = 1) -> Dict:
        """Get P&L stats for the last N hours"""
        start_time = datetime.now() - timedelta(hours=hours)
        closed_trades = self.trade_manager.get_closed_trades()
        filtered = self._filter_trades_by_period(closed_trades, start_time)
        stats = self._calculate_stats(filtered)
        stats['period'] = f'last_{hours}_hours'
        stats['start_time'] = start_time.isoformat()
        stats['end_time'] = datetime.now().isoformat()
        return stats
    
    def get_daily_stats(self, days: int = 1) -> Dict:
        """Get P&L stats for the last N days"""
        start_time = datetime.now() - timedelta(days=days)
        closed_trades = self.trade_manager.get_closed_trades()
        filtered = self._filter_trades_by_period(closed_trades, start_time)
        stats = self._calculate_stats(filtered)
        stats['period'] = f'last_{days}_days'
        stats['start_time'] = start_time.isoformat()
        stats['end_time'] = datetime.now().isoformat()
        return stats
    
    def get_weekly_stats(self, weeks: int = 1) -> Dict:
        """Get P&L stats for the last N weeks"""
        start_time = datetime.now() - timedelta(weeks=weeks)
        closed_trades = self.trade_manager.get_closed_trades()
        filtered = self._filter_trades_by_period(closed_trades, start_time)
        stats = self._calculate_stats(filtered)
        stats['period'] = f'last_{weeks}_weeks'
        stats['start_time'] = start_time.isoformat()
        stats['end_time'] = datetime.now().isoformat()
        return stats
    
    def get_monthly_stats(self, months: int = 1) -> Dict:
        """Get P&L stats for the last N months"""
        start_time = datetime.now() - timedelta(days=months * 30)
        closed_trades = self.trade_manager.get_closed_trades()
        filtered = self._filter_trades_by_period(closed_trades, start_time)
        stats = self._calculate_stats(filtered)
        stats['period'] = f'last_{months}_months'
        stats['start_time'] = start_time.isoformat()
        stats['end_time'] = datetime.now().isoformat()
        return stats
    
    def get_all_time_stats(self) -> Dict:
        """Get all-time P&L stats"""
        closed_trades = self.trade_manager.get_closed_trades()
        stats = self._calculate_stats(closed_trades)
        stats['period'] = 'all_time'
        return stats
    
    def get_summary(self) -> Dict:
        """Get comprehensive summary with all time periods"""
        return {
            'hourly': self.get_hourly_stats(1),
            'daily': self.get_daily_stats(1),
            'weekly': self.get_weekly_stats(1),
            'monthly': self.get_monthly_stats(1),
            'all_time': self.get_all_time_stats(),
            'open_trades': [t.to_dict() for t in self.trade_manager.get_open_trades()],
            'recent_trades': [t.to_dict() for t in self.trade_manager.get_closed_trades()[-10:]]
        }
    
    def get_daily_breakdown(self, days: int = 7) -> List[Dict]:
        """Get day-by-day breakdown for the last N days"""
        breakdown = []
        closed_trades = self.trade_manager.get_closed_trades()
        
        for i in range(days):
            day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            filtered = self._filter_trades_by_period(closed_trades, day_start, day_end)
            total_pl = sum(t.profit_loss or 0 for t in filtered)
            
            breakdown.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'day': day_start.strftime('%A'),
                'trades': len(filtered),
                'profit_loss': round(total_pl, 2)
            })
        
        return breakdown[::-1]  # Reverse to get chronological order
