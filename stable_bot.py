#!/usr/bin/env python3
import asyncio
import logging
import os
import signal
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums import ContentType, ChatMemberStatus, ChatAction

# Configuration
API_TOKEN = "7686244968:AAHb1w8ybeNmRqEpmeTnX24dDkeGS6PUm8M"
ADMIN_ID = 7201285915
CHANNEL_ID = "@flex_public"

# Global variables
user_ids = set()
blocked_users = set()
verified_users = set()

def load_data():
    global user_ids, blocked_users, verified_users
    try:
        with open("user_ids.txt", "r") as f:
            user_ids = {int(line.strip()) for line in f if line.strip()}
    except FileNotFoundError:
        user_ids = set()

    try:
        with open("blocked_users.txt", "r") as f:
            blocked_users = {int(line.strip()) for line in f if line.strip()}
    except FileNotFoundError:
        blocked_users = set()

    try:
        with open("verified_users.txt", "r") as f:
            verified_users = {int(line.strip()) for line in f if line.strip()}
    except FileNotFoundError:
        verified_users = set()

def save_data():
    with open("user_ids.txt", "w") as f:
        for uid in user_ids:
            f.write(f"{uid}\n")

    with open("blocked_users.txt", "w") as f:
        for uid in blocked_users:
            f.write(f"{uid}\n")

    with open("verified_users.txt", "w") as f:
        for uid in verified_users:
            f.write(f"{uid}\n")

# Load data at startup
load_data()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize bot
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def advanced_typing_animation(chat_id: int, action_type: ChatAction = ChatAction.TYPING, operation: str = "key"):
    """Advanced typing animation with multiple stages and dynamic messages"""
    try:
        # Stage 1: Initial processing
        if operation == "key":
            status_msg = await bot.send_message(chat_id, "🔄 **Initializing Premium Key Generator...**", parse_mode="Markdown")
        else:
            status_msg = await bot.send_message(chat_id, "📤 **Initializing Download Manager...**", parse_mode="Markdown")
        
        await bot.send_chat_action(chat_id, action_type)
        await asyncio.sleep(1.2)
        
        # Stage 2: Security verification
        if operation == "key":
            await status_msg.edit_text("🔐 **Verifying Premium Access Credentials...**", parse_mode="Markdown")
        else:
            await status_msg.edit_text("🛡️ **Verifying Premium Download Rights...**", parse_mode="Markdown")
        
        await bot.send_chat_action(chat_id, action_type)
        await asyncio.sleep(1.5)
        
        # Stage 3: Generation/Preparation
        if operation == "key":
            await status_msg.edit_text("⚡ **Generating Secure Activation Key...**", parse_mode="Markdown")
        else:
            await status_msg.edit_text("📱 **Preparing Premium APK Package...**", parse_mode="Markdown")
        
        await bot.send_chat_action(chat_id, action_type)
        await asyncio.sleep(1.8)
        
        # Stage 4: Finalizing
        if operation == "key":
            await status_msg.edit_text("✨ **Encrypting Key with Premium Protection...**", parse_mode="Markdown")
        else:
            await status_msg.edit_text("📦 **Packaging Premium Features...**", parse_mode="Markdown")
        
        await bot.send_chat_action(chat_id, action_type)
        await asyncio.sleep(1.3)
        
        # Stage 5: Ready to deliver
        if operation == "key":
            await status_msg.edit_text("🎯 **Premium Key Ready! Delivering Securely...**", parse_mode="Markdown")
        else:
            await status_msg.edit_text("🚀 **Premium APK Ready! Uploading Now...**", parse_mode="Markdown")
        
        await bot.send_chat_action(chat_id, action_type)
        await asyncio.sleep(1.0)
        
        # Delete status message
        await status_msg.delete()
        
    except Exception as e:
        logging.error(f"Animation error: {e}")

async def check_membership(user_id):
    if user_id == ADMIN_ID:
        return True

    if user_id in verified_users:
        return True

    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
            verified_users.add(user_id)
            save_data()
            return True
        else:
            if user_id in verified_users:
                verified_users.remove(user_id)
                save_data()
            return False
    except Exception as e:
        logging.error(f"Membership check error: {e}")
        return user_id in verified_users

def get_welcome_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Join Elite Channel", url="https://t.me/flex_public")],
        [InlineKeyboardButton(text="✅ Verify Premium Access", callback_data="verify")]
    ])

def get_content_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔐 Premium Key", callback_data="key"),
            InlineKeyboardButton(text="📱 Elite APK", callback_data="apk")
        ]
    ])

@dp.message(CommandStart())
async def start_handler(message: Message):
    user_ids.add(message.from_user.id)
    save_data()

    if message.from_user.id in blocked_users:
        await message.reply("🚫 **Access Permanently Denied**\n\n⛔ Your account has been restricted from accessing our premium services.")
        return

    user_name = message.from_user.first_name or "Elite User"

    welcome_text = f"""🎯 **Welcome to FlexBot Elite Services, {user_name}!** 🎯

🌟 **Exclusive Premium Access Portal**
⚡ **Advanced Graphics Tools & Premium Resources** 
🎮 **Elite BGMI Collections & Modifications**
🔐 **Secure Activation Systems**
🎨 **Professional Design Assets Library**

✨ **What Makes Us Special:**
• 🛡️ Military-grade security protocols
• ⚡ Lightning-fast content delivery
• 🎯 Personalized premium experience
• 🔄 Real-time updates & notifications
• 💎 VIP community access

🚀 **Ready to unlock the elite experience?**
📌 Join our exclusive premium channel first
🔓 Then verify your membership to access everything"""

    await message.reply(welcome_text, reply_markup=get_welcome_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "verify")
async def verify_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id

    if user_id in blocked_users:
        await callback_query.message.edit_text("🚫 **Access Permanently Denied**\n\n⛔ Your account has been restricted from accessing our services.")
        return

    is_member = await check_membership(user_id)

    if is_member:
        user_name = callback_query.from_user.first_name or "Elite Member"

        success_text = f"""🎉 **Welcome to the Elite Club, {user_name}!** 🎉

✅ **Premium Access Successfully Granted**
🔓 **All Elite Features Unlocked**
⭐ **VIP Community Access Activated**
🛡️ **Security Protocols Enabled**

🎯 **Your Premium Benefits:**
• 🔐 Instant activation keys
• 📱 Premium APK collections
• 🎨 Exclusive graphics packs
• ⚡ Priority support access
• 💎 Elite community perks

🚀 **Choose your premium content:**"""

        await callback_query.message.edit_text(success_text, reply_markup=get_content_kb(), parse_mode="Markdown")
    else:
        failure_text = """❌ **Verification Failed - Access Denied**

🔍 **Issue Detected:**
You are not currently a member of our premium channel.

📢 **Quick Resolution:**
1️⃣ Join our exclusive premium channel
2️⃣ Return here and click verify again
3️⃣ Enjoy instant access to all features

⚡ **Join now to unlock:**
• 🔐 Premium activation keys
• 📱 Elite APK collections  
• 🎨 Exclusive content library
• 💎 VIP community benefits"""

        await callback_query.message.edit_text(failure_text, reply_markup=get_welcome_kb(), parse_mode="Markdown")

@dp.callback_query(F.data == "key")
async def key_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id

    if user_id in blocked_users:
        await callback_query.message.edit_text("🚫 **Access Permanently Denied**")
        return

    if not await check_membership(user_id):
        await callback_query.message.edit_text(
            "❌ **Premium Access Required**\n\n🔐 Join our exclusive channel to unlock premium keys",
            reply_markup=get_welcome_kb(),
            parse_mode="Markdown"
        )
        return

    # Advanced key delivery with animation
    await advanced_typing_animation(user_id, ChatAction.TYPING, "key")

    try:
        with open("key.txt", "r", encoding="utf-8") as f:
            key_text = f.read().strip()

        # Enhanced key delivery message
        key_message = f"""🔐 **Premium Activation Key Delivered** 🔐

🎯 **Your Secure Key:**
`{key_text}`

✨ **Key Features:**
• 🛡️ Military-grade encryption
• ⚡ Instant activation capability
• 🔄 Universal compatibility
• 💎 Premium access unlocked

📋 **Instructions:**
1️⃣ Tap the key above to copy instantly
2️⃣ Paste in your application
3️⃣ Enjoy premium features immediately

🎉 **Thank you for choosing FlexBot Elite Services!**"""

        await bot.send_message(user_id, key_message, parse_mode="Markdown")

        # Send thank you message
        thanks_message = """🙏 **Thank You for Using Our Premium Services** 🙏

⭐ Your trust in FlexBot Elite is greatly appreciated!
💎 Share with friends to help them access premium content
🔄 Stay tuned for exciting updates and new features

🎯 **Need help?** Contact our VIP support team anytime!"""

        await asyncio.sleep(2)  # Small delay before thank you
        await bot.send_message(user_id, thanks_message, parse_mode="Markdown")

    except FileNotFoundError:
        await callback_query.message.reply("❌ **Premium Key Temporarily Unavailable**")

@dp.callback_query(F.data == "apk")
async def apk_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id

    if user_id in blocked_users:
        await callback_query.message.edit_text("🚫 **Access Permanently Denied**")
        return

    if not await check_membership(user_id):
        await callback_query.message.edit_text(
            "❌ **Premium Access Required**\n\n📱 Join our channel to download elite APK files",
            reply_markup=get_welcome_kb(),
            parse_mode="Markdown"
        )
        return

    # Advanced APK delivery with animation
    await advanced_typing_animation(user_id, ChatAction.UPLOAD_DOCUMENT, "apk")

    try:
        with open("apk_file_id.txt", "r") as f:
            file_id = f.read().strip()

        # Enhanced caption
        caption = "📱 **Premium Elite APK Collection**"
        try:
            with open("apk_caption.txt", "r", encoding="utf-8") as f:
                caption = f.read().strip()
        except FileNotFoundError:
            pass

        enhanced_caption = f"""{caption}

🎮 **Elite Gaming Experience Unlocked**
⚡ **Lightning-fast Performance**
🛡️ **Advanced Security Features**
💎 **VIP Access Included**

🙏 **Thank you for choosing FlexBot Elite Services!**
⭐ Rate us and share with gaming friends!"""

        await bot.send_document(user_id, file_id, caption=enhanced_caption)

        # Additional thank you message for APK downloads
        apk_thanks = """🎮 **Download Complete - Elite Gaming Awaits!** 🎮

🚀 **Installation Tips:**
• Enable unknown sources in settings
• Install with care and enjoy premium features
• Join our community for tips and tricks

💎 **VIP Gaming Experience Unlocked!**
🙏 Thank you for trusting FlexBot Elite Services!"""

        await asyncio.sleep(3)  # Delay for download completion
        await bot.send_message(user_id, apk_thanks, parse_mode="Markdown")

    except FileNotFoundError:
        await callback_query.message.reply("❌ **Elite APK Temporarily Unavailable**\n\n🔧 Our premium collection is being updated with new features.")

@dp.message(Command("setkey"))
async def setkey_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split(' ', 1)
    if len(args) < 2:
        await message.reply("**Usage:** `/setkey <premium_key_text>`")
        return

    with open("key.txt", "w", encoding="utf-8") as f:
        f.write(args[1])
    await message.reply("✅ **Premium Key Updated Successfully**\n\n🔐 New key is now active for all premium users.")

@dp.message(F.content_type == ContentType.DOCUMENT)
async def setapk_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.caption or not message.caption.startswith('/setapk'):
        return

    file_id = message.document.file_id
    caption = message.caption.replace('/setapk', '').strip() or "📱 Elite Premium Collection"

    with open("apk_file_id.txt", "w") as f:
        f.write(file_id)
    with open("apk_caption.txt", "w", encoding="utf-8") as f:
        f.write(caption)
    await message.reply("✅ **Elite APK Updated Successfully**\n\n📱 New premium package is now available for download.")

@dp.message(Command("broadcast"))
async def broadcast_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ **Admin Access Required**")
        return

    load_data()
    user_ids.add(ADMIN_ID)
    save_data()

    args = message.text.split(' ', 1)
    if len(args) < 2:
        await message.reply("""📢 **Advanced Broadcast System**

**Basic Broadcast:**
`/broadcast Your premium announcement`

**Enhanced Broadcast with Buttons:**
```
/broadcast 🚀 Major Update Available!

BUTTON:🔐 Get Key|key
BUTTON:📱 Download APK|apk
URL:📢 Join Channel|https://t.me/flex_public
URL:💎 VIP Support|https://t.me/support
```

**Professional Example:**
```
/broadcast 🎯 FlexBot Elite Services Launch!
Experience the next level of premium gaming.

BUTTON:⚡ Premium Key|key
BUTTON:🎮 Elite APK|apk
URL:🚀 Join Now|https://t.me/flex_public
```""", parse_mode="Markdown")
        return

    content = args[1]
    lines = content.split('\n')
    text = ""
    buttons = []

    for line in lines:
        line = line.strip()
        if line.startswith('BUTTON:') and '|' in line:
            try:
                _, rest = line.split(':', 1)
                btn_text, btn_data = rest.split('|', 1)
                buttons.append(InlineKeyboardButton(text=btn_text.strip(), callback_data=f"bc_{btn_data.strip()}"))
            except:
                pass
        elif line.startswith('URL:') and '|' in line:
            try:
                _, rest = line.split(':', 1)
                btn_text, btn_url = rest.split('|', 1)
                buttons.append(InlineKeyboardButton(text=btn_text.strip(), url=btn_url.strip()))
            except:
                pass
        else:
            if line:
                text += line + '\n'

    text = text.strip()
    if not text:
        await message.reply("❌ **Empty broadcast message**")
        return

    keyboard = None
    if buttons:
        rows = []
        for i in range(0, len(buttons), 2):
            rows.append(buttons[i:i+2])
        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

    sent = 0
    failed = 0

    status = await message.reply("📡 **Elite Broadcast System Activated...**")

    for uid in user_ids:
        if uid in blocked_users:
            continue
        try:
            if keyboard:
                await bot.send_message(uid, text, parse_mode="Markdown", reply_markup=keyboard)
            else:
                await bot.send_message(uid, text, parse_mode="Markdown")
            sent += 1
        except:
            failed += 1
        await asyncio.sleep(0.05)

    await status.edit_text(f"""📡 **Elite Broadcast Complete**

✅ **Successfully delivered:** {sent}
❌ **Failed deliveries:** {failed}
🎯 **Success rate:** {(sent/(sent+failed)*100) if (sent+failed) > 0 else 0:.1f}%

💎 **Premium messaging system performance optimized!**""")

@dp.callback_query(F.data.startswith("bc_"))
async def broadcast_callback_handler(callback_query: CallbackQuery):
    await callback_query.answer("⚡ Processing elite request...")
    data = callback_query.data[3:]
    user_id = callback_query.from_user.id

    if data == "key":
        if user_id in blocked_users:
            await callback_query.message.reply("🚫 **Access Denied**")
            return

        if not await check_membership(user_id):
            await callback_query.message.reply("❌ **Premium Required**", reply_markup=get_welcome_kb())
            return

        await advanced_typing_animation(user_id, ChatAction.TYPING, "key")

        try:
            with open("key.txt", "r", encoding="utf-8") as f:
                key_text = f.read().strip()
            await bot.send_message(user_id, f"🔐 **Elite Key from Broadcast**\n\n`{key_text}`\n\n✨ **Delivered via premium broadcast system!**", parse_mode="Markdown")
        except FileNotFoundError:
            await callback_query.message.reply("❌ **Key temporarily unavailable**")

    elif data == "apk":
        if user_id in blocked_users:
            await callback_query.message.reply("🚫 **Access Denied**")
            return

        if not await check_membership(user_id):
            await callback_query.message.reply("❌ **Premium Required**", reply_markup=get_welcome_kb())
            return

        await advanced_typing_animation(user_id, ChatAction.UPLOAD_DOCUMENT, "apk")

        try:
            with open("apk_file_id.txt", "r") as f:
                file_id = f.read().strip()
            with open("apk_caption.txt", "r", encoding="utf-8") as f:
                caption = f.read().strip()
            await bot.send_document(user_id, file_id, caption=caption + "\n\n📱 **Delivered via elite broadcast!**")
        except FileNotFoundError:
            await callback_query.message.reply("❌ **APK temporarily unavailable**")
    else:
        await callback_query.message.reply(f"✅ **Elite Action Completed:** {data}")

@dp.message(Command("block"))
async def block_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("**Usage:** `/block <user_id>`")
        return

    try:
        uid = int(args[1])
        blocked_users.add(uid)
        if uid in verified_users:
            verified_users.remove(uid)
        save_data()
        await message.reply(f"✅ **User {uid} permanently blocked from elite services**")
    except ValueError:
        await message.reply("❌ **Invalid user ID format**")

@dp.message(Command("unblock"))
async def unblock_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("**Usage:** `/unblock <user_id>`")
        return

    try:
        uid = int(args[1])
        if uid in blocked_users:
            blocked_users.remove(uid)
            save_data()
            await message.reply(f"✅ **User {uid} restored to elite services**")
        else:
            await message.reply("**User was not blocked**")
    except ValueError:
        await message.reply("❌ **Invalid user ID format**")

@dp.message(Command("help"))
async def help_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.reply("""🔧 **Elite Admin Command Center**

**🔐 Content Management:**
• `/setkey <text>` - Update premium key
• `/setapk` - Upload elite APK collection

**📢 Broadcast System:**
• `/broadcast <message>` - Send to all users
• Advanced button support with BUTTON: and URL: format

**👥 User Management:**
• `/block <id>` - Block user from services
• `/unblock <id>` - Restore user access

💎 **Elite administrative tools at your command!**""", parse_mode="Markdown")

@dp.message(F.text)
async def text_handler(message: Message):
    text = message.text.lower()
    user_id = message.from_user.id

    if user_id in blocked_users:
        return

    if any(w in text for w in ['key', 'activation', 'code']):
        if not await check_membership(user_id):
            await message.reply("❌ **Elite Premium Required**", reply_markup=get_welcome_kb())
            return

        await advanced_typing_animation(user_id, ChatAction.TYPING, "key")

        try:
            with open("key.txt", "r", encoding="utf-8") as f:
                key_text = f.read().strip()
            await message.reply(f"🔐 **Premium Elite Key**\n\n`{key_text}`\n\n💎 **Enjoy your elite experience!**", parse_mode="Markdown")
        except FileNotFoundError:
            await message.reply("❌ **Key temporarily unavailable**")

    elif any(w in text for w in ['apk', 'app', 'download']):
        if not await check_membership(user_id):
            await message.reply("❌ **Elite Premium Required**", reply_markup=get_welcome_kb())
            return

        await advanced_typing_animation(user_id, ChatAction.UPLOAD_DOCUMENT, "apk")

        try:
            with open("apk_file_id.txt", "r") as f:
                file_id = f.read().strip()
            with open("apk_caption.txt", "r", encoding="utf-8") as f:
                caption = f.read().strip()
            await bot.send_document(user_id, file_id, caption=caption + "\n\n🎮 **Elite gaming experience unlocked!**")
        except FileNotFoundError:
            await message.reply("❌ **APK temporarily unavailable**")
    else:
        await message.reply("🎯 **Elite Services Available**", reply_markup=get_content_kb())

def signal_handler(signum, frame):
    print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
    save_data()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

async def main():
    print("🤖 FlexBot Elite Services Started")
    print(f"📢 Elite Channel: {CHANNEL_ID}")
    print(f"🔑 Admin: {ADMIN_ID}")
    print(f"👥 Elite Users: {len(user_ids)}")
    print("✅ Advanced features enabled")

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("🛑 Keyboard interrupt")
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Bot error: {e}")
    finally:
        save_data()
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Stopped")
    finally:
        save_data()