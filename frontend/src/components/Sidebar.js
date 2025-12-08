import React from 'react';
import { TrendingUp, LayoutDashboard, History, BarChart3, Wallet, TestTube } from 'lucide-react';

const cryptoIcons = {
  BTC: '₿',
  ETH: 'Ξ',
  BNB: 'B',
  SOL: 'S',
  XRP: 'X',
  DOGE: 'Ð',
  ADA: 'A',
  MATIC: 'M'
};

function Sidebar({ prices, selectedCrypto, onSelectCrypto, activeView, onViewChange }) {
  const formatPrice = (price) => {
    if (price >= 1000) {
      return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
    return `$${price.toFixed(4)}`;
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <TrendingUp size={28} color="#00d4aa" />
        <h1>CryptoBot</h1>
      </div>

      {/* Navigation Menu */}
      <div className="nav-menu">
        <div 
          className={`nav-item ${activeView === 'dashboard' ? 'active' : ''}`}
          onClick={() => onViewChange('dashboard')}
        >
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </div>
        <div 
          className={`nav-item ${activeView === 'wallet' ? 'active' : ''}`}
          onClick={() => onViewChange('wallet')}
        >
          <Wallet size={20} />
          <span>Wallet</span>
        </div>
        <div 
          className={`nav-item ${activeView === 'trades' ? 'active' : ''}`}
          onClick={() => onViewChange('trades')}
        >
          <History size={20} />
          <span>Trade History</span>
        </div>
        <div 
          className={`nav-item ${activeView === 'analytics' ? 'active' : ''}`}
          onClick={() => onViewChange('analytics')}
        >
          <BarChart3 size={20} />
          <span>Analytics</span>
        </div>
        <div 
          className={`nav-item ${activeView === 'testing' ? 'active' : ''}`}
          onClick={() => onViewChange('testing')}
        >
          <TestTube size={20} />
          <span>Testing Lab</span>
        </div>
      </div>

      <div className="divider"></div>
      
      <div className="crypto-list">
        {Object.entries(prices).map(([symbol, data]) => {
          const base = data?.base || symbol.replace('USDT', '').replace('BTC', '');
          return (
            <div 
              key={symbol}
              className={`crypto-item ${selectedCrypto === symbol ? 'active' : ''}`}
              onClick={() => onSelectCrypto(symbol)}
            >
              <div className="crypto-info">
                <div className="crypto-icon">
                  {cryptoIcons[base] || base?.charAt(0) || '?'}
                </div>
                <div>
                  <div className="crypto-name">{base}</div>
                  <div className="crypto-symbol">{symbol}</div>
                </div>
              </div>
              <div className="crypto-price">
                <div className="price-value">{formatPrice(data?.price || 0)}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default Sidebar;
