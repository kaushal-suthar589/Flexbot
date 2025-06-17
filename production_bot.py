#!/usr/bin/env python3
import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums import ContentType, ChatMemberStatus

# Configuration
API_TOKEN = "7686244968:AAHb1w8ybeNmRqEpmeTnX24dDkeGS6PUm8M"
ADMIN_ID = 7201285915
CHANNEL_ID = "@flex_public"

# Global data
users = set()
blocked = set()
verified = set()

def load_users():
    global users, blocked, verified
    try:
        with open("user_ids.txt", "r") as f:
            users = {int(line.strip()) for line in f if line.strip()}
    except:
        users = set()
    
    try:
        with open("blocked_users.txt", "r") as f:
            blocked = {int(line.strip()) for line in f if line.strip()}
    except:
        blocked = set()
    
    try:
        with open("verified_users.txt", "r") as f:
            verified = {int(line.strip()) for line in f if line.strip()}
    except:
        verified = set()

def save_users():
    try:
        with open("user_ids.txt", "w") as f:
            for u in users:
                f.write(f"{u}\n")
        
        with open("blocked_users.txt", "w") as f:
            for u in blocked:
                f.write(f"{u}\n")
        
        with open("verified_users.txt", "w") as f:
            for u in verified:
                f.write(f"{u}\n")
    except Exception as e:
        print(f"Save error: {e}")

load_users()

# Bot setup
logging.basicConfig(level=logging.WARNING)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def is_member(user_id):
    if user_id == ADMIN_ID:
        return True
    
    if user_id in verified:
        return True
    
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
            verified.add(user_id)
            save_users()
            return True
        else:
            if user_id in verified:
                verified.remove(user_id)
                save_users()
            return False
    except:
        return user_id in verified

def welcome_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Join Channel", url="https://t.me/flex_public")],
        [InlineKeyboardButton(text="✅ Verify", callback_data="verify")]
    ])

def content_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔐 Key", callback_data="key"),
            InlineKeyboardButton(text="📱 APK", callback_data="apk")
        ]
    ])

@dp.message(CommandStart())
async def start(message: Message):
    users.add(message.from_user.id)
    save_users()
    
    if message.from_user.id in blocked:
        await message.reply("Access Denied")
        return
    
    text = "FlexBot Premium\n\nPremium Content Access\nGraphics Tools\nBGMI Collections\n\nJoin channel → Verify"
    await message.reply(text, reply_markup=welcome_kb())

@dp.callback_query(F.data == "verify")
async def verify(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    if user_id in blocked:
        await callback_query.message.edit_text("Access Denied")
        return
    
    member = await is_member(user_id)
    
    if member:
        text = "Access Granted\n\nPremium Unlocked\nElite Community\n\nChoose:"
        await callback_query.message.edit_text(text, reply_markup=content_kb())
    else:
        text = "Verification Failed\n\nJoin channel first → Then verify"
        await callback_query.message.edit_text(text, reply_markup=welcome_kb())

@dp.callback_query(F.data == "key")
async def key(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    if user_id in blocked:
        await callback_query.message.edit_text("Access Denied")
        return
    
    if not await is_member(user_id):
        text = "Premium Required\n\nJoin channel first"
        await callback_query.message.edit_text(text, reply_markup=welcome_kb())
        return
    
    try:
        with open("key.txt", "r", encoding="utf-8") as f:
            key_text = f.read().strip()
        await bot.send_message(user_id, f"Premium Key\n\n{key_text}")
    except:
        await callback_query.message.reply("Key unavailable")

@dp.callback_query(F.data == "apk")
async def apk(callback_query: CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    if user_id in blocked:
        await callback_query.message.edit_text("Access Denied")
        return
    
    if not await is_member(user_id):
        text = "Premium Required\n\nJoin channel first"
        await callback_query.message.edit_text(text, reply_markup=welcome_kb())
        return
    
    try:
        with open("apk_file_id.txt", "r") as f:
            file_id = f.read().strip()
        
        caption = "BGMI Premium"
        try:
            with open("apk_caption.txt", "r", encoding="utf-8") as f:
                caption = f.read().strip()
        except:
            pass
        
        await bot.send_document(user_id, file_id, caption=caption)
    except:
        await callback_query.message.reply("APK unavailable")

@dp.message(Command("setkey"))
async def setkey(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split(' ', 1)
    if len(args) < 2:
        await message.reply("Usage: /setkey <text>")
        return
    
    with open("key.txt", "w", encoding="utf-8") as f:
        f.write(args[1])
    await message.reply("Key Updated")

@dp.message(F.content_type == ContentType.DOCUMENT)
async def setapk(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    if not message.caption or not message.caption.startswith('/setapk'):
        return
    
    file_id = message.document.file_id
    caption = message.caption.replace('/setapk', '').strip() or "BGMI Premium"
    
    with open("apk_file_id.txt", "w") as f:
        f.write(file_id)
    with open("apk_caption.txt", "w", encoding="utf-8") as f:
        f.write(caption)
    await message.reply("APK Updated")

@dp.message(Command("broadcast"))
async def broadcast(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("Admin only")
        return
    
    load_users()
    users.add(ADMIN_ID)
    save_users()
    
    args = message.text.split(' ', 1)
    if len(args) < 2:
        text = """Broadcast System

Basic:
/broadcast Message here

With Buttons:
/broadcast Message

BUTTON:Text|callback
URL:Text|https://link

Example:
/broadcast Update!

BUTTON:Key|key
URL:Channel|https://t.me/flex_public"""
        await message.reply(text)
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
        await message.reply("Empty message")
        return
    
    keyboard = None
    if buttons:
        rows = []
        for i in range(0, len(buttons), 2):
            rows.append(buttons[i:i+2])
        keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    
    sent = 0
    failed = 0
    status = await message.reply("Broadcasting...")
    
    for uid in users:
        if uid in blocked:
            continue
        try:
            if keyboard:
                await bot.send_message(uid, text, reply_markup=keyboard)
            else:
                await bot.send_message(uid, text)
            sent += 1
        except:
            failed += 1
        await asyncio.sleep(0.05)
    
    await status.edit_text(f"Complete\n\nSent: {sent}\nFailed: {failed}")

@dp.callback_query(F.data.startswith("bc_"))
async def broadcast_cb(callback_query: CallbackQuery):
    await callback_query.answer("Processing...")
    data = callback_query.data[3:]
    user_id = callback_query.from_user.id
    
    if data == "key":
        if user_id in blocked or not await is_member(user_id):
            await callback_query.message.reply("Access Required", reply_markup=welcome_kb())
            return
        
        try:
            with open("key.txt", "r", encoding="utf-8") as f:
                key_text = f.read().strip()
            await bot.send_message(user_id, f"Key\n\n{key_text}")
        except:
            await callback_query.message.reply("Key unavailable")
    
    elif data == "apk":
        if user_id in blocked or not await is_member(user_id):
            await callback_query.message.reply("Access Required", reply_markup=welcome_kb())
            return
        
        try:
            with open("apk_file_id.txt", "r") as f:
                file_id = f.read().strip()
            with open("apk_caption.txt", "r", encoding="utf-8") as f:
                caption = f.read().strip()
            await bot.send_document(user_id, file_id, caption=caption)
        except:
            await callback_query.message.reply("APK unavailable")
    else:
        await callback_query.message.reply(f"Action: {data}")

@dp.message(Command("block"))
async def block(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage: /block <user_id>")
        return
    
    try:
        uid = int(args[1])
        blocked.add(uid)
        if uid in verified:
            verified.remove(uid)
        save_users()
        await message.reply(f"Blocked {uid}")
    except:
        await message.reply("Invalid ID")

@dp.message(Command("unblock"))
async def unblock(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage: /unblock <user_id>")
        return
    
    try:
        uid = int(args[1])
        if uid in blocked:
            blocked.remove(uid)
            save_users()
            await message.reply(f"Unblocked {uid}")
        else:
            await message.reply("User not blocked")
    except:
        await message.reply("Invalid ID")

@dp.message(Command("status"))
async def status(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    text = f"""Bot Status

Online: Yes
Users: {len(users)}
Verified: {len(verified)}
Blocked: {len(blocked)}
Channel: {CHANNEL_ID}
Admin: {ADMIN_ID}"""
    
    await message.reply(text)

@dp.message(F.text)
async def text_handler(message: Message):
    text = message.text.lower()
    user_id = message.from_user.id
    
    if user_id in blocked:
        return
    
    if any(w in text for w in ['key', 'activation', 'code']):
        if not await is_member(user_id):
            await message.reply("Premium Required", reply_markup=welcome_kb())
            return
        
        try:
            with open("key.txt", "r", encoding="utf-8") as f:
                key_text = f.read().strip()
            await message.reply(f"Key\n\n{key_text}")
        except:
            await message.reply("Key unavailable")
    
    elif any(w in text for w in ['apk', 'app', 'download']):
        if not await is_member(user_id):
            await message.reply("Premium Required", reply_markup=welcome_kb())
            return
        
        try:
            with open("apk_file_id.txt", "r") as f:
                file_id = f.read().strip()
            with open("apk_caption.txt", "r", encoding="utf-8") as f:
                caption = f.read().strip()
            await bot.send_document(user_id, file_id, caption=caption)
        except:
            await message.reply("APK unavailable")
    else:
        await message.reply("How can I help?", reply_markup=content_kb())

async def main():
    print("FlexBot Started - Production Mode")
    print(f"Channel: {CHANNEL_ID}")
    print(f"Admin: {ADMIN_ID}")
    print(f"Users: {len(users)}")
    print("24/7 Hosting Active")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Error: {e}")
        await asyncio.sleep(5)
        # Restart on error
        os.execv(sys.executable, ['python'] + sys.argv)
    finally:
        save_users()
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        save_users()