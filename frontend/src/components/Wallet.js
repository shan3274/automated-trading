import React from 'react';
import { Wallet as WalletIcon, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';

const cryptoIcons = {
  BTC: '₿',
  ETH: 'Ξ',
  BNB: 'B',
  SOL: 'S',
  XRP: 'X',
  DOGE: 'Ð',
  ADA: 'A',
  USDT: '$',
  USDC: '$',
  BUSD: '$'
};

function Wallet({ balances, prices }) {
  // Filter important assets with balance > 0
  const importantAssets = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'DOGE', 'ADA', 'USDT', 'USDC'];
  
  const getAssetData = () => {
    const assets = [];
    
    for (const [asset, balance] of Object.entries(balances)) {
      if (balance.total > 0) {
        const symbol = `${asset}USDT`;
        const price = prices[symbol]?.price || 0;
        const usdValue = asset === 'USDT' || asset === 'USDC' || asset === 'BUSD' 
          ? balance.total 
          : balance.total * price;
        
        assets.push({
          asset,
          ...balance,
          price,
          usdValue,
          isStablecoin: ['USDT', 'USDC', 'BUSD', 'TUSD', 'USD1'].includes(asset)
        });
      }
    }
    
    // Sort by USD value descending
    return assets.sort((a, b) => b.usdValue - a.usdValue);
  };

  const assetData = getAssetData();
  
  // Calculate totals
  const totalUsdValue = assetData.reduce((sum, a) => sum + a.usdValue, 0);
  const stablecoinValue = assetData.filter(a => a.isStablecoin).reduce((sum, a) => sum + a.usdValue, 0);
  const cryptoValue = totalUsdValue - stablecoinValue;

  const formatPrice = (price) => {
    if (!price && price !== 0) return '$0.00';
    if (price >= 1000) {
      return `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
    if (price >= 1) {
      return `$${price.toFixed(2)}`;
    }
    return `$${price.toFixed(6)}`;
  };

  const formatBalance = (balance) => {
    if (balance >= 1000) {
      return balance.toLocaleString('en-US', { maximumFractionDigits: 2 });
    }
    if (balance >= 1) {
      return balance.toFixed(4);
    }
    return balance.toFixed(8);
  };

  // Show top assets (important ones first, then by value)
  const topAssets = assetData
    .sort((a, b) => {
      const aImportant = importantAssets.includes(a.asset);
      const bImportant = importantAssets.includes(b.asset);
      if (aImportant && !bImportant) return -1;
      if (!aImportant && bImportant) return 1;
      return b.usdValue - a.usdValue;
    })
    .slice(0, 20);

  return (
    <div className="wallet-container">
      {/* Portfolio Summary */}
      <div className="card wallet-summary">
        <div className="card-header">
          <h2 className="card-title">
            <WalletIcon size={20} />
            Wallet Overview
          </h2>
          <span className="testnet-badge">🧪 Testnet</span>
        </div>

        <div className="portfolio-stats">
          <div className="portfolio-total">
            <div className="total-label">Total Portfolio Value</div>
            <div className="total-value">{formatPrice(totalUsdValue)}</div>
          </div>

          <div className="portfolio-breakdown">
            <div className="breakdown-item">
              <div className="breakdown-icon crypto">
                <TrendingUp size={20} />
              </div>
              <div className="breakdown-info">
                <div className="breakdown-label">Crypto Assets</div>
                <div className="breakdown-value">{formatPrice(cryptoValue)}</div>
              </div>
            </div>
            <div className="breakdown-item">
              <div className="breakdown-icon stable">
                <DollarSign size={20} />
              </div>
              <div className="breakdown-info">
                <div className="breakdown-label">Stablecoins</div>
                <div className="breakdown-value">{formatPrice(stablecoinValue)}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Assets List */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Assets ({topAssets.length})</h2>
        </div>

        <div className="assets-list">
          <div className="assets-header">
            <span>Asset</span>
            <span>Balance</span>
            <span>Price</span>
            <span>Value</span>
          </div>

          {topAssets.map((asset, index) => (
            <div key={asset.asset} className="asset-row">
              <div className="asset-info">
                <div className="asset-icon">
                  {cryptoIcons[asset.asset] || asset.asset.charAt(0)}
                </div>
                <div className="asset-name">
                  <span className="asset-symbol">{asset.asset}</span>
                  {asset.isStablecoin && <span className="stable-tag">Stable</span>}
                </div>
              </div>
              <div className="asset-balance">
                <span className="balance-free">{formatBalance(asset.free)}</span>
                {asset.locked > 0 && (
                  <span className="balance-locked">🔒 {formatBalance(asset.locked)}</span>
                )}
              </div>
              <div className="asset-price">
                {asset.isStablecoin ? '$1.00' : formatPrice(asset.price)}
              </div>
              <div className="asset-value">
                {formatPrice(asset.usdValue)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="wallet-quick-stats">
        <div className="quick-stat">
          <span className="quick-label">Total Assets</span>
          <span className="quick-value">{assetData.length}</span>
        </div>
        <div className="quick-stat">
          <span className="quick-label">Available USDT</span>
          <span className="quick-value">{formatBalance(balances.USDT?.free || 0)}</span>
        </div>
        <div className="quick-stat">
          <span className="quick-label">BTC Holdings</span>
          <span className="quick-value">{formatBalance(balances.BTC?.total || 0)} BTC</span>
        </div>
      </div>
    </div>
  );
}

export default Wallet;
