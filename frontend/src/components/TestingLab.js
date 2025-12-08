import React, { useState } from 'react';
import '../TestingLab.css';
import { 
  TestTube, 
  TrendingUp, 
  TrendingDown, 
  Target,
  AlertTriangle,
  Play,
  CheckCircle,
  XCircle,
  Activity
} from 'lucide-react';

function TestingLab({ apiUrl }) {
  const [testResults, setTestResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [manualTrade, setManualTrade] = useState({
    symbol: 'BTCUSDT',
    side: 'BUY',
    quantity: 0.001,
    price: 0
  });

  const addResult = (test, status, message, data = null) => {
    const result = {
      id: Date.now(),
      test,
      status, // 'success', 'error', 'info'
      message,
      data,
      timestamp: new Date().toLocaleTimeString()
    };
    setTestResults(prev => [result, ...prev]);
    return result;
  };

  const testAPIConnection = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/health`);
      const data = await response.json();
      if (data.status === 'ok') {
        addResult('API Connection', 'success', 'API is responding correctly', data);
      } else {
        addResult('API Connection', 'error', 'API returned unexpected status', data);
      }
    } catch (error) {
      addResult('API Connection', 'error', `Connection failed: ${error.message}`);
    }
    setLoading(false);
  };

  const testGetBalance = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/balance`);
      const data = await response.json();
      const usdtBalance = data.USDT?.total || 0;
      const btcBalance = data.BTC?.total || 0;
      addResult('Get Balance', 'success', `USDT: ${usdtBalance}, BTC: ${btcBalance}`, data);
    } catch (error) {
      addResult('Get Balance', 'error', `Failed: ${error.message}`);
    }
    setLoading(false);
  };

  const testGetPrice = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/price/${manualTrade.symbol}`);
      const data = await response.json();
      addResult('Get Price', 'success', `${manualTrade.symbol}: $${data.price.toLocaleString()}`, data);
      setManualTrade(prev => ({ ...prev, price: data.price }));
    } catch (error) {
      addResult('Get Price', 'error', `Failed: ${error.message}`);
    }
    setLoading(false);
  };

  const testAnalysis = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/analysis/${manualTrade.symbol}`);
      const data = await response.json();
      const summary = `RSI: ${data.rsi?.toFixed(2) || 'N/A'}, Signal: ${data.signal}, Trend: ${data.trend}`;
      addResult('Technical Analysis', 'success', summary, data);
    } catch (error) {
      addResult('Technical Analysis', 'error', `Failed: ${error.message}`);
    }
    setLoading(false);
  };

  const testOpenTrades = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/trades/open`);
      const data = await response.json();
      addResult('Open Trades', 'info', `Found ${data.count || 0} open trades`, data);
    } catch (error) {
      addResult('Open Trades', 'error', `Failed: ${error.message}`);
    }
    setLoading(false);
  };

  const testClosedTrades = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/trades/closed?limit=5`);
      const data = await response.json();
      addResult('Closed Trades', 'info', `Found ${data.total || 0} closed trades`, data);
    } catch (error) {
      addResult('Closed Trades', 'error', `Failed: ${error.message}`);
    }
    setLoading(false);
  };

  const testPLAnalytics = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/analytics/summary`);
      const data = await response.json();
      const summary = `Daily P/L: $${data.daily?.total_profit_loss || 0}, Win Rate: ${data.daily?.win_rate || 0}%`;
      addResult('P&L Analytics', 'success', summary, data);
    } catch (error) {
      addResult('P&L Analytics', 'error', `Failed: ${error.message}`);
    }
    setLoading(false);
  };

  const simulateBuyOrder = async () => {
    setLoading(true);
    addResult('Simulate Buy Order', 'info', `Simulating BUY ${manualTrade.quantity} ${manualTrade.symbol} @ $${manualTrade.price}`, manualTrade);
    
    // Simulate delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Calculate costs
    const cost = manualTrade.quantity * manualTrade.price;
    addResult('Buy Order Cost', 'info', `Total cost: $${cost.toFixed(2)}`);
    setLoading(false);
  };

  const simulateSellOrder = async () => {
    setLoading(true);
    addResult('Simulate Sell Order', 'info', `Simulating SELL ${manualTrade.quantity} ${manualTrade.symbol} @ $${manualTrade.price}`, manualTrade);
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const proceeds = manualTrade.quantity * manualTrade.price;
    addResult('Sell Order Proceeds', 'info', `Total proceeds: $${proceeds.toFixed(2)}`);
    setLoading(false);
  };

  const testStopLoss = async () => {
    const stopLossPercent = 2.0;
    const entryPrice = manualTrade.price;
    const stopLossPrice = entryPrice * (1 - stopLossPercent / 100);
    const loss = (entryPrice - stopLossPrice) * manualTrade.quantity;
    
    addResult('Stop Loss Test', 'info', 
      `Entry: $${entryPrice.toFixed(2)}, SL: $${stopLossPrice.toFixed(2)}, Loss: $${loss.toFixed(2)} (-${stopLossPercent}%)`,
      { entryPrice, stopLossPrice, loss, stopLossPercent }
    );
  };

  const testTakeProfit = async () => {
    const takeProfitPercent = 4.0;
    const entryPrice = manualTrade.price;
    const takeProfitPrice = entryPrice * (1 + takeProfitPercent / 100);
    const profit = (takeProfitPrice - entryPrice) * manualTrade.quantity;
    
    addResult('Take Profit Test', 'success', 
      `Entry: $${entryPrice.toFixed(2)}, TP: $${takeProfitPrice.toFixed(2)}, Profit: $${profit.toFixed(2)} (+${takeProfitPercent}%)`,
      { entryPrice, takeProfitPrice, profit, takeProfitPercent }
    );
  };

  const runAllTests = async () => {
    setTestResults([]);
    addResult('Test Suite', 'info', 'Starting comprehensive test suite...');
    
    await testAPIConnection();
    await new Promise(r => setTimeout(r, 500));
    
    await testGetBalance();
    await new Promise(r => setTimeout(r, 500));
    
    await testGetPrice();
    await new Promise(r => setTimeout(r, 500));
    
    await testAnalysis();
    await new Promise(r => setTimeout(r, 500));
    
    await testOpenTrades();
    await new Promise(r => setTimeout(r, 500));
    
    await testClosedTrades();
    await new Promise(r => setTimeout(r, 500));
    
    await testPLAnalytics();
    await new Promise(r => setTimeout(r, 500));
    
    testStopLoss();
    await new Promise(r => setTimeout(r, 500));
    
    testTakeProfit();
    
    addResult('Test Suite', 'success', 'All tests completed!');
  };

  const clearResults = () => {
    setTestResults([]);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success': return <CheckCircle size={18} color="#00d4aa" />;
      case 'error': return <XCircle size={18} color="#ff6b6b" />;
      default: return <Activity size={18} color="#ffd93d" />;
    }
  };

  return (
    <div className="testing-lab-container">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <TestTube size={20} />
            Testing Lab
          </h2>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="btn btn-primary" onClick={runAllTests} disabled={loading}>
              <Play size={16} />
              Run All Tests
            </button>
            <button className="btn btn-secondary" onClick={clearResults}>
              Clear Results
            </button>
          </div>
        </div>

        {/* Manual Trade Setup */}
        <div className="test-section">
          <h3 className="section-title">Manual Trade Setup</h3>
          <div className="manual-trade-form">
            <div className="form-group">
              <label>Symbol</label>
              <select 
                value={manualTrade.symbol}
                onChange={(e) => setManualTrade({...manualTrade, symbol: e.target.value})}
              >
                <option value="BTCUSDT">BTC/USDT</option>
                <option value="ETHUSDT">ETH/USDT</option>
                <option value="BNBUSDT">BNB/USDT</option>
                <option value="SOLUSDT">SOL/USDT</option>
                <option value="XRPUSDT">XRP/USDT</option>
              </select>
            </div>
            <div className="form-group">
              <label>Quantity</label>
              <input 
                type="number" 
                step="0.001"
                value={manualTrade.quantity}
                onChange={(e) => setManualTrade({...manualTrade, quantity: parseFloat(e.target.value)})}
              />
            </div>
            <div className="form-group">
              <label>Price (Auto-fill with Get Price)</label>
              <input 
                type="number" 
                value={manualTrade.price}
                onChange={(e) => setManualTrade({...manualTrade, price: parseFloat(e.target.value)})}
              />
            </div>
          </div>
        </div>

        {/* Quick Tests */}
        <div className="test-section">
          <h3 className="section-title">Quick Tests</h3>
          <div className="test-buttons">
            <button className="test-btn" onClick={testAPIConnection} disabled={loading}>
              <Activity size={16} />
              API Connection
            </button>
            <button className="test-btn" onClick={testGetBalance} disabled={loading}>
              💰 Balance
            </button>
            <button className="test-btn" onClick={testGetPrice} disabled={loading}>
              💵 Get Price
            </button>
            <button className="test-btn" onClick={testAnalysis} disabled={loading}>
              📊 Analysis
            </button>
            <button className="test-btn" onClick={testOpenTrades} disabled={loading}>
              🟢 Open Trades
            </button>
            <button className="test-btn" onClick={testClosedTrades} disabled={loading}>
              ✅ Closed Trades
            </button>
            <button className="test-btn" onClick={testPLAnalytics} disabled={loading}>
              📈 P&L Analytics
            </button>
          </div>
        </div>

        {/* Trade Simulation */}
        <div className="test-section">
          <h3 className="section-title">Trade Simulation</h3>
          <div className="test-buttons">
            <button className="test-btn buy" onClick={simulateBuyOrder} disabled={loading || !manualTrade.price}>
              <TrendingUp size={16} />
              Simulate BUY
            </button>
            <button className="test-btn sell" onClick={simulateSellOrder} disabled={loading || !manualTrade.price}>
              <TrendingDown size={16} />
              Simulate SELL
            </button>
            <button className="test-btn" onClick={testStopLoss} disabled={!manualTrade.price}>
              <AlertTriangle size={16} />
              Test Stop Loss
            </button>
            <button className="test-btn" onClick={testTakeProfit} disabled={!manualTrade.price}>
              <Target size={16} />
              Test Take Profit
            </button>
          </div>
        </div>
      </div>

      {/* Test Results */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Test Results ({testResults.length})</h2>
        </div>
        
        <div className="test-results">
          {testResults.length === 0 ? (
            <div className="no-results">
              <p>No test results yet. Run some tests to see results here.</p>
            </div>
          ) : (
            testResults.map(result => (
              <div key={result.id} className={`test-result ${result.status}`}>
                <div className="result-header">
                  <div className="result-title">
                    {getStatusIcon(result.status)}
                    <span>{result.test}</span>
                  </div>
                  <span className="result-time">{result.timestamp}</span>
                </div>
                <div className="result-message">{result.message}</div>
                {result.data && (
                  <details className="result-data">
                    <summary>View Data</summary>
                    <pre>{JSON.stringify(result.data, null, 2)}</pre>
                  </details>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default TestingLab;
