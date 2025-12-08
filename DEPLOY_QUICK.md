# 🚀 Quick Deployment Steps

## ⚡ Fastest Way (Railway + Vercel)

### 1️⃣ Backend to Railway (5 minutes)

```bash
# Create GitHub repo
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/trading-bot.git
git push -u origin main
```

Then:
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. New Project → Deploy from GitHub
4. Select your repo
5. Add environment variables:
   - `BINANCE_API_KEY`
   - `BINANCE_API_SECRET`
   - `USE_TESTNET=True`
   - `TRADE_SYMBOL=BTCUSDT`
   - `TRADE_QUANTITY=0.001`
6. Railway will auto-deploy ✅
7. Copy your Railway URL (e.g., `https://xxx.railway.app`)

---

### 2️⃣ Frontend to Vercel (3 minutes)

```bash
cd frontend

# Create .env.production file
echo "REACT_APP_API_URL=https://your-railway-url.railway.app" > .env.production

# Deploy
npm install -g vercel
vercel login
vercel --prod
```

Or via Vercel Dashboard:
1. Go to [vercel.com](https://vercel.com)
2. Import Git Repository
3. Root Directory: `frontend`
4. Add Environment Variable:
   - Key: `REACT_APP_API_URL`
   - Value: `https://your-railway-url.railway.app`
5. Deploy ✅

---

## 💰 Cost

- Frontend (Vercel): **FREE** ✅
- Backend (Railway): **$5/month** (first $5 free credit)

---

## ⚠️ Before Going Live

1. ✅ Test on testnet first (USE_TESTNET=True)
2. ✅ Start with small quantity (0.001 BTC)
3. ✅ Monitor for 24 hours
4. ✅ Check logs regularly
5. ⚠️ Only then switch to live trading (USE_TESTNET=False)

---

## 📱 Access Your Bot

- **Dashboard**: `https://your-app.vercel.app`
- **API**: `https://your-railway-url.railway.app/api/health`

---

## 🔧 Local Testing First (Recommended)

Before deploying, test locally:
```bash
# Terminal 1: Backend
python api/server.py

# Terminal 2: Bot
python main.py

# Terminal 3: Frontend
cd frontend && npm start
```

Visit: http://localhost:3000

If everything works locally, then deploy! 🚀

---

## 🆘 Problems?

### Railway deployment fails
- Check `requirements.txt` has all packages
- View logs in Railway dashboard
- Verify environment variables

### Frontend can't connect
- Check CORS in `api/server.py`
- Verify `REACT_APP_API_URL` is set
- Check browser console (F12)

### Bot not trading
- This is NORMAL if market is sideways
- Check logs: should see "📊 Signal: HOLD"
- Bot waits for strong signals (this is good!)

---

Ready to deploy? Follow steps 1️⃣ and 2️⃣ above! 🎯
