# 🚀 Deployment Guide - Crypto Trading Bot

## Architecture

```
Frontend (React)  →  Vercel (FREE)
    ↓
Backend (Python)  →  Railway ($5/month)
    ↓
Binance API (Testnet/Live)
```

---

## 📦 Step 1: Prepare Code for Deployment

### A. Update Environment Variables

Create `.env.production` file:
```bash
# Binance API (Use your REAL keys for production)
BINANCE_API_KEY=your_production_api_key
BINANCE_API_SECRET=your_production_api_secret
USE_TESTNET=False  # Change to False for live trading!

# Trading Config
TRADE_SYMBOL=BTCUSDT
TRADE_QUANTITY=0.001

# IMPORTANT: For production, use HTTPS
FRONTEND_URL=https://your-app.vercel.app
```

---

## 🚂 Step 2: Deploy Backend to Railway

### Option A: Via GitHub (Recommended)

1. **Create GitHub Repository**
   ```bash
   cd /Users/shan/Desktop/Automate-trading
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/trading-bot.git
   git push -u origin main
   ```

2. **Deploy to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `trading-bot` repo
   - Railway will auto-detect Python and install dependencies

3. **Set Environment Variables on Railway**
   - Go to your project → Variables tab
   - Add all variables from `.env.production`
   - BINANCE_API_KEY
   - BINANCE_API_SECRET
   - USE_TESTNET
   - TRADE_SYMBOL
   - TRADE_QUANTITY

4. **Configure Start Command**
   - Settings → Start Command: `python api/server.py`
   - Or let it use `Procfile`

5. **Get Your Backend URL**
   - Railway will give you a URL like: `https://trading-bot-production.up.railway.app`
   - Copy this URL for frontend config

### Option B: Via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

---

## ⚡ Step 3: Deploy Frontend to Vercel

1. **Update Frontend API URL**

   Edit `frontend/src/App.js`:
   ```javascript
   // Change this line:
   const apiUrl = 'http://localhost:5001';
   
   // To:
   const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:5001';
   ```

2. **Create Frontend Environment File**

   Create `frontend/.env.production`:
   ```
   REACT_APP_API_URL=https://your-railway-backend-url.up.railway.app
   ```

3. **Deploy to Vercel**

   ```bash
   cd frontend
   
   # Install Vercel CLI
   npm install -g vercel
   
   # Login
   vercel login
   
   # Deploy
   vercel
   
   # For production
   vercel --prod
   ```

   Or use Vercel Dashboard:
   - Go to [vercel.com](https://vercel.com)
   - Import Git Repository
   - Root Directory: `frontend`
   - Framework Preset: Create React App
   - Add Environment Variable: `REACT_APP_API_URL`
   - Deploy

---

## 🔧 Step 4: Post-Deployment Configuration

### Update CORS in Backend

Edit `api/server.py`:
```python
# Update CORS origins
CORS(app, origins=[
    "http://localhost:3000",
    "https://your-app.vercel.app",  # Add your Vercel URL
    "https://*.vercel.app"  # Allow all Vercel preview URLs
])
```

Redeploy backend after this change.

---

## ✅ Step 5: Verify Deployment

1. **Check Backend Health**
   ```bash
   curl https://your-railway-url.up.railway.app/api/health
   ```
   Should return: `{"status": "ok"}`

2. **Check Frontend**
   - Open your Vercel URL
   - Dashboard should load
   - Check if it connects to backend

3. **Check Bot Logs**
   - Railway Dashboard → Logs tab
   - Should see: "🚀 Starting bot..."

---

## 💰 Cost Breakdown

### Option 1: Railway + Vercel
- **Frontend (Vercel)**: FREE ✅
- **Backend (Railway)**: $5/month
- **Total**: $5/month

### Option 2: DigitalOcean Droplet
- **Full VPS**: $6/month
- **Total**: $6/month (but more control)

### Option 3: AWS/GCP (Not recommended for beginners)
- Variable pricing, can get expensive

---

## 🛡️ Security Checklist Before Going Live

- [ ] API keys are in environment variables (NOT in code)
- [ ] `.env` is in `.gitignore`
- [ ] CORS is properly configured
- [ ] USE_TESTNET=False for live trading
- [ ] Stop loss and take profit are set
- [ ] Start with small trade quantity
- [ ] Test with testnet first for 1 week
- [ ] Monitor logs daily

---

## 🐛 Troubleshooting

### Backend won't start on Railway
- Check logs in Railway dashboard
- Verify `requirements.txt` has all dependencies
- Make sure `Procfile` or `railway.json` is correct

### Frontend can't connect to backend
- Check CORS configuration
- Verify `REACT_APP_API_URL` environment variable
- Check browser console for errors

### Bot not making trades
- Check logs for strategy signals
- Verify API keys are correct
- Check account balance
- Market might be sideways (normal behavior)

---

## 📱 Monitoring Your Bot

### Railway Logs
```bash
railway logs
```

### Set Up Alerts
- Railway: Notifications → Enable deployment alerts
- Add health check endpoint monitoring

### Regular Checks
- Check logs daily
- Monitor P&L in dashboard
- Verify API connection

---

## 🔄 Continuous Deployment

Once set up:
1. Make code changes locally
2. Commit and push to GitHub
3. Railway auto-deploys backend
4. Vercel auto-deploys frontend

---

## 🆘 Need Help?

If you get stuck:
1. Check Railway/Vercel logs
2. Check browser console (F12)
3. Test API endpoints with curl/Postman
4. Verify environment variables are set

---

## 🚨 IMPORTANT: Before Live Trading

1. **Test on Testnet for at least 1 week**
2. **Start with minimum quantity**
3. **Monitor closely for first 24 hours**
4. **Have stop loss configured**
5. **Never invest more than you can afford to lose**

---

Good luck! 🚀
