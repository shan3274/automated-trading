"""
Base Strategy Class - All strategies inherit from this
"""
from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional
from enum import Enum

class Signal(Enum):
    """Trading signals"""
    BUY = 'BUY'
    SELL = 'SELL'
    HOLD = 'HOLD'

class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.position = None  # Current position
        self.entry_price = 0.0
    
    @abstractmethod
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        pass
    
    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> Signal:
        """Generate trading signal based on indicators"""
        pass
    
    def should_buy(self, df: pd.DataFrame) -> bool:
        """Check if we should buy"""
        return self.generate_signal(df) == Signal.BUY
    
    def should_sell(self, df: pd.DataFrame) -> bool:
        """Check if we should sell"""
        return self.generate_signal(df) == Signal.SELL
    
    def update_position(self, position: str, price: float):
        """Update current position"""
        self.position = position
        self.entry_price = price
    
    def clear_position(self):
        """Clear current position"""
        self.position = None
        self.entry_price = 0.0
