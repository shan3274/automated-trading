import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  Calendar,
  BarChart2,
  DollarSign,
  Percent,
  Award,
  Target
} from 'lucide-react';

function Analytics({ apiUrl }) {
  const [analytics, setAnalytics] = useState(null);
  const [breakdown, setBreakdown] = useState([]);
  const [selectedPeriod, setSelectedPeriod] = useState('daily');
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = async () => {
    try {
      const [summaryRes, breakdownRes] = await Promise.all([
        fetch(`${apiUrl}/api/analytics/summary`),
        fetch(`${apiUrl}/api/analytics/breakdown?days=7`)
      ]);
      
      const summaryData = await summaryRes.json();
      const breakdownData = await breakdownRes.json();
      
      setAnalytics(summaryData);
      setBreakdown(breakdownData.breakdown || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [apiUrl]);

  const formatPrice = (price) => {
    if (!price && price !== 0) return '$0.00';
    const isNegative = price < 0;
    return `${isNegative ? '-' : ''}$${Math.abs(price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const getPeriodData = () => {
    if (!analytics) return null;
    
    switch (selectedPeriod) {
      case 'hourly': return analytics.hourly;
      case 'daily': return analytics.daily;
      case 'weekly': return analytics.weekly;
      case 'monthly': return analytics.monthly;
      case 'all_time': return analytics.all_time;
      default: return analytics.daily;
    }
  };

  const currentPeriod = getPeriodData();

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <BarChart2 size={20} />
            P&L Analytics
          </h2>
        </div>
        <div style={{ padding: '40px', textAlign: 'center', color: '#8a8aa3' }}>
          Loading analytics...
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-container">
      {/* Period Selector */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <BarChart2 size={20} />
            Profit & Loss Analytics
          </h2>
        </div>
        
        <div className="period-selector">
          {['hourly', 'daily', 'weekly', 'monthly', 'all_time'].map((period) => (
            <button
              key={period}
              className={`period-btn ${selectedPeriod === period ? 'active' : ''}`}
              onClick={() => setSelectedPeriod(period)}
            >
              {period === 'hourly' && <Clock size={16} />}
              {period === 'daily' && <Calendar size={16} />}
              {period === 'weekly' && '📅'}
              {period === 'monthly' && '📆'}
              {period === 'all_time' && <Target size={16} />}
              <span>{period.replace('_', ' ').toUpperCase()}</span>
            </button>
          ))}
        </div>

        {/* Stats Grid */}
        {currentPeriod && (
          <div className="analytics-stats-grid">
            <div className={`analytics-stat ${currentPeriod.total_profit_loss >= 0 ? 'positive' : 'negative'}`}>
              <div className="stat-icon">
                <DollarSign size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-label">Total P&L</div>
                <div className="stat-value">
                  {currentPeriod.total_profit_loss >= 0 ? '+' : ''}{formatPrice(currentPeriod.total_profit_loss)}
                </div>
                <div className="stat-sub">
                  {currentPeriod.total_profit_loss_pct >= 0 ? '+' : ''}{currentPeriod.total_profit_loss_pct?.toFixed(2)}%
                </div>
              </div>
            </div>

            <div className="analytics-stat">
              <div className="stat-icon">
                <BarChart2 size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-label">Total Trades</div>
                <div className="stat-value">{currentPeriod.total_trades}</div>
                <div className="stat-sub">
                  <span className="win">{currentPeriod.winning_trades}W</span>
                  {' / '}
                  <span className="loss">{currentPeriod.losing_trades}L</span>
                </div>
              </div>
            </div>

            <div className="analytics-stat">
              <div className="stat-icon">
                <Percent size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-label">Win Rate</div>
                <div className="stat-value">{currentPeriod.win_rate?.toFixed(1)}%</div>
                <div className="stat-sub">
                  {currentPeriod.win_rate >= 50 ? '🎯 Good' : '⚠️ Needs Work'}
                </div>
              </div>
            </div>

            <div className="analytics-stat">
              <div className="stat-icon">
                <TrendingUp size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-label">Avg Win</div>
                <div className="stat-value positive">+{formatPrice(currentPeriod.avg_profit)}</div>
              </div>
            </div>

            <div className="analytics-stat">
              <div className="stat-icon">
                <TrendingDown size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-label">Avg Loss</div>
                <div className="stat-value negative">{formatPrice(currentPeriod.avg_loss)}</div>
              </div>
            </div>

            <div className="analytics-stat">
              <div className="stat-icon">
                <Award size={24} />
              </div>
              <div className="stat-content">
                <div className="stat-label">Best Trade</div>
                <div className="stat-value positive">
                  {currentPeriod.best_trade ? `+${formatPrice(currentPeriod.best_trade.profit_loss)}` : 'N/A'}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 7-Day Breakdown Chart */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <Calendar size={20} />
            7-Day Performance
          </h2>
        </div>
        
        <div className="daily-breakdown">
          {breakdown.length === 0 ? (
            <div className="no-data">No data available</div>
          ) : (
            <div className="breakdown-chart">
              {breakdown.map((day, index) => {
                const maxPL = Math.max(...breakdown.map(d => Math.abs(d.profit_loss || 0)), 1);
                const barHeight = Math.abs(day.profit_loss || 0) / maxPL * 100;
                const isPositive = (day.profit_loss || 0) >= 0;
                
                return (
                  <div key={index} className="breakdown-bar">
                    <div className="bar-container">
                      <div 
                        className={`bar ${isPositive ? 'positive' : 'negative'}`}
                        style={{ height: `${Math.max(barHeight, 5)}%` }}
                      >
                        <span className="bar-value">
                          {isPositive ? '+' : ''}{formatPrice(day.profit_loss)}
                        </span>
                      </div>
                    </div>
                    <div className="bar-label">
                      <div className="bar-day">{day.day?.slice(0, 3)}</div>
                      <div className="bar-trades">{day.trades} trades</div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Open Trades Summary */}
      {analytics?.open_trades && analytics.open_trades.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">
              🟢 Active Positions ({analytics.open_trades.length})
            </h2>
          </div>
          <div className="open-trades-summary">
            {analytics.open_trades.map((trade, index) => (
              <div key={index} className="open-trade-item">
                <div className="trade-symbol">{trade.symbol}</div>
                <div className="trade-info">
                  <span className="trade-side buy">{trade.side}</span>
                  <span>{trade.quantity} @ {formatPrice(trade.entry_price)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Analytics;
