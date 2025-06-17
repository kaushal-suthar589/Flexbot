import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums import ContentType, ChatMemberStatus

# Configuration
API_TOKEN = "7686244968:AAHb1w8ybeNmRqEpmeTnX24dDkeGS6PUm8M"
ADMIN_ID = 7201285915
CHANNEL_ID = "@flex_public"

# Data storage
user_ids = set()
blocked_users = set()
verified_users = set()

def load_data():
    global user_ids, blocked_users, verified_users
    try:
        with open("user_ids.txt", "r") as f:
            user_ids = {int(line.strip()) for line in f if line.strip()}
    except:
        user_ids = set()
    
    try:
        with open("blocked_users.txt", "r") as f:
            blocked_users = {int(line.strip()) for line in f if line.strip()}
    except:
        blocked_users = set()
    
    try:
        with open("verified_users.txt", "r") as f:
            verified_users = {int(line.strip()) for line in f if line.strip()}
    except:
        verified_users = set()

def save_data():
    try:
        with open("user_ids.txt", "w") as f:
            for uid in user_ids:
                f.write(f"{uid}\n")
        
        with open("blocked_users.txt", "w") as f:
            for uid in blocked_users:
                f.write(f"{uid}\n")
        
        with open("verified_users.txt", "w") as f:
            for uid in verified_users:
                f.write(f"{uid}\n")
    except Exception as e:
        print(f"Save error: {e}")

load_data()

# Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

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
    except:
        return user_id in verified_users

def welcome_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Join Channel", url="https://t.me/flex_public")],
        [InlineKeyboardButton(text="✅ Verify", callback_data="verify")]
    ])

def content_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔐 Key", callback_data="key"),
            InlineKeyboardButton(text="📱 APK", callback_data="apk")
        ]
    ])

@dp.message(CommandStart())
async def start_cmd(message: Message):
    user_ids.add(message.from_user.id)
    save_data()
    
    if message.from_user.id in blocked_users:
        await message.reply("🚫 Access Denied")
        return
    
    text = "🎯 **FlexBot Premium**\n\n🌟 Premium Content\n🔐 Graphics Tools\n📱 BGMI Collections\n\n📌 Join channel → Verify"
    await message.reply(text, reply_markup=welcome_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "verify")
async def verify_cb(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    if user_id in blocked_users:
        await callback_query.message.edit_text("🚫 Access Denied")
        return
    
    is_member = await check_membership(user_id)
    
    if is_member:
        text = "🎉 **Access Granted**\n\n✅ Premium Unlocked\n⭐ Elite Community\n\nChoose:"
        await callback_query.message.edit_text(text, reply_markup=content_keyboard(), parse_mode="Markdown")
    else:
        text = "❌ **Failed**\n\nJoin channel first → Then verify"
        await callback_query.message.edit_text(text, reply_markup=welcome_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "key")
async def key_cb(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    if user_id in blocked_users:
        await callback_query.message.edit_text("🚫 Access Denied")
        return
    
    if not await check_membership(user_id):
        text = "❌ Premium Required\n\nJoin channel first"
        await callback_query.message.edit_text(text, reply_markup=welcome_keyboard(), parse_mode="Markdown")
        return
    
    try:
        with open("key.txt", "r", encoding="utf-8") as f:
            key_text = f.read().strip()
        await bot.send_message(user_id, f"🔐 **Premium Key**\n\n`{key_text}`", parse_mode="Markdown")
    except:
        await callback_query.message.reply("❌ Key unavailable")

@dp.callback_query(F.data == "apk")
async def apk_cb(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    if user_id in blocked_users:
        await callback_query.message.edit_text("🚫 Access Denied")
        return
    
    if not await check_membership(user_id):
        text = "❌ Premium Required\n\nJoin channel first"
        await callback_query.message.edit_text(text, reply_markup=welcome_keyboard(), parse_mode="Markdown")
        return
    
    try:
        with open("apk_file_id.txt", "r") as f:
            file_id = f.read().strip()
        
        caption = "📱 BGMI Premium"
        try:
            with open("apk_caption.txt", "r", encoding="utf-8") as f:
                caption = f.read().strip()
        except:
            pass
        
        await bot.send_document(user_id, file_id, caption=caption)
    except:
        await callback_query.message.reply("❌ APK unavailable")

@dp.message(Command("setkey"))
async def setkey_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split(' ', 1)
    if len(args) < 2:
        await message.reply("Usage: /setkey <text>")
        return
    
    with open("key.txt", "w", encoding="utf-8") as f:
        f.write(args[1])
    await message.reply("✅ Key Updated")

@dp.message(F.content_type == ContentType.DOCUMENT)
async def setapk_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    if not message.caption or not message.caption.startswith('/setapk'):
        return
    
    file_id = message.document.file_id
    caption = message.caption.replace('/setapk', '').strip() or "📱 BGMI Premium"
    
    with open("apk_file_id.txt", "w") as f:
        f.write(file_id)
    with open("apk_caption.txt", "w", encoding="utf-8") as f:
        f.write(caption)
    await message.reply("✅ APK Updated")

@dp.message(Command("broadcast"))
async def broadcast_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ Admin only")
        return
    
    load_data()
    user_ids.add(ADMIN_ID)
    save_data()
    
    args = message.text.split(' ', 1)
    if len(args) < 2:
        text = """📢 **Broadcast**

**Basic:**
`/broadcast Message here`

**With Buttons:**
```
/broadcast Message

BUTTON:Text|callback
URL:Text|https://link
```

**Example:**
```
/broadcast 🚀 Update!

BUTTON:🔐 Key|key
URL:📢 Channel|https://t.me/flex_public
```"""
        await message.reply(text, parse_mode="Markdown")
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
        await message.reply("❌ Empty message")
        return
    
    keyboard = None
    if buttons:
        rows = []
        for i in range(0, len(buttons), 2):
            rows.append(buttons[i:i+2])
        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    
    sent = 0
    failed = 0
    status = await message.reply("📡 Broadcasting...")
    
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
    
    await status.edit_text(f"📡 **Complete**\n\n✅ Sent: {sent}\n❌ Failed: {failed}")

@dp.callback_query(F.data.startswith("bc_"))
async def broadcast_cb(callback_query: CallbackQuery):
    await callback_query.answer("Processing...")
    data = callback_query.data[3:]
    user_id = callback_query.from_user.id
    
    if data == "key":
        if user_id in blocked_users or not await check_membership(user_id):
            await callback_query.message.reply("❌ Access Required", reply_markup=welcome_keyboard())
            return
        
        try:
            with open("key.txt", "r", encoding="utf-8") as f:
                key_text = f.read().strip()
            await bot.send_message(user_id, f"🔐 **Key**\n\n`{key_text}`", parse_mode="Markdown")
        except:
            await callback_query.message.reply("❌ Key unavailable")
    
    elif data == "apk":
        if user_id in blocked_users or not await check_membership(user_id):
            await callback_query.message.reply("❌ Access Required", reply_markup=welcome_keyboard())
            return
        
        try:
            with open("apk_file_id.txt", "r") as f:
                file_id = f.read().strip()
            with open("apk_caption.txt", "r", encoding="utf-8") as f:
                caption = f.read().strip()
            await bot.send_document(user_id, file_id, caption=caption)
        except:
            await callback_query.message.reply("❌ APK unavailable")
    else:
        await callback_query.message.reply(f"✅ Action: {data}")

@dp.message(Command("block"))
async def block_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage: /block <user_id>")
        return
    
    try:
        uid = int(args[1])
        blocked_users.add(uid)
        if uid in verified_users:
            verified_users.remove(uid)
        save_data()
        await message.reply(f"✅ Blocked {uid}")
    except:
        await message.reply("❌ Invalid ID")

@dp.message(Command("unblock"))
async def unblock_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage: /unblock <user_id>")
        return
    
    try:
        uid = int(args[1])
        if uid in blocked_users:
            blocked_users.remove(uid)
            save_data()
            await message.reply(f"✅ Unblocked {uid}")
        else:
            await message.reply("User not blocked")
    except:
        await message.reply("❌ Invalid ID")

@dp.message(Command("help"))
async def help_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    text = """🔧 **Admin Commands**

**Content:**
• /setkey <text> - Set key
• /setapk - Upload APK

**Broadcast:**
• /broadcast <message> - Send to all
• Supports BUTTON: and URL: format

**Users:**
• /block <id> - Block user
• /unblock <id> - Unblock user"""
    
    await message.reply(text, parse_mode="Markdown")

@dp.message(F.text)
async def text_handler(message: Message):
    text = message.text.lower()
    user_id = message.from_user.id
    
    if user_id in blocked_users:
        return
    
    if any(w in text for w in ['key', 'activation', 'code']):
        if not await check_membership(user_id):
            await message.reply("❌ Premium Required", reply_markup=welcome_keyboard())
            return
        
        try:
            with open("key.txt", "r", encoding="utf-8") as f:
                key_text = f.read().strip()
            await message.reply(f"🔐 **Key**\n\n`{key_text}`", parse_mode="Markdown")
        except:
            await message.reply("❌ Key unavailable")
    
    elif any(w in text for w in ['apk', 'app', 'download']):
        if not await check_membership(user_id):
            await message.reply("❌ Premium Required", reply_markup=welcome_keyboard())
            return
        
        try:
            with open("apk_file_id.txt", "r") as f:
                file_id = f.read().strip()
            with open("apk_caption.txt", "r", encoding="utf-8") as f:
                caption = f.read().strip()
            await bot.send_document(user_id, file_id, caption=caption)
        except:
            await message.reply("❌ APK unavailable")
    else:
        await message.reply("🎯 **How can I help?**", reply_markup=content_keyboard())

async def main():
    print("🤖 FlexBot Starting...")
    print(f"📢 Channel: {CHANNEL_ID}")
    print(f"🔑 Admin: {ADMIN_ID}")
    print(f"👥 Users: {len(user_ids)}")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        save_data()
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        save_data()