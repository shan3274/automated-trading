import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign, 
  BarChart3,
  Play,
  Square,
  Settings,
  Zap,
  XCircle,
  Clock
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5001';

function Dashboard({ prices, selectedCrypto, analysis, botStatus, onStartBot, onStopBot }) {
  const [showSettings, setShowSettings] = useState(false);
  const [botConfig, setBotConfig] = useState({
    symbol: 'BTCUSDT',
    strategy: 'combined',
    quantity: 0.001
  });
  const [openTrades, setOpenTrades] = useState([]);

  // Fetch open trades from API
  const fetchOpenTrades = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/trades/open`);
      const data = await response.json();
      setOpenTrades(data.trades || []);
    } catch (error) {
      console.error('Error fetching open trades:', error);
    }
  };

  useEffect(() => {
    fetchOpenTrades();
    const interval = setInterval(fetchOpenTrades, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

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

  const handleClosePosition = async () => {
    if (!window.confirm('Are you sure you want to close the current position?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/bot/close-position`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();

      if (response.ok) {
        const profitClass = data.profit_loss >= 0 ? 'profit' : 'loss';
        const profitSign = data.profit_loss >= 0 ? '+' : '';
        alert(
          `Position Closed!\n\n` +
          `Entry: ${formatPrice(data.entry_price)}\n` +
          `Exit: ${formatPrice(data.exit_price)}\n` +
          `P/L: ${profitSign}${formatPrice(data.profit_loss)} (${data.profit_pct.toFixed(2)}%)`
        );
      } else {
        alert('Error: ' + (data.error || 'Failed to close position'));
      }
    } catch (error) {
      alert('Failed to close position: ' + error.message);
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

  const buildIndicatorLogs = (a) => {
    if (!a) return [];
    const logs = [];

    if (a.rsi !== undefined) {
      const status = getRSIStatus(a.rsi);
      logs.push({
        title: 'RSI',
        text: `RSI ${status.text} — momentum ${a.rsi < 40 ? 'leaning bullish' : a.rsi > 60 ? 'leaning bearish' : 'neutral'}`,
        tone: status.class
      });
    }

    if (a.ema_9 && a.ema_21 && a.price) {
      const emaTrendUp = a.ema_9 > a.ema_21;
      logs.push({
        title: 'Trend (EMA)',
        text: `Price ${formatPrice(a.price)} is ${emaTrendUp ? 'above' : 'below'} 21 EMA; short EMA ${emaTrendUp ? 'leading' : 'lagging'} -> ${emaTrendUp ? 'bullish bias' : 'bearish bias'}`,
        tone: emaTrendUp ? 'buy' : 'sell'
      });
    }

    if (a.macd !== undefined && a.macd_signal !== undefined) {
      const macdUp = a.macd > a.macd_signal;
      logs.push({
        title: 'MACD',
        text: `MACD ${a.macd?.toFixed(2) ?? 'N/A'} vs signal ${a.macd_signal?.toFixed(2) ?? 'N/A'} -> ${macdUp ? 'momentum picking up' : 'momentum fading'}`,
        tone: macdUp ? 'buy' : 'sell'
      });
    }

    if (a.bb_lower && a.bb_upper && a.price) {
      const nearLower = a.price <= a.bb_lower * 1.02;
      const nearUpper = a.price >= a.bb_upper * 0.98;
      if (nearLower) {
        logs.push({ title: 'Bollinger', text: 'Price near lower band — value zone if buyers step in', tone: 'buy' });
      } else if (nearUpper) {
        logs.push({ title: 'Bollinger', text: 'Price near upper band — stretched, watch for pullback', tone: 'sell' });
      } else {
        logs.push({ title: 'Bollinger', text: 'Price mid-band — balanced, no edge', tone: 'neutral' });
      }
    }

    if (a.signal) {
      logs.push({
        title: 'Composite Signal',
        text: `${a.signal} (${a.signal_strength || 0}/4 confirmations)`,
        tone: getSignalClass(a.signal)
      });
    }

    return logs;
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
                <>
                  <button className="btn btn-stop" onClick={handleStopBot}>
                    <Square size={18} />
                    Stop Bot
                  </button>
                  <button 
                    className="btn btn-close-trade" 
                    onClick={handleClosePosition}
                    disabled={!botStatus.in_position}
                    style={{
                      background: botStatus.in_position 
                        ? 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
                        : 'rgba(74, 74, 106, 0.5)',
                      border: 'none',
                      marginLeft: '12px',
                      cursor: botStatus.in_position ? 'pointer' : 'not-allowed',
                      opacity: botStatus.in_position ? 1 : 0.5
                    }}
                    title={botStatus.in_position ? 'Close current trade' : 'No open position'}
                  >
                    <XCircle size={18} />
                    Close Trade
                  </button>
                </>
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
                  <option value="BTCUSDT">₿ BTC/USDT</option>
                  <option value="ETHUSDT">Ξ ETH/USDT</option>
                  <option value="SOLUSDT">S SOL/USDT</option>
                  <option value="DOGEUSDT">🐕 DOGE/USDT</option>
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
                  <option value="pulse">🚀 Momentum Pulse (Aggressive)</option>
                  <option value="mtf">🧭 MTF Pulse (HTF trend + 5m entries)</option>
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

      {/* Running Trades Section */}
      {openTrades.length > 0 && (
        <div className="card" style={{ marginTop: '24px' }}>
          <div className="card-header">
            <h2 className="card-title">
              <Clock size={20} />
              🟢 Running Trades ({openTrades.length})
            </h2>
          </div>
          <div className="running-trades-list">
            {openTrades.map((trade, index) => (
              <div 
                key={trade.id || index} 
                className="running-trade-item"
                style={{
                  padding: '16px',
                  background: 'rgba(0, 212, 170, 0.1)',
                  borderRadius: '12px',
                  marginBottom: '12px',
                  border: '1px solid rgba(0, 212, 170, 0.2)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <span style={{ 
                      background: trade.side === 'BUY' ? 'rgba(0, 212, 170, 0.3)' : 'rgba(255, 71, 87, 0.3)',
                      padding: '4px 12px',
                      borderRadius: '6px',
                      color: trade.side === 'BUY' ? '#00d4aa' : '#ff4757',
                      fontWeight: '600',
                      fontSize: '0.85rem'
                    }}>
                      {trade.side}
                    </span>
                    <span style={{ fontWeight: '600', fontSize: '1.1rem' }}>{trade.symbol}</span>
                    <span style={{ color: '#8a8aa3' }}>× {trade.quantity}</span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    {trade.unrealized_pl !== undefined && (
                      <div style={{ 
                        color: trade.unrealized_pl >= 0 ? '#00d4aa' : '#ff4757',
                        fontWeight: '600',
                        fontSize: '1.1rem'
                      }}>
                        {trade.unrealized_pl >= 0 ? '+' : ''}{formatPrice(trade.unrealized_pl)}
                        <span style={{ fontSize: '0.85rem', marginLeft: '8px' }}>
                          ({trade.unrealized_pl_pct >= 0 ? '+' : ''}{trade.unrealized_pl_pct?.toFixed(2)}%)
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', fontSize: '0.9rem' }}>
                  <div>
                    <span style={{ color: '#8a8aa3' }}>Entry: </span>
                    <span style={{ fontWeight: '500' }}>{formatPrice(trade.entry_price)}</span>
                  </div>
                  <div>
                    <span style={{ color: '#8a8aa3' }}>Current: </span>
                    <span style={{ fontWeight: '500' }}>{formatPrice(trade.current_price)}</span>
                  </div>
                  <div>
                    <span style={{ color: '#8a8aa3' }}>Strategy: </span>
                    <span style={{ fontWeight: '500' }}>{trade.strategy || 'N/A'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

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
