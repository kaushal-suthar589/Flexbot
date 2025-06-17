import asyncio
import logging
import os
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums import ContentType, ChatMemberStatus, ChatAction

# Configuration
API_TOKEN = "7686244968:AAHb1w8ybeNmRqEpmeTnX24dDkeGS6PUm8M"
ADMIN_ID = 7201285915  # Your actual Telegram User ID
CHANNEL_USERNAME = "@flex_public"
CHANNEL_ID = "@flex_public"

# Global variables for user management
user_ids = set()
blocked_users = set()
verified_users = set()

def load_blocked_users():
    global blocked_users
    try:
        with open("blocked_users.txt", "r") as f:
            blocked_users = {int(line.strip()) for line in f if line.strip()}
    except FileNotFoundError:
        blocked_users = set()

def save_blocked_users():
    with open("blocked_users.txt", "w") as f:
        for user_id in blocked_users:
            f.write(f"{user_id}\n")

def load_verified_users():
    global verified_users
    try:
        with open("verified_users.txt", "r") as f:
            verified_users = {int(line.strip()) for line in f if line.strip()}
    except FileNotFoundError:
        verified_users = set()

def save_verified_users():
    with open("verified_users.txt", "w") as f:
        for user_id in verified_users:
            f.write(f"{user_id}\n")

def save_user_ids():
    with open("user_ids.txt", "w") as f:
        for user_id in user_ids:
            f.write(f"{user_id}\n")

def load_user_ids():
    global user_ids
    try:
        with open("user_ids.txt", "r") as f:
            user_ids = {int(line.strip()) for line in f if line.strip()}
    except FileNotFoundError:
        user_ids = set()

# Load all data on startup
load_blocked_users()
load_verified_users()
load_user_ids()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize bot
if not API_TOKEN:
    print("❌ BOT_TOKEN environment variable not configured!")
    exit(1)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def show_typing_animation(chat_id: int, action_type: ChatAction = ChatAction.TYPING):
    """Show typing animation for 5 seconds with periodic updates"""
    try:
        # Send initial status message
        if action_type == ChatAction.TYPING:
            status_msg = await bot.send_message(chat_id, "🔄 **Processing your request...**", parse_mode="Markdown")
        else:
            status_msg = await bot.send_message(chat_id, "📤 **Preparing your download...**", parse_mode="Markdown")
        
        # Show typing animation for 5 seconds
        await bot.send_chat_action(chat_id, action_type)
        await asyncio.sleep(1.5)
        
        # Update status message
        if action_type == ChatAction.TYPING:
            await status_msg.edit_text("🔐 **Generating activation key...**", parse_mode="Markdown")
        else:
            await status_msg.edit_text("📱 **Fetching premium APK...**", parse_mode="Markdown")
        
        await bot.send_chat_action(chat_id, action_type)
        await asyncio.sleep(1.5)
        
        # Final status update
        if action_type == ChatAction.TYPING:
            await status_msg.edit_text("✅ **Key ready! Sending now...**", parse_mode="Markdown")
        else:
            await status_msg.edit_text("✅ **APK ready! Uploading now...**", parse_mode="Markdown")
        
        await bot.send_chat_action(chat_id, action_type)
        await asyncio.sleep(1)
        
        # Delete status message after animation
        await status_msg.delete()
        
    except Exception as e:
        logging.error(f"Error showing typing animation: {e}")

async def check_channel_membership(user_id):
    try:
        # Admin always has access
        if user_id == ADMIN_ID:
            print(f"✅ Admin access granted for ID: {user_id}")
            return True
        
        # For testing: if channel is @flex_public, temporarily allow all users
        print(f"🔍 Checking membership for user {user_id} in channel {CHANNEL_ID}")
        
        try:
            member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
            print(f"🔍 Member status: {member.status}")
            
            if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
                print(f"✅ User {user_id} is a valid member")
                return True
            else:
                print(f"❌ User {user_id} is not a member. Status: {member.status}")
                if user_id in verified_users:
                    verified_users.remove(user_id)
                    save_verified_users()
                return False
                
        except Exception as e:
            print(f"⚠️ API Error checking membership for {user_id}: {e}")
            # Fallback: check if user was previously verified
            is_verified = user_id in verified_users
            print(f"🔍 Fallback verification status: {is_verified}")
            return is_verified
            
    except Exception as e:
        print(f"❌ Critical error in membership check: {e}")
        return False

def get_welcome_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🚀 Join Premium Channel", url="https://t.me/flex_public")],
        [InlineKeyboardButton(text="✅ Verify Membership", callback_data="check_joined")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_content_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="🔐 Get Activation Key", callback_data="get_key"),
            InlineKeyboardButton(text="📱 BGMI APK", callback_data="get_apk")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(CommandStart())
async def send_welcome(message: Message):
    user_ids.add(message.from_user.id)
    save_user_ids()
    
    # Debug: Print user ID to console
    print(f"🔍 DEBUG: User {message.from_user.first_name} ID: {message.from_user.id}")
    
    if message.from_user.id in blocked_users:
        await message.reply("🚫 **Access Denied**\n\nYour account has been restricted from using this service.")
        return
    
    welcome_text = """🎯 **Welcome to FlexBot Premium Services** 🎯

🌟 **Exclusive Access to Premium Content**
🔐 **Advanced Graphics Tools & Resources** 
📱 **Latest BGMI Premium Collections**
🎨 **Cutting-Edge Design Assets**

⚡ **To Access Premium Features:**
📌 Join our exclusive channel to unlock premium content
🔓 Verify your membership to proceed"""
    
    await message.reply(welcome_text, reply_markup=get_welcome_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "check_joined")
async def check_joined(callback_query: CallbackQuery):
    try:
        await callback_query.answer()
    except Exception:
        pass  # Ignore old callback errors
    user_id = callback_query.from_user.id
    
    if user_id in blocked_users:
        await callback_query.message.edit_text("🚫 **Access Denied**\n\nYour account has been restricted from accessing this service.")
        return
    
    is_member = await check_channel_membership(user_id)
    
    if is_member:
        verified_users.add(user_id)
        save_verified_users()
        
        thank_you_text = """🎉 **Membership Verified Successfully** 🎉

✅ **Premium Access Granted**
🔓 **All Features Unlocked**
⭐ **Welcome to the Elite Community**

Choose your desired content:"""
        
        try:
            await callback_query.message.edit_text(thank_you_text, reply_markup=get_content_keyboard(), parse_mode="Markdown")
        except Exception:
            # Message already updated, ignore duplicate requests
            pass
    else:
        not_joined_text = """❌ **Membership Verification Failed**

📢 Please join our premium channel first to access exclusive content.
🔄 After joining, click "✅ Verify Membership" to proceed."""
        
        await callback_query.message.edit_text(not_joined_text, reply_markup=get_welcome_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "get_key")
async def get_key(callback_query: CallbackQuery):
    try:
        await callback_query.answer()
    except Exception:
        pass
    user_id = callback_query.from_user.id
    
    if user_id in blocked_users:
        await callback_query.message.edit_text("🚫 **Access Denied**\n\nYour account has been restricted from accessing this service.")
        return
    
    is_member = await check_channel_membership(user_id)
    
    if not is_member:
        notice_text = """❌ **Premium Membership Required**

📢 You must be a member of our premium channel to access activation keys.
🔗 Please rejoin the channel and verify your membership."""
        
        await callback_query.message.edit_text(notice_text, reply_markup=get_welcome_keyboard(), parse_mode="Markdown")
        return
    
    # Show "Bot is generating your key..." animation
    await show_typing_animation(user_id, ChatAction.TYPING)
    
    try:
        with open("key.txt", "r", encoding="utf-8") as f:
            key_text = f.read().strip()
        
        # Send key as new message instead of reply to avoid conflicts
        await bot.send_message(user_id, f"🔐 **Premium Activation Key**\n\n`{key_text}`\n\n✅ Tap the key above to copy it instantly!\n\n🎯 Use this key to unlock premium features.", parse_mode="Markdown")
    except FileNotFoundError:
        await callback_query.message.reply("❌ **Key Currently Unavailable**\n\nThe activation key is being updated. Please try again in a few moments.")

@dp.callback_query(F.data == "get_apk")
async def get_apk(callback_query: CallbackQuery):
    try:
        await callback_query.answer()
    except Exception:
        pass
    user_id = callback_query.from_user.id
    
    if user_id in blocked_users:
        await callback_query.message.edit_text("🚫 **Access Denied**\n\nYour account has been restricted from accessing this service.")
        return
    
    is_member = await check_channel_membership(user_id)
    
    if not is_member:
        notice_text = """❌ **Premium Membership Required**

📢 You must be a member of our premium channel to download APK files.
🔗 Please rejoin the channel and verify your membership."""
        
        await callback_query.message.edit_text(notice_text, reply_markup=get_welcome_keyboard(), parse_mode="Markdown")
        return
    
    # Show "Bot is preparing your APK..." animation
    await show_typing_animation(user_id, ChatAction.UPLOAD_DOCUMENT)
    
    try:
        with open("apk_file_id.txt", "r") as f:
            file_id = f.read().strip()
        
        try:
            with open("apk_caption.txt", "r", encoding="utf-8") as f:
                caption = f.read().strip()
        except FileNotFoundError:
            caption = "📱 BGMI Premium Collection"
        
        await bot.send_document(user_id, file_id, caption=caption)
    except FileNotFoundError:
        await callback_query.message.reply("❌ **APK Currently Unavailable**\n\nThe premium APK is being updated with new features. Please check back shortly.")
    except Exception as e:
        await callback_query.message.reply("❌ **Download Error**\n\nThere was a temporary issue with the download. Please try again.")

@dp.message(Command("setkey"))
async def set_key(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    if not message.text:
        await message.reply("**Usage:** `/setkey Your Premium Key Text`")
        return
    
    command_args = message.text.split(' ', 1)
    key_text = command_args[1] if len(command_args) > 1 else ""
    
    if not key_text:
        await message.reply("**Usage:** `/setkey Your Premium Key Text`")
        return
        
    with open("key.txt", "w", encoding="utf-8") as f:
        f.write(key_text)
    await message.reply("✅ **Activation Key Updated Successfully**")

@dp.message(F.content_type == ContentType.DOCUMENT)
async def set_apk(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.caption or not message.caption.startswith('/setapk'):
        return

    file = message.document
    file_id = file.file_id
    caption = message.caption.replace('/setapk', '').strip() or "📱 BGMI Premium Collection"
    
    with open("apk_file_id.txt", "w") as f:
        f.write(file_id)
    with open("apk_caption.txt", "w", encoding="utf-8") as f:
        f.write(caption)
    await message.reply("✅ **Premium APK Updated Successfully**")

@dp.message(Command("broadcast"))
async def broadcast_message(message: Message):
    print(f"🔍 BROADCAST DEBUG: Your ID: {message.from_user.id}, Set Admin ID: {ADMIN_ID}")
    if message.from_user.id != ADMIN_ID:
        await message.reply(f"❌ **Access Denied**\n\nYour ID: `{message.from_user.id}`\nAdmin ID: `{ADMIN_ID}`")
        return

    # Force reload all user data to ensure fresh data
    load_user_ids()
    load_verified_users() 
    load_blocked_users()
    
    # Ensure admin is in user_ids for testing
    if ADMIN_ID not in user_ids:
        user_ids.add(ADMIN_ID)
        save_user_ids()
        print(f"🔍 BROADCAST: Added admin {ADMIN_ID} to user_ids")
    
    # Add current message sender to user_ids if different from admin
    user_ids.add(message.from_user.id)
    save_user_ids()

    print(f"🔍 BROADCAST: Total users in database: {len(user_ids)}")
    print(f"🔍 BROADCAST: User IDs: {list(user_ids)}")
    print(f"🔍 BROADCAST: Verified users: {len(verified_users)}")
    print(f"🔍 BROADCAST: Blocked users: {len(blocked_users)}")

    if not message.text:
        await message.reply("❌ **No message text found**")
        return

    # Extract broadcast content properly
    try:
        command_args = message.text.split(' ', 1)
        broadcast_content = command_args[1] if len(command_args) > 1 else ""
    except Exception as e:
        print(f"❌ BROADCAST: Error parsing command: {e}")
        await message.reply("❌ **Error parsing broadcast command**")
        return
    
    print(f"🔍 BROADCAST: Raw message: '{message.text}'")
    print(f"🔍 BROADCAST: Extracted content: '{broadcast_content}'")
    
    if not broadcast_content.strip():
        await message.reply("""📢 **Advanced Broadcasting System**

**Simple Broadcast:**
`/broadcast Your announcement message here`

**Interactive Broadcast with Buttons:**
```
/broadcast Your main message content

Button Text 1 - /command1
Button Text 2 - https://example.com
Button Text 3 - /command2
```

**Professional Example:**
```
/broadcast 🚀 Major Update Released!
New premium features are now available for all verified members.

🔐 Get Premium Key - /key
📱 BGMI APK - /apk
🌟 Join Premium Channel - https://t.me/flex_public
```""", parse_mode="Markdown")
        return

    # Parse message and buttons
    lines = broadcast_content.split('\n')
    broadcast_text = ""
    buttons = []
    
    print(f"🔍 BROADCAST: Processing {len(lines)} lines")
    
    for line_num, line in enumerate(lines):
        print(f"🔍 BROADCAST: Line {line_num}: '{line}'")
        
        if ' - /' in line or ' - https://' in line:
            parts = line.split(' - ', 1)
            if len(parts) == 2:
                button_text = parts[0].strip()
                button_action = parts[1].strip()
                
                print(f"🔍 BROADCAST: Button found - Text: '{button_text}', Action: '{button_action}'")
                
                if button_action.startswith('/'):
                    command = button_action[1:]
                    buttons.append(InlineKeyboardButton(text=button_text, callback_data=f"broadcast_{command}"))
                elif button_action.startswith('https://'):
                    buttons.append(InlineKeyboardButton(text=button_text, url=button_action))
        else:
            broadcast_text += line + '\n'
    
    broadcast_text = broadcast_text.strip()
    
    print(f"🔍 BROADCAST: Final broadcast text: '{broadcast_text}'")
    print(f"🔍 BROADCAST: Found {len(buttons)} buttons")
    
    if not broadcast_text:
        await message.reply("❌ **Empty broadcast message**")
        return

    # Create keyboard if buttons exist
    keyboard = None
    if buttons:
        # Group buttons into rows (2 per row max)
        button_rows = []
        for i in range(0, len(buttons), 2):
            button_rows.append(buttons[i:i+2])
        keyboard = InlineKeyboardMarkup(inline_keyboard=button_rows)
        print(f"🔍 BROADCAST: Created keyboard with {len(button_rows)} rows")

    # Track broadcasting progress
    sent_count = 0
    failed_count = 0
    
    status_msg = await message.reply("📡 **Starting Broadcast...**\n\n⏳ Sending messages to all users...")
    
    print(f"🔍 BROADCAST: Starting to send to {len(user_ids)} users")
    
    for user_id in user_ids:
        if user_id in blocked_users:
            print(f"🚫 BROADCAST: Skipping blocked user {user_id}")
            continue
            
        try:
            if keyboard:
                await bot.send_message(user_id, broadcast_text, parse_mode="Markdown", reply_markup=keyboard)
            else:
                await bot.send_message(user_id, broadcast_text, parse_mode="Markdown")
            sent_count += 1
            print(f"✅ BROADCAST: Sent to user {user_id}")
            
            # Update status every 5 messages
            if sent_count % 5 == 0:
                try:
                    await status_msg.edit_text(f"📡 **Broadcasting...**\n\n✅ Sent: {sent_count}\n❌ Failed: {failed_count}\n⏳ In progress...")
                except:
                    pass  # Ignore edit message errors
                
        except Exception as e:
            failed_count += 1
            print(f"❌ BROADCAST: Failed to send to {user_id}: {e}")
            logging.error(f"Failed to send broadcast to {user_id}: {e}")
        
        # Small delay to avoid rate limits
        await asyncio.sleep(0.1)
    
    final_text = f"""📡 **Broadcast Complete**

✅ **Successfully sent:** {sent_count}
❌ **Failed:** {failed_count}
👥 **Total users:** {len(user_ids)}
🚫 **Blocked users:** {len(blocked_users)}

📊 **Success rate:** {(sent_count/(sent_count+failed_count)*100) if (sent_count+failed_count) > 0 else 0:.1f}%"""
    
    try:
        await status_msg.edit_text(final_text)
    except:
        await message.reply(final_text)

@dp.message(Command("debug"))
async def debug_info(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    debug_text = f"""🔧 **Bot Debug Information**

👥 **Total Users:** {len(user_ids)}
✅ **Verified Users:** {len(verified_users)}
🚫 **Blocked Users:** {len(blocked_users)}
📢 **Channel ID:** {CHANNEL_ID}

**Recent User IDs:**
{', '.join(map(str, list(user_ids)[-10:]))}"""
    
    await message.reply(debug_text)

@dp.message(Command("testbroadcast"))
async def test_broadcast(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    test_message = "🧪 **Test Broadcast Message**\n\nThis is a test message to verify broadcast functionality."
    
    try:
        await bot.send_message(ADMIN_ID, test_message, parse_mode="Markdown")
        await message.reply("✅ **Test broadcast sent successfully to admin**")
    except Exception as e:
        await message.reply(f"❌ **Test broadcast failed:** {e}")

@dp.message(Command("help"))
async def admin_help(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    help_text = """🔧 **Admin Commands**

**Content Management:**
• `/setkey <key>` - Set activation key
• `/setapk` - Upload APK (caption message with /setapk)

**User Management:**
• `/block <user_id>` - Block a user
• `/unblock <user_id>` - Unblock a user
• `/reset <user_id>` - Reset user verification

**Broadcast:**
• `/broadcast <message>` - Send message to all users
• `/testbroadcast` - Test broadcast functionality

**Information:**
• `/debug` - Show bot statistics
• `/help` - Show this help message"""
    
    await message.reply(help_text)

@dp.message(Command("block"))
async def block_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply("**Usage:** `/block <user_id>`")
            return
        
        user_id = int(args[1])
        blocked_users.add(user_id)
        save_blocked_users()
        
        # Remove from verified users if blocked
        if user_id in verified_users:
            verified_users.remove(user_id)
            save_verified_users()
        
        await message.reply(f"✅ **User {user_id} has been blocked**")
        
    except ValueError:
        await message.reply("❌ **Invalid user ID**")
    except Exception as e:
        await message.reply(f"❌ **Error:** {e}")

@dp.message(Command("unblock"))
async def unblock_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply("**Usage:** `/unblock <user_id>`")
            return
        
        user_id = int(args[1])
        if user_id in blocked_users:
            blocked_users.remove(user_id)
            save_blocked_users()
            await message.reply(f"✅ **User {user_id} has been unblocked**")
        else:
            await message.reply(f"ℹ️ **User {user_id} was not blocked**")
            
    except ValueError:
        await message.reply("❌ **Invalid user ID**")
    except Exception as e:
        await message.reply(f"❌ **Error:** {e}")

@dp.message(Command("reset"))
async def reset_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply("**Usage:** `/reset <user_id>`")
            return
        
        user_id = int(args[1])
        
        # Remove from all sets
        if user_id in verified_users:
            verified_users.remove(user_id)
            save_verified_users()
        
        if user_id in blocked_users:
            blocked_users.remove(user_id)
            save_blocked_users()
        
        await message.reply(f"✅ **User {user_id} has been reset (removed from verified and blocked lists)**")
        
    except ValueError:
        await message.reply("❌ **Invalid user ID**")
    except Exception as e:
        await message.reply(f"❌ **Error:** {e}")

# Handle broadcast button callbacks
@dp.callback_query(F.data.startswith("broadcast_"))
async def handle_broadcast_buttons(callback_query: CallbackQuery):
    try:
        await callback_query.answer("📡 Processing broadcast request...")
    except Exception:
        pass

# Direct message handlers for non-command messages
async def handle_key_request(user_id, message):
    """Handle direct key requests"""
    is_member = await check_channel_membership(user_id)
    
    if not is_member:
        await message.reply("❌ **Premium Membership Required**\n\nPlease join our channel first:", reply_markup=get_welcome_keyboard())
        return
    
    await show_typing_animation(user_id, ChatAction.TYPING)
    
    try:
        with open("key.txt", "r", encoding="utf-8") as f:
            key_text = f.read().strip()
        await bot.send_message(user_id, f"🔐 **Premium Key**\n\n`{key_text}`", parse_mode="Markdown")
    except FileNotFoundError:
        await message.reply("❌ **Key unavailable at the moment**")

async def handle_apk_request(user_id, message):
    """Handle direct APK requests"""
    is_member = await check_channel_membership(user_id)
    
    if not is_member:
        await message.reply("❌ **Premium Membership Required**\n\nPlease join our channel first:", reply_markup=get_welcome_keyboard())
        return
    
    await show_typing_animation(user_id, ChatAction.UPLOAD_DOCUMENT)
    
    try:
        with open("apk_file_id.txt", "r") as f:
            file_id = f.read().strip()
        
        try:
            with open("apk_caption.txt", "r", encoding="utf-8") as f:
                caption = f.read().strip()
        except FileNotFoundError:
            caption = "📱 BGMI Premium Collection"
        
        await bot.send_document(user_id, file_id, caption=caption)
    except FileNotFoundError:
        await message.reply("❌ **APK currently unavailable**")

@dp.message(F.text)
async def direct_key(message: Message):
    """Handle direct text messages for key requests"""
    text = message.text.lower()
    user_id = message.from_user.id
    
    if user_id in blocked_users:
        return
    
    key_triggers = ['key', 'activation', 'code', 'password', 'unlock']
    apk_triggers = ['apk', 'app', 'download', 'file', 'bgmi']
    
    if any(trigger in text for trigger in key_triggers):
        await handle_key_request(user_id, message)
    elif any(trigger in text for trigger in apk_triggers):
        await handle_apk_request(user_id, message)
    else:
        # Show available options
        await message.reply("🎯 **How can I help you?**", reply_markup=get_content_keyboard())

@dp.message(F.content_type == ContentType.ANY)
async def direct_apk(message: Message):
    """Handle any other content type"""
    user_id = message.from_user.id
    
    if user_id in blocked_users:
        return
    
    if user_id != ADMIN_ID:
        await message.reply("🎯 **Available Services:**", reply_markup=get_content_keyboard())

@dp.message(Command("status"))
async def bot_status(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    status_text = f"""🤖 **Bot Status Report**

🟢 **Status:** Online & Running
⏰ **Uptime:** Active
📊 **Performance:** Optimal

**User Statistics:**
👥 Total Users: {len(user_ids)}
✅ Verified: {len(verified_users)}
🚫 Blocked: {len(blocked_users)}
📈 Active Rate: {((len(user_ids) - len(blocked_users))/max(len(user_ids), 1)*100):.1f}%

**System Info:**
📢 Channel: {CHANNEL_ID}
🔑 Admin ID: {ADMIN_ID}
🛡️ Security: Active"""
    
    await message.reply(status_text)

async def main():
    print("🤖 Starting FlexBot Premium Services...")
    print(f"📢 Channel: {CHANNEL_ID}")
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print(f"👥 Loaded {len(user_ids)} users")
    print(f"✅ Loaded {len(verified_users)} verified users")
    print(f"🚫 Loaded {len(blocked_users)} blocked users")
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())