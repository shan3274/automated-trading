import React, { useState } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign, 
  BarChart3,
  Play,
  Square,
  Settings,
  Zap
} from 'lucide-react';

function Dashboard({ prices, selectedCrypto, analysis, botStatus, onStartBot, onStopBot }) {
  const [showSettings, setShowSettings] = useState(false);
  const [botConfig, setBotConfig] = useState({
    symbol: 'BTCUSDT',
    strategy: 'combined',
    quantity: 0.001
  });

  const currentPrice = prices[selectedCrypto]?.price || 0;
  const baseCurrency = selectedCrypto.replace('USDT', '');

  const formatPrice = (price) => {
    if (!price) return '$0.00';
    if (price >= 1000) {
      return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
    return `$${price.toFixed(4)}`;
  };

  const handleStartBot = async () => {
    try {
      await onStartBot(botConfig);
    } catch (error) {
      alert('Failed to start bot: ' + error.message);
    }
  };

  const handleStopBot = async () => {
    try {
      await onStopBot();
    } catch (error) {
      alert('Failed to stop bot: ' + error.message);
    }
  };

  const getSignalClass = (signal) => {
    if (!signal) return 'neutral';
    return signal.toLowerCase() === 'buy' ? 'buy' : 
           signal.toLowerCase() === 'sell' ? 'sell' : 'neutral';
  };

  const getRSIStatus = (rsi) => {
    if (!rsi) return { text: 'N/A', class: 'neutral' };
    if (rsi < 30) return { text: `${rsi.toFixed(1)} (Oversold)`, class: 'buy' };
    if (rsi > 70) return { text: `${rsi.toFixed(1)} (Overbought)`, class: 'sell' };
    return { text: rsi.toFixed(1), class: 'neutral' };
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h1 className="dashboard-title">
          <span>{baseCurrency}</span>/USDT Dashboard
        </h1>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <span style={{ color: '#8a8aa3' }}>Testnet Mode</span>
          <div style={{ 
            padding: '6px 12px', 
            background: 'rgba(255, 217, 61, 0.2)', 
            borderRadius: '8px',
            color: '#ffd93d',
            fontSize: '0.85rem'
          }}>
            🧪 Paper Trading
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <DollarSign size={18} />
            Current Price
          </div>
          <div className="stat-value">{formatPrice(currentPrice)}</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <Activity size={18} />
            RSI (14)
          </div>
          <div className={`stat-value ${getRSIStatus(analysis?.rsi).class}`}>
            {getRSIStatus(analysis?.rsi).text}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <BarChart3 size={18} />
            Trend
          </div>
          <div className={`stat-value ${analysis?.trend === 'UP' ? 'positive' : 'negative'}`}>
            {analysis?.trend === 'UP' ? (
              <><TrendingUp size={24} style={{ marginRight: '8px' }} /> Bullish</>
            ) : (
              <><TrendingDown size={24} style={{ marginRight: '8px' }} /> Bearish</>
            )}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <Zap size={18} />
            Signal
          </div>
          <div className={`stat-value ${getSignalClass(analysis?.signal)}`}>
            {analysis?.signal || 'NEUTRAL'}
          </div>
        </div>
      </div>

      {/* Bot Control Section */}
      <div className="bot-section">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">
              <Activity size={20} />
              Trading Bot Control
            </h2>
            <button 
              className="btn btn-secondary"
              onClick={() => setShowSettings(!showSettings)}
            >
              <Settings size={18} />
              Settings
            </button>
          </div>

          <div className="bot-control">
            <div className="bot-status">
              <div className={`status-indicator ${botStatus.running ? 'running' : 'stopped'}`}></div>
              <div className="bot-info">
                <h3>{botStatus.running ? '🟢 Bot Running' : '🔴 Bot Stopped'}</h3>
                <p>
                  {botStatus.running 
                    ? `Trading ${botStatus.symbol} with ${botStatus.strategy}`
                    : 'Click Start to begin automated trading'
                  }
                </p>
              </div>
            </div>

            <div className="bot-controls">
              {botStatus.running ? (
                <button className="btn btn-stop" onClick={handleStopBot}>
                  <Square size={18} />
                  Stop Bot
                </button>
              ) : (
                <button className="btn btn-start" onClick={handleStartBot}>
                  <Play size={18} />
                  Start Bot
                </button>
              )}
            </div>
          </div>

          {showSettings && (
            <div className="settings-form">
              <div className="form-group">
                <label>Trading Pair</label>
                <select 
                  value={botConfig.symbol}
                  onChange={(e) => setBotConfig({...botConfig, symbol: e.target.value})}
                >
                  <option value="BTCUSDT">BTC/USDT</option>
                  <option value="ETHUSDT">ETH/USDT</option>
                  <option value="BNBUSDT">BNB/USDT</option>
                  <option value="SOLUSDT">SOL/USDT</option>
                  <option value="XRPUSDT">XRP/USDT</option>
                </select>
              </div>
              <div className="form-group">
                <label>Strategy</label>
                <select 
                  value={botConfig.strategy}
                  onChange={(e) => setBotConfig({...botConfig, strategy: e.target.value})}
                >
                  <option value="combined">Combined (RSI + EMA) - 1h</option>
                  <option value="rsi">RSI Only - 1h</option>
                  <option value="ema">EMA Crossover - 1h</option>
                  <option value="1min">⚡ 1-Minute Fast (Testing)</option>
                </select>
              </div>
              <div className="form-group">
                <label>Quantity</label>
                <input 
                  type="number" 
                  step="0.001"
                  value={botConfig.quantity}
                  onChange={(e) => setBotConfig({...botConfig, quantity: parseFloat(e.target.value)})}
                />
              </div>
            </div>
          )}

          {botStatus.running && (
            <div style={{ marginTop: '20px', padding: '16px', background: 'rgba(0, 212, 170, 0.1)', borderRadius: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ color: '#8a8aa3' }}>Position:</span>
                <span style={{ fontWeight: '600' }}>{botStatus.in_position ? 'IN POSITION' : 'NO POSITION'}</span>
              </div>
              {botStatus.entry_price > 0 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ color: '#8a8aa3' }}>Entry Price:</span>
                  <span style={{ fontWeight: '600' }}>{formatPrice(botStatus.entry_price)}</span>
                </div>
              )}
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#8a8aa3' }}>Total Trades:</span>
                <span style={{ fontWeight: '600' }}>{botStatus.trades || 0}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Analysis Section */}
      <div className="analysis-section">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">
              <BarChart3 size={20} />
              Technical Indicators
            </h2>
          </div>
          
          <div className="indicators-grid">
            <div className="indicator">
              <div className="indicator-name">RSI (14)</div>
              <div className={`indicator-value ${getRSIStatus(analysis?.rsi).class}`}>
                {analysis?.rsi?.toFixed(2) || 'N/A'}
              </div>
            </div>
            <div className="indicator">
              <div className="indicator-name">EMA (9)</div>
              <div className="indicator-value">
                {formatPrice(analysis?.ema_9)}
              </div>
            </div>
            <div className="indicator">
              <div className="indicator-name">EMA (21)</div>
              <div className="indicator-value">
                {formatPrice(analysis?.ema_21)}
              </div>
            </div>
            <div className="indicator">
              <div className="indicator-name">MACD</div>
              <div className={`indicator-value ${analysis?.macd > 0 ? 'buy' : 'sell'}`}>
                {analysis?.macd?.toFixed(2) || 'N/A'}
              </div>
            </div>
            <div className="indicator">
              <div className="indicator-name">BB Upper</div>
              <div className="indicator-value">
                {formatPrice(analysis?.bb_upper)}
              </div>
            </div>
            <div className="indicator">
              <div className="indicator-name">BB Lower</div>
              <div className="indicator-value">
                {formatPrice(analysis?.bb_lower)}
              </div>
            </div>
          </div>
        </div>

        <div className="card signal-card">
          <h3 style={{ color: '#8a8aa3', marginBottom: '20px' }}>Trading Signal</h3>
          <div className={`signal-badge ${getSignalClass(analysis?.signal)}`}>
            {analysis?.signal || 'NEUTRAL'}
          </div>
          <p className="signal-strength">
            Signal Strength: {analysis?.signal_strength || 0}/4
          </p>
          <div style={{ marginTop: '20px', fontSize: '0.9rem', color: '#8a8aa3' }}>
            {analysis?.signal === 'BUY' && '📈 Multiple indicators suggest bullish momentum'}
            {analysis?.signal === 'SELL' && '📉 Multiple indicators suggest bearish momentum'}
            {analysis?.signal === 'NEUTRAL' && '⏳ Waiting for clear market direction'}
          </div>
        </div>
      </div>

      {/* Trade History */}
      {botStatus.trade_history && botStatus.trade_history.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Recent Trades</h2>
          </div>
          <div className="trade-history">
            {botStatus.trade_history.map((trade, index) => (
              <div key={index} className="trade-item">
                <span className={`trade-type ${trade.type.toLowerCase()}`}>{trade.type}</span>
                <span>{trade.symbol}</span>
                <span>{trade.quantity}</span>
                <span>{formatPrice(trade.price)}</span>
                {trade.profit_loss !== undefined && (
                  <span className={trade.profit_loss >= 0 ? 'positive' : 'negative'}>
                    {trade.profit_loss >= 0 ? '+' : ''}{formatPrice(trade.profit_loss)}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
