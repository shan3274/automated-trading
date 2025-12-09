import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  Calendar,
  BarChart2,
  DollarSign,
  Activity,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

function TradeHistory({ apiUrl }) {
  const [trades, setTrades] = useState([]);
  const [openTrades, setOpenTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('open');
  const [expandedTrade, setExpandedTrade] = useState(null);
  const [closingId, setClosingId] = useState(null);

  const fetchTrades = async () => {
    try {
      const [openRes, closedRes] = await Promise.all([
        fetch(`${apiUrl}/api/trades/open`),
        fetch(`${apiUrl}/api/trades/closed?limit=20`)
      ]);
      
      const openData = await openRes.json();
      const closedData = await closedRes.json();
      
      setOpenTrades(openData.trades || []);
      setTrades(closedData.trades || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching trades:', error);
      setLoading(false);
    }
  };

  const handleCloseTrade = async (tradeId) => {
    try {
      setClosingId(tradeId);
      await fetch(`${apiUrl}/api/trades/${tradeId}/close`, {
        method: 'POST'
      });
      await fetchTrades();
    } catch (error) {
      console.error('Error closing trade:', error);
    } finally {
      setClosingId(null);
    }
  };

  useEffect(() => {
    fetchTrades();
    const interval = setInterval(fetchTrades, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, [apiUrl]);

  const formatPrice = (price) => {
    if (price === null || price === undefined) return 'N/A';
    return `$${parseFloat(price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatPL = (pl, pct) => {
    if (pl === undefined || pl === null) return null;
    const isPositive = pl >= 0;
    return (
      <span className={isPositive ? 'positive' : 'negative'}>
        {isPositive ? '+' : ''}{formatPrice(pl)} ({isPositive ? '+' : ''}{pct?.toFixed(2)}%)
      </span>
    );
  };

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <Activity size={20} />
            Trade History
          </h2>
        </div>
        <div style={{ padding: '40px', textAlign: 'center', color: '#8a8aa3' }}>
          Loading trades...
        </div>
      </div>
    );
  }

  return (
    <div className="card trade-history-card">
      <div className="card-header">
        <h2 className="card-title">
          <Activity size={20} />
          Trade History
        </h2>
      </div>

      {/* Tabs */}
      <div className="trade-tabs">
        <button 
          className={`trade-tab ${activeTab === 'open' ? 'active' : ''}`}
          onClick={() => setActiveTab('open')}
        >
          🟢 Running ({openTrades.length})
        </button>
        <button 
          className={`trade-tab ${activeTab === 'closed' ? 'active' : ''}`}
          onClick={() => setActiveTab('closed')}
        >
          ✅ Closed ({trades.length})
        </button>
      </div>

      {/* Open/Running Trades */}
      {activeTab === 'open' && (
        <div className="trades-list">
          {openTrades.length === 0 ? (
            <div className="no-trades">
              <p>No running trades</p>
            </div>
          ) : (
            openTrades.map((trade, index) => (
              <div 
                key={trade.id || index} 
                className="trade-item open-trade"
                onClick={() => setExpandedTrade(expandedTrade === trade.id ? null : trade.id)}
              >
                <div className="trade-header">
                  <div className="trade-main">
                    <span className={`trade-side ${trade.side?.toLowerCase()}`}>{trade.side}</span>
                    <span className="trade-symbol">{trade.symbol}</span>
                    <span className="trade-qty">{trade.quantity}</span>
                  </div>
                  <div className="trade-pl">
                    {trade.unrealized_pl !== undefined && (
                      <span className={trade.unrealized_pl >= 0 ? 'positive' : 'negative'}>
                        {trade.unrealized_pl >= 0 ? '+' : ''}{formatPrice(trade.unrealized_pl)}
                        <br/>
                        <small>({trade.unrealized_pl_pct >= 0 ? '+' : ''}{trade.unrealized_pl_pct?.toFixed(2)}%)</small>
                      </span>
                    )}
                  </div>
                  <div className="trade-actions">
                    <button 
                      className="trade-close-btn"
                      disabled={closingId === trade.id}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCloseTrade(trade.id);
                      }}
                    >
                      {closingId === trade.id ? 'Closing...' : 'Close'}
                    </button>
                  </div>
                  {expandedTrade === trade.id ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </div>
                
                {expandedTrade === trade.id && (
                  <div className="trade-details">
                    <div className="detail-row">
                      <span>Entry Price:</span>
                      <span>{formatPrice(trade.entry_price)}</span>
                    </div>
                    <div className="detail-row">
                      <span>Current Price:</span>
                      <span>{formatPrice(trade.current_price)}</span>
                    </div>
                    <div className="detail-row">
                      <span>Take Profit:</span>
                      <span>{formatPrice(trade.take_profit)}</span>
                    </div>
                    <div className="detail-row">
                      <span>Stop Loss:</span>
                      <span>{formatPrice(trade.stop_loss)}</span>
                    </div>
                    <div className="detail-row">
                      <span>Entry Time:</span>
                      <span>{formatDate(trade.entry_time)}</span>
                    </div>
                    <div className="detail-row">
                      <span>Strategy:</span>
                      <span>{trade.strategy || 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                      <span>Trade ID:</span>
                      <span className="trade-id">{trade.id}</span>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Closed Trades */}
      {activeTab === 'closed' && (
        <div className="trades-list">
          {trades.length === 0 ? (
            <div className="no-trades">
              <p>No closed trades yet</p>
            </div>
          ) : (
            trades.map((trade, index) => (
              <div 
                key={trade.id || index} 
                className={`trade-item closed-trade ${trade.profit_loss >= 0 ? 'profitable' : 'loss'}`}
                onClick={() => setExpandedTrade(expandedTrade === trade.id ? null : trade.id)}
              >
                <div className="trade-header">
                  <div className="trade-main">
                    <span className={`trade-side ${trade.side?.toLowerCase()}`}>{trade.side}</span>
                    <span className="trade-symbol">{trade.symbol}</span>
                    <span className="trade-qty">{trade.quantity}</span>
                  </div>
                  <div className="trade-pl">
                    {formatPL(trade.profit_loss, trade.profit_loss_pct)}
                  </div>
                  {expandedTrade === trade.id ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                </div>
                
                {expandedTrade === trade.id && (
                  <div className="trade-details">
                    <div className="detail-row">
                      <span>Entry Price:</span>
                      <span>{formatPrice(trade.entry_price)}</span>
                    </div>
                    <div className="detail-row">
                      <span>Exit Price:</span>
                      <span>{formatPrice(trade.exit_price)}</span>
                    </div>
                    <div className="detail-row">
                      <span>Take Profit:</span>
                      <span>{formatPrice(trade.take_profit)}</span>
                    </div>
                    <div className="detail-row">
                      <span>Stop Loss:</span>
                      <span>{formatPrice(trade.stop_loss)}</span>
                    </div>
                    <div className="detail-row">
                      <span>Entry Time:</span>
                      <span>{formatDate(trade.entry_time)}</span>
                    </div>
                    <div className="detail-row">
                      <span>Exit Time:</span>
                      <span>{formatDate(trade.exit_time)}</span>
                    </div>
                    <div className="detail-row">
                      <span>Strategy:</span>
                      <span>{trade.strategy || 'N/A'}</span>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default TradeHistory;
