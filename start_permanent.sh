
#!/bin/bash

echo "🎯 FlexBot Permanent Hosting Startup Script"
echo "🚀 Free Trial - Maximum Uptime Mode"
echo ""

# Kill any existing bot processes
echo "🧹 Cleaning up existing processes..."
pkill -f "enhanced_bot.py" 2>/dev/null
pkill -f "permanent_host.py" 2>/dev/null
sleep 2

# Make sure log directory exists
mkdir -p logs

echo "🔥 Starting permanent hosting service..."
echo "📊 Bot will restart automatically if it stops"
echo "💾 Logs will be saved to bot_host.log"
echo ""

# Start permanent hosting service
python3 permanent_host.py

echo "🏁 Permanent hosting service ended"
