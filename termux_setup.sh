#!/data/data/com.termux/files/usr/bin/bash
# Termux Setup Script for Crypto Trading Bot
# Run this in Termux: bash termux_setup.sh

echo "🚀 Setting up Crypto Trading Bot on Termux..."
echo ""

# Update packages
echo "📦 Updating Termux packages..."
pkg update -y && pkg upgrade -y

# Install required packages
echo "📦 Installing Python and dependencies..."
pkg install -y python git clang openssl libffi rust binutils

# Setup storage access
echo "📂 Setting up storage access..."
termux-setup-storage

# Install pip packages
echo "🐍 Installing Python packages..."
pip install --upgrade pip

# Install requirements one by one to handle errors
echo "📚 Installing trading bot requirements..."
pip install python-binance==1.0.19
pip install pandas==2.0.3
pip install ta==0.11.0
pip install flask==3.0.0
pip install flask-cors==4.0.0
pip install flask-socketio==5.3.5
pip install python-dotenv==1.0.0

# Create .env file if not exists
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# Binance API Configuration
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
USE_TESTNET=True

# Trading Config
TRADE_SYMBOL=BTCUSDT
TRADE_QUANTITY=0.001
EOF
    echo "✅ .env file created"
fi

# Make scripts executable
chmod +x *.sh

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║     ✅ Setup Complete!                     ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "📝 IMPORTANT: Edit .env file with your API keys"
echo "   nano .env"
echo ""
echo "🚀 Quick Commands:"
echo "   Start bot:    bash start.sh"
echo "   Stop bot:     bash stop.sh"
echo "   Check status: bash status.sh"
echo "   View logs:    bash logs.sh"
echo ""
echo "📚 Full guide: cat TERMUX_GUIDE.md"
echo ""
echo "🎉 Ready to trade!"
