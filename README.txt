
🤖 FlexBot Complete Package - हिंदी Setup Guide

📁 मुख्य Files:
✅ enhanced_bot.py     - मुख्य bot (सभी features के साथ)
✅ permanent_host.py   - Auto-restart service 
✅ quick_start.py      - Quick launcher
✅ key.txt            - Premium activation key
✅ apk_file_id.txt    - APK file ID
✅ user_ids.txt       - User database

🚀 Setup Instructions:

1️⃣ Dependencies Install करें:
   pip install aiogram asyncio

2️⃣ Bot Configure करें:
   - enhanced_bot.py में अपना BOT_TOKEN डालें
   - ADMIN_ID अपना Telegram ID डालें
   - CHANNEL_ID अपना channel username डालें

3️⃣ Bot चलाने के तरीके:

   🔥 Normal Run:
   python3 enhanced_bot.py

   ⚡ Permanent Hosting (Auto-restart):
   python3 permanent_host.py

   🚀 Quick Start:
   python3 quick_start.py

🎛️ Admin Commands:
/setkey <text>       - Premium key set करें
/setapk (with file)  - APK upload करें  
/broadcast <message> - सभी users को message भेजें
/block <user_id>     - User को block करें
/status             - Bot statistics देखें

💎 Premium Features:
- Key distribution system
- APK file sharing
- Channel membership verification
- Advanced broadcasting
- User management
- Auto-restart functionality

🔧 Bot Configuration:
1. अपना bot token डालें
2. Admin ID set करें
3. Channel ID configure करें
4. Premium key और APK file setup करें

📊 File Structure:
- Data files automatically create होंगी
- User database maintain होगा
- Blocked users list manage होगी

🛡️ Security:
- Admin-only commands
- Channel verification
- User blocking system
- Secure file handling

Happy Botting! 🎉
