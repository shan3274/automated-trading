import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import Sidebar from './components/Sidebar';
import TradeHistory from './components/TradeHistory';
import Analytics from './components/Analytics';
import Wallet from './components/Wallet';
import TestingLab from './components/TestingLab';
import './App.css';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5001';
const API_URL = `${API_BASE}/api`;

function App() {
  const [prices, setPrices] = useState({});
  const [selectedCrypto, setSelectedCrypto] = useState('BTCUSDT');
  const [analysis, setAnalysis] = useState(null);
  const [botStatus, setBotStatus] = useState({ running: false });
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('dashboard'); // 'dashboard', 'trades', 'analytics', 'wallet', 'testing'
  const [balances, setBalances] = useState({});

  // Fetch prices
  const fetchPrices = async () => {
    try {
      const response = await axios.get(`${API_URL}/prices`);
      setPrices(response.data);
    } catch (error) {
      console.error('Error fetching prices:', error);
    }
  };

  // Fetch balances
  const fetchBalances = async () => {
    try {
      const response = await axios.get(`${API_URL}/balance`);
      setBalances(response.data);
    } catch (error) {
      console.error('Error fetching balances:', error);
    }
  };

  // Fetch analysis
  const fetchAnalysis = async (symbol) => {
    try {
      const response = await axios.get(`${API_URL}/analysis/${symbol}`);
      setAnalysis(response.data);
    } catch (error) {
      console.error('Error fetching analysis:', error);
    }
  };

  // Fetch bot status
  const fetchBotStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/bot/status`);
      setBotStatus(response.data);
    } catch (error) {
      console.error('Error fetching bot status:', error);
    }
  };

  // Start bot
  const startBot = async (config) => {
    try {
      const response = await axios.post(`${API_URL}/bot/start`, config);
      setBotStatus({ running: true, ...response.data });
      return response.data;
    } catch (error) {
      console.error('Error starting bot:', error);
      throw error;
    }
  };

  // Stop bot
  const stopBot = async () => {
    try {
      const response = await axios.post(`${API_URL}/bot/stop`);
      setBotStatus({ running: false });
      return response.data;
    } catch (error) {
      console.error('Error stopping bot:', error);
      throw error;
    }
  };

  useEffect(() => {
    const init = async () => {
      await fetchPrices();
      await fetchBalances();
      await fetchAnalysis(selectedCrypto);
      await fetchBotStatus();
      setLoading(false);
    };
    init();

    // Refresh prices every 10 seconds
    const priceInterval = setInterval(fetchPrices, 10000);
    // Refresh balances every 30 seconds
    const balanceInterval = setInterval(fetchBalances, 30000);
    // Refresh analysis every 30 seconds
    const analysisInterval = setInterval(() => fetchAnalysis(selectedCrypto), 30000);
    // Refresh bot status every 5 seconds
    const botInterval = setInterval(fetchBotStatus, 5000);

    return () => {
      clearInterval(priceInterval);
      clearInterval(balanceInterval);
      clearInterval(analysisInterval);
      clearInterval(botInterval);
    };
  }, [selectedCrypto]);

  const handleSelectCrypto = (symbol) => {
    setSelectedCrypto(symbol);
    fetchAnalysis(symbol);
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loader"></div>
        <p>Loading Trading Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="app">
      <Sidebar 
        prices={prices} 
        selectedCrypto={selectedCrypto}
        onSelectCrypto={handleSelectCrypto}
        activeView={activeView}
        onViewChange={setActiveView}
      />
      <main className="main-content">
        {activeView === 'dashboard' && (
          <Dashboard 
            prices={prices}
            selectedCrypto={selectedCrypto}
            analysis={analysis}
            botStatus={botStatus}
            onStartBot={startBot}
            onStopBot={stopBot}
          />
        )}
        {activeView === 'trades' && (
          <TradeHistory apiUrl={API_BASE} />
        )}
        {activeView === 'analytics' && (
          <Analytics apiUrl={API_BASE} />
        )}
        {activeView === 'wallet' && (
          <Wallet balances={balances} prices={prices} />
        )}
        {activeView === 'testing' && (
          <TestingLab apiUrl={API_BASE} />
        )}
      </main>
    </div>
  );
}

export default App;
