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
ADMIN_ID = 7201285915
CHANNEL_USERNAME = "@flex_public"
CHANNEL_ID = "@flex_public"  # Make sure this channel exists and bot is admin

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
    except Exception as e:
        print(f"Error loading blocked users: {e}")
        blocked_users = set()

def save_blocked_users():
    try:
        with open("blocked_users.txt", "w") as f:
            for user_id in blocked_users:
                f.write(f"{user_id}\n")
    except Exception as e:
        print(f"Error saving blocked users: {e}")

def load_verified_users():
    global verified_users
    try:
        with open("verified_users.txt", "r") as f:
            verified_users = {int(line.strip()) for line in f if line.strip()}
    except FileNotFoundError:
        verified_users = set()
    except Exception as e:
        print(f"Error loading verified users: {e}")
        verified_users = set()

def save_verified_users():
    try:
        with open("verified_users.txt", "w") as f:
            for user_id in verified_users:
                f.write(f"{user_id}\n")
    except Exception as e:
        print(f"Error saving verified users: {e}")

def save_user_ids():
    try:
        with open("user_ids.txt", "w") as f:
            for user_id in user_ids:
                f.write(f"{user_id}\n")
    except Exception as e:
        print(f"Error saving user IDs: {e}")

def load_user_ids():
    global user_ids
    try:
        with open("user_ids.txt", "r") as f:
            user_ids = {int(line.strip()) for line in f if line.strip()}
    except FileNotFoundError:
        user_ids = set()
    except Exception as e:
        print(f"Error loading user IDs: {e}")
        user_ids = set()

# Load all data on startup
load_blocked_users()
load_verified_users()
load_user_ids()

# Setup logging - reduce verbosity but keep errors
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize bot
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def show_typing_animation(chat_id: int, action_type: ChatAction = ChatAction.TYPING):
    """Enhanced loading animation with multiple stages and emojis"""
    try:
        # Stage 1: Initial loading
        if action_type == ChatAction.TYPING:
            status_msg = await bot.send_message(chat_id, "⏳ **Loading Premium Key Generator...**", parse_mode="Markdown")
        else:
            status_msg = await bot.send_message(chat_id, "⏳ **Loading Download Manager...**", parse_mode="Markdown")
        
        await bot.send_chat_action(chat_id, action_type)
        await asyncio.sleep(1.0)
        
        # Stage 2: Processing with spinner
        loading_emojis = ["🔄", "⚡", "🔃", "⭐"]
        for i, emoji in enumerate(loading_emojis):
            if action_type == ChatAction.TYPING:
                try:
                    await status_msg.edit_text(f"{emoji} **Processing premium access...** {emoji}", parse_mode="Markdown")
                except Exception:
                    pass
            else:
                try:
                    await status_msg.edit_text(f"{emoji} **Preparing download...** {emoji}", parse_mode="Markdown")
                except Exception:
                    pass
            
            await bot.send_chat_action(chat_id, action_type)
            await asyncio.sleep(0.8)
        
        # Stage 3: Security verification
        if action_type == ChatAction.TYPING:
            try:
                await status_msg.edit_text("🔐 **Verifying premium membership...** 🛡️", parse_mode="Markdown")
            except Exception:
                pass
        else:
            try:
                await status_msg.edit_text("🛡️ **Verifying download permissions...** 🔐", parse_mode="Markdown")
            except Exception:
                pass
        
        await bot.send_chat_action(chat_id, action_type)
        await asyncio.sleep(1.2)
        
        # Stage 4: Generation/Preparation with progress
        progress_bars = ["▱▱▱▱▱", "▰▱▱▱▱", "▰▰▱▱▱", "▰▰▰▱▱", "▰▰▰▰▱", "▰▰▰▰▰"]
        for i, bar in enumerate(progress_bars):
            if action_type == ChatAction.TYPING:
                try:
                    await status_msg.edit_text(f"🔑 **Generating activation key...** {bar}", parse_mode="Markdown")
                except Exception:
                    pass
            else:
                try:
                    await status_msg.edit_text(f"📱 **Preparing APK package...** {bar}", parse_mode="Markdown")
                except Exception:
                    pass
            
            await bot.send_chat_action(chat_id, action_type)
            await asyncio.sleep(0.6)
        
        # Stage 5: Final loading with sparkles
        final_emojis = ["✨", "🌟", "⭐", "💫"]
        for emoji in final_emojis:
            if action_type == ChatAction.TYPING:
                try:
                    await status_msg.edit_text(f"{emoji} **Key generation complete!** {emoji}", parse_mode="Markdown")
                except Exception:
                    pass
            else:
                try:
                    await status_msg.edit_text(f"{emoji} **APK package ready!** {emoji}", parse_mode="Markdown")
                except Exception:
                    pass
            
            await bot.send_chat_action(chat_id, action_type)
            await asyncio.sleep(0.5)
        
        # Stage 6: Ready to deliver
        if action_type == ChatAction.TYPING:
            try:
                await status_msg.edit_text("🚀 **Delivering your premium key...** 🎯", parse_mode="Markdown")
            except Exception:
                pass
        else:
            try:
                await status_msg.edit_text("🚀 **Uploading premium APK...** 📦", parse_mode="Markdown")
            except Exception:
                pass
        
        await bot.send_chat_action(chat_id, action_type)
        await asyncio.sleep(1.0)
        
        # Delete status message after animation
        try:
            await status_msg.delete()
        except Exception:
            pass
        
    except Exception as e:
        print(f"Error showing loading animation: {e}")
        # Fallback simple animation
        try:
            await bot.send_chat_action(chat_id, action_type)
            await asyncio.sleep(3)
        except Exception:
            pass

async def check_channel_membership(user_id):
    try:
        # Admin always has access
        if user_id == ADMIN_ID:
            print(f"✅ Admin access granted for ID: {user_id}")
            return True

        print(f"🔍 Checking membership for user {user_id} in channel {CHANNEL_ID}")
        
        try:
            # Force fresh check by clearing cache
            member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
            print(f"🔍 Member status for {user_id}: {member.status}")

            # Check for valid membership statuses
            valid_statuses = [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]
            
            if member.status in valid_statuses:
                print(f"✅ User {user_id} is a valid member with status: {member.status}")
                verified_users.add(user_id)
                save_verified_users()
                return True
            elif member.status == ChatMemberStatus.LEFT:
                print(f"❌ User {user_id} has left the channel")
                if user_id in verified_users:
                    verified_users.remove(user_id)
                    save_verified_users()
                return False
            elif member.status == ChatMemberStatus.KICKED:
                print(f"❌ User {user_id} is banned from the channel")
                if user_id in verified_users:
                    verified_users.remove(user_id)
                    save_verified_users()
                return False
            else:
                print(f"❌ User {user_id} has invalid status: {member.status}")
                if user_id in verified_users:
                    verified_users.remove(user_id)
                    save_verified_users()
                return False

        except Exception as e:
            print(f"⚠️ API Error checking membership for {user_id}: {e}")
            # For testing, return False to force proper membership check
            return False

    except Exception as e:
        print(f"❌ Critical error in membership check for {user_id}: {e}")
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
    try:
        user_ids.add(message.from_user.id)
        save_user_ids()

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
    except Exception as e:
        print(f"Error in welcome handler: {e}")
        await message.reply("🤖 **Bot Started Successfully!**\n\nWelcome to FlexBot Premium Services!")

@dp.callback_query(F.data == "check_joined")
async def check_joined(callback_query: CallbackQuery):
    try:
        await callback_query.answer()
        user_id = callback_query.from_user.id

        if user_id in blocked_users:
            await callback_query.message.edit_text("🚫 **Access Denied**\n\nYour account has been restricted from accessing this service.")
            return

        # Show loading animation for membership check
        loading_msg = await callback_query.message.edit_text("🔍 **Checking membership status...** ⏳", parse_mode="Markdown")
        
        # Loading animation for membership check
        check_emojis = ["🔍", "🔎", "👁️", "🛡️"]
        for emoji in check_emojis:
            try:
                await loading_msg.edit_text(f"{emoji} **Verifying your membership...** {emoji}", parse_mode="Markdown")
                await asyncio.sleep(0.8)
            except Exception:
                pass

        is_member = await check_channel_membership(user_id)

        if is_member:
            verified_users.add(user_id)
            save_verified_users()

            thank_you_text = """🎉 **Membership Verified Successfully** 🎉

✅ **Premium Access Granted**
🔓 **All Features Unlocked**
⭐ **Welcome to the Elite Community**

Choose your desired content:"""

            await callback_query.message.edit_text(thank_you_text, reply_markup=get_content_keyboard(), parse_mode="Markdown")
        else:
            not_joined_text = """❌ **Membership Verification Failed**

📢 Please join our premium channel first to access exclusive content.
🔄 After joining, click "✅ Verify Membership" to proceed."""

            await callback_query.message.edit_text(not_joined_text, reply_markup=get_welcome_keyboard(), parse_mode="Markdown")
    except Exception as e:
        print(f"Error in check_joined: {e}")

@dp.callback_query(F.data == "get_key")
async def get_key(callback_query: CallbackQuery):
    try:
        await callback_query.answer()
        user_id = callback_query.from_user.id

        if user_id in blocked_users:
            await callback_query.message.edit_text("🚫 **Access Denied**")
            return

        is_member = await check_channel_membership(user_id)

        if not is_member:
            await callback_query.message.edit_text(
                "❌ **Premium Membership Required**\n\nPlease join our channel first!",
                reply_markup=get_welcome_keyboard(),
                parse_mode="Markdown"
            )
            return

        # Show typing animation before sending key
        await show_typing_animation(user_id, ChatAction.TYPING)

        try:
            with open("key.txt", "r", encoding="utf-8") as f:
                key_text = f.read().strip()

            await bot.send_message(user_id, f"🔐 **Premium Activation Key**\n\n`{key_text}`\n\n✅ Tap the key above to copy it!", parse_mode="Markdown")
        except FileNotFoundError:
            await callback_query.message.reply("❌ **Key Currently Unavailable**\n\nPlease try again later.")
    except Exception as e:
        print(f"Error in get_key: {e}")

@dp.callback_query(F.data == "get_apk")
async def get_apk(callback_query: CallbackQuery):
    try:
        await callback_query.answer()
        user_id = callback_query.from_user.id

        if user_id in blocked_users:
            await callback_query.message.edit_text("🚫 **Access Denied**")
            return

        is_member = await check_channel_membership(user_id)

        if not is_member:
            await callback_query.message.edit_text(
                "❌ **Premium Membership Required**\n\nPlease join our channel first!",
                reply_markup=get_welcome_keyboard(),
                parse_mode="Markdown"
            )
            return

        # Show uploading animation before sending APK
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
            await callback_query.message.reply("❌ **APK Currently Unavailable**\n\nPlease check back later.")
    except Exception as e:
        print(f"Error in get_apk: {e}")

@dp.message(Command("setkey"))
async def set_key(message: Message):
    try:
        if message.from_user.id != ADMIN_ID:
            return

        command_args = message.text.split(' ', 1)
        key_text = command_args[1] if len(command_args) > 1 else ""

        if not key_text:
            await message.reply("**Usage:** `/setkey Your Premium Key Text`")
            return

        with open("key.txt", "w", encoding="utf-8") as f:
            f.write(key_text)
        await message.reply("✅ **Activation Key Updated Successfully**")
    except Exception as e:
        print(f"Error in set_key: {e}")

@dp.message(F.content_type == ContentType.DOCUMENT)
async def set_apk(message: Message):
    try:
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
    except Exception as e:
        print(f"Error in set_apk: {e}")

@dp.message(Command("broadcast"))
async def broadcast_message(message: Message):
    """Enhanced broadcast command with custom button support"""
    if message.from_user.id != ADMIN_ID:
        await message.reply(f"❌ **Access Denied**\n\nOnly admin can use broadcast")
        return

    # Force reload user data
    load_user_ids()
    load_verified_users() 
    load_blocked_users()
    
    # Ensure admin is in user_ids
    if ADMIN_ID not in user_ids:
        user_ids.add(ADMIN_ID)
        save_user_ids()
    
    user_ids.add(message.from_user.id)
    save_user_ids()

    # Extract broadcast content
    try:
        command_args = message.text.split(' ', 1)
        broadcast_content = command_args[1] if len(command_args) > 1 else ""
    except Exception as e:
        await message.reply("❌ **Error parsing broadcast command**")
        return
    
    if not broadcast_content.strip():
        await message.reply("""📢 **Enhanced Broadcasting System with Custom Buttons**

**📍 Basic Broadcast:**
```
/broadcast Your message here
```

**🎛️ Broadcast with Buttons (Advanced):**
```
/broadcast Your main message content

BUTTON:Button Text 1|callback_data_1
BUTTON:Button Text 2|callback_data_2
URL:Website Link|https://example.com
URL:Join Channel|https://t.me/flex_public
```

**📋 Professional Examples:**

**Example 1 - Simple Announcement:**
```
/broadcast 🚀 New Update Available!
Premium features have been enhanced for better performance.
```

**Example 2 - Interactive Broadcast:**
```
/broadcast 🎯 Welcome to Premium Services!
Access exclusive content with our latest features.

BUTTON:🔐 Get Key|get_activation_key
BUTTON:📱 Download APK|get_premium_apk
URL:📢 Join Channel|https://t.me/flex_public
URL:💬 Support|https://t.me/support_chat
```

**Example 3 - Product Launch:**
```
/broadcast 🔥 BGMI Premium Launch!
Exclusive graphics pack now available for verified members.

BUTTON:✨ Get Graphics|graphics_pack
BUTTON:🎮 Game APK|bgmi_premium
BUTTON:🔑 Activation|premium_key
URL:🎯 Tutorial|https://tutorial.link
```

**🎨 Button Format Rules:**
• **BUTTON:** for callback buttons (bot actions)
• **URL:** for web links  
• Format: `TYPE:Display Text|action_data`
• Max 8 buttons per message
• Buttons appear in 2-column layout

**⚡ Quick Commands:**
• `/broadcast_test` - Send test broadcast to admin only
• `/broadcast_stats` - View broadcast statistics""", parse_mode="Markdown")
        return

    # Parse message content and extract buttons
    lines = broadcast_content.split('\n')
    broadcast_text = ""
    buttons = []
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('BUTTON:') or line.startswith('URL:'):
            try:
                # Parse button format: TYPE:Display Text|action_data
                button_type = line.split(':', 1)[0]
                button_content = line.split(':', 1)[1]
                
                if '|' in button_content:
                    button_text, button_data = button_content.split('|', 1)
                    button_text = button_text.strip()
                    button_data = button_data.strip()
                    
                    if button_type == 'BUTTON':
                        buttons.append(InlineKeyboardButton(text=button_text, callback_data=f"bc_{button_data}"))
                    elif button_type == 'URL':
                        buttons.append(InlineKeyboardButton(text=button_text, url=button_data))
                    
                    print(f"🔍 BROADCAST: Added {button_type} - '{button_text}' -> '{button_data}'")
                else:
                    print(f"⚠️ BROADCAST: Invalid button format: {line}")
            except Exception as e:
                print(f"❌ BROADCAST: Error parsing button: {line} - {e}")
        else:
            if line:  # Only add non-empty lines
                broadcast_text += line + '\n'
    
    broadcast_text = broadcast_text.strip()
    
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
        print(f"🔍 BROADCAST: Created keyboard with {len(button_rows)} rows, {len(buttons)} total buttons")

    # Track broadcasting progress
    sent_count = 0
    failed_count = 0
    
    status_msg = await message.reply("📡 **Starting Enhanced Broadcast...**\n\n⏳ Sending messages to all users...")
    
    print(f"🔍 BROADCAST: Sending to {len(user_ids)} users")
    
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
                    await status_msg.edit_text(f"📡 **Broadcasting...**\n\n✅ Sent: {sent_count}\n❌ Failed: {failed_count}\n🎯 Buttons: {len(buttons)}\n⏳ In progress...")
                except:
                    pass
                
        except Exception as e:
            failed_count += 1
            print(f"❌ BROADCAST: Failed to send to {user_id}: {e}")
        
        # Rate limiting
        await asyncio.sleep(0.1)
    
    final_text = f"""📡 **Enhanced Broadcast Complete**

✅ **Successfully sent:** {sent_count}
❌ **Failed:** {failed_count}
👥 **Total users:** {len(user_ids)}
🎯 **Buttons included:** {len(buttons)}
🚫 **Blocked users:** {len(blocked_users)}

📊 **Success rate:** {(sent_count/(sent_count+failed_count)*100) if (sent_count+failed_count) > 0 else 0:.1f}%

**Button Summary:**
{chr(10).join([f"• {btn.text}" for btn in buttons[:5]])}
{"• ..." if len(buttons) > 5 else ""}"""
    
    try:
        await status_msg.edit_text(final_text)
    except:
        await message.reply(final_text)

@dp.message(Command("broadcast_test"))
async def test_broadcast(message: Message):
    """Test broadcast functionality with admin only"""
    if message.from_user.id != ADMIN_ID:
        return
    
    test_message = """🧪 **Test Broadcast Message**

This is a test message to verify enhanced broadcast functionality with buttons.

Test completed successfully! ✅"""
    
    # Test buttons
    test_buttons = [
        [InlineKeyboardButton(text="🔐 Test Key", callback_data="bc_test_key")],
        [InlineKeyboardButton(text="📱 Test APK", callback_data="bc_test_apk")],
        [InlineKeyboardButton(text="🌐 Test URL", url="https://t.me/flex_public")]
    ]
    test_keyboard = InlineKeyboardMarkup(inline_keyboard=test_buttons)
    
    try:
        await bot.send_message(ADMIN_ID, test_message, parse_mode="Markdown", reply_markup=test_keyboard)
        await message.reply("✅ **Test broadcast sent successfully to admin with buttons**")
    except Exception as e:
        await message.reply(f"❌ **Test broadcast failed:** {e}")

@dp.message(Command("broadcast_stats"))
async def broadcast_stats(message: Message):
    """Show detailed broadcast statistics"""
    if message.from_user.id != ADMIN_ID:
        return
    
    stats_text = f"""📊 **Enhanced Broadcast Statistics**

**User Database:**
👥 Total Users: {len(user_ids)}
✅ Verified Users: {len(verified_users)}
🚫 Blocked Users: {len(blocked_users)}
📈 Active Users: {len(user_ids) - len(blocked_users)}

**System Status:**
🤖 Bot: Online & Enhanced
📢 Channel: {CHANNEL_ID}
🔑 Admin ID: {ADMIN_ID}
⚡ Features: Advanced Buttons Enabled

**Recent User IDs:**
{', '.join(map(str, list(user_ids)[-10:]))}

**Enhancement Features:**
🎛️ Custom Button Support
📱 URL Button Integration  
🔄 Real-time Progress Tracking
📊 Detailed Statistics
🚫 Auto-skip Blocked Users"""
    
    await message.reply(stats_text)

# Handle custom broadcast button callbacks
@dp.callback_query(F.data.startswith("bc_"))
async def handle_broadcast_callbacks(callback_query: CallbackQuery):
    """Handle custom broadcast button callbacks"""
    try:
        await callback_query.answer("🎯 Processing your request...")
    except Exception:
        pass
    
    callback_data = callback_query.data[3:]  # Remove 'bc_' prefix
    user_id = callback_query.from_user.id
    
    print(f"🔍 BROADCAST CALLBACK: User {user_id} clicked '{callback_data}'")
    
    # Handle different callback actions
    if callback_data in ['get_activation_key', 'premium_key', 'test_key']:
        await get_key_from_broadcast(callback_query)
    elif callback_data in ['get_premium_apk', 'bgmi_premium', 'test_apk']:
        await get_apk_from_broadcast(callback_query)
    elif callback_data == 'graphics_pack':
        await callback_query.message.reply("🎨 **Graphics Pack**\n\nPremium graphics collection is being prepared for download!")
    else:
        # Generic response for custom callbacks
        await callback_query.message.reply(f"✅ **Action Triggered**\n\nYou clicked: `{callback_data}`\n\nCustom action processed successfully!", parse_mode="Markdown")

async def get_key_from_broadcast(callback_query: CallbackQuery):
    """Handle key request from broadcast button"""
    user_id = callback_query.from_user.id
    
    if user_id in blocked_users:
        await callback_query.message.reply("🚫 **Access Denied**\n\nYour account has been restricted.")
        return
    
    is_member = await check_channel_membership(user_id)
    
    if not is_member:
        await callback_query.message.reply("❌ **Premium Membership Required**\n\nPlease join our channel first!", reply_markup=get_welcome_keyboard())
        return
    
    await show_typing_animation(user_id, ChatAction.TYPING)
    
    try:
        with open("key.txt", "r", encoding="utf-8") as f:
            key_text = f.read().strip()
        await bot.send_message(user_id, f"🔐 **Premium Activation Key**\n\n`{key_text}`\n\n✅ Requested via broadcast button!", parse_mode="Markdown")
    except FileNotFoundError:
        await callback_query.message.reply("❌ **Key Currently Unavailable**")

async def get_apk_from_broadcast(callback_query: CallbackQuery):
    """Handle APK request from broadcast button"""
    user_id = callback_query.from_user.id
    
    if user_id in blocked_users:
        await callback_query.message.reply("🚫 **Access Denied**\n\nYour account has been restricted.")
        return
    
    is_member = await check_channel_membership(user_id)
    
    if not is_member:
        await callback_query.message.reply("❌ **Premium Membership Required**\n\nPlease join our channel first!", reply_markup=get_welcome_keyboard())
        return
    
    await show_typing_animation(user_id, ChatAction.UPLOAD_DOCUMENT)
    
    try:
        with open("apk_file_id.txt", "r") as f:
            file_id = f.read().strip()
        with open("apk_caption.txt", "r", encoding="utf-8") as f:
            caption = f.read().strip()
        await bot.send_document(user_id, file_id, caption=caption + "\n\n📱 Requested via broadcast button!")
    except FileNotFoundError:
        await callback_query.message.reply("❌ **APK Currently Unavailable**")

# Admin commands for user management
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

@dp.message(Command("status"))
async def status_check(message: Message):
    try:
        if message.from_user.id != ADMIN_ID:
            return

        status_text = f"""🤖 **Bot Status Report**

🟢 **Status:** Online & Running
👥 **Total Users:** {len(user_ids)}
✅ **Verified Users:** {len(verified_users)}
🚫 **Blocked Users:** {len(blocked_users)}
📢 **Channel:** {CHANNEL_ID}
🔑 **Admin ID:** {ADMIN_ID}"""

        await message.reply(status_text)
    except Exception as e:
        print(f"Error in status: {e}")

@dp.message(Command("help"))
async def admin_help(message: Message):
    try:
        if message.from_user.id != ADMIN_ID:
            return

        help_text = """🔧 **Admin Commands**

**Content Management:**
• `/setkey <key>` - Set activation key
• `/setapk` - Upload APK (with file)

**User Management:**
• `/block <user_id>` - Block a user
• `/unblock <user_id>` - Unblock a user

**System:**
• `/status` - Bot status
• `/help` - This help message"""

        await message.reply(help_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in help: {e}")

@dp.message(Command("testmembership"))
async def test_membership(message: Message):
    """Test membership check for current user"""
    if message.from_user.id != ADMIN_ID:
        return
    
    user_id = message.from_user.id
    
    # First show what we have in cache
    await message.reply(f"🔍 **Testing membership for User ID:** `{user_id}`\n\n⏳ Checking...")
    
    # Clear user from verified list for testing
    if user_id in verified_users:
        verified_users.remove(user_id)
        save_verified_users()
    
    # Now test membership
    is_member = await check_channel_membership(user_id)
    
    try:
        # Get actual chat member info
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        actual_status = member.status
    except Exception as e:
        actual_status = f"Error: {e}"
    
    test_result = f"""🧪 **Membership Test Results**

**User ID:** `{user_id}`
**Channel:** `{CHANNEL_ID}`
**Actual API Status:** `{actual_status}`
**Our Check Result:** {'✅ Member' if is_member else '❌ Not Member'}
**In Verified List:** {'✅ Yes' if user_id in verified_users else '❌ No'}
**Is Admin:** {'✅ Yes' if user_id == ADMIN_ID else '❌ No'}

**Debug Info:**
• Total verified users: {len(verified_users)}
• Bot Token: Active
• Channel ID: {CHANNEL_ID}

**Bot Permission Check:**
Try `/checkchannel` to verify bot has access to channel."""
    
    await message.reply(test_result, parse_mode="Markdown")

@dp.message(Command("checkchannel"))
async def check_channel_access(message: Message):
    """Check if bot can access the channel"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        chat_info = await bot.get_chat(CHANNEL_ID)
        
        result = f"""🔍 **Channel Access Test**

✅ **Bot can access channel!**

**Channel Info:**
• **Title:** {chat_info.title}
• **Type:** {chat_info.type}
• **ID:** `{chat_info.id}`
• **Username:** @{chat_info.username if chat_info.username else 'No username'}
• **Members Count:** {chat_info.member_count if hasattr(chat_info, 'member_count') else 'Unknown'}

**Bot Status:** Ready for membership checks ✅"""
        
        await message.reply(result, parse_mode="Markdown")
        
    except Exception as e:
        error_result = f"""❌ **Channel Access Failed**

**Error:** `{e}`

**Possible Issues:**
1. Bot is not admin in channel `{CHANNEL_ID}`
2. Channel doesn't exist or is private
3. Bot token is invalid
4. Channel ID format is wrong

**Solutions:**
1. Add bot as admin to {CHANNEL_ID}
2. Make sure channel exists and is public
3. Check bot token in secrets"""
        
        await message.reply(error_result, parse_mode="Markdown")

@dp.message(Command("forceverify"))
async def force_verify_user(message: Message):
    """Force verify a user for testing"""
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply("**Usage:** `/forceverify <user_id>`")
        return
    
    try:
        user_id = int(args[1])
        verified_users.add(user_id)
        save_verified_users()
        await message.reply(f"✅ **Force verified user:** `{user_id}`\n\nThey can now access premium features.")
    except ValueError:
        await message.reply("❌ **Invalid user ID**")

@dp.message(Command("adminhelp"))
async def admin_help_detailed(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply(f"❌ **Access Denied**\n\nYour ID: `{message.from_user.id}`\nAdmin ID: `{ADMIN_ID}`")
        return

    help_text = """🔧 **FlexBot Administrative Command Center**

**📝 Content Management Commands:**
• `/setkey <text>` - Configure premium activation key
• `/setapk` (with file attachment) - Upload premium APK package

**👥 User Management Operations:**  
• `/block <user_id>` - Restrict user access to services
• `/unblock <user_id>` - Restore user access privileges

**📢 Broadcasting & Communication:**
• `/broadcast <message>` - Send announcements to all users
• `/broadcast_test` - Test broadcast functionality with admin
• `/broadcast_stats` - View detailed broadcast statistics

**Enhanced Broadcasting Features:**
Add interactive buttons using format:
```
BUTTON:Button Text|callback_data
URL:Button Text|https://link.com
```

**📊 System Monitoring:**
• `/status` - View comprehensive system dashboard
• `/help` - Basic admin commands
• `/adminhelp` - This detailed command reference

**🧪 Debug & Testing:**
• `/testmembership` - Test membership check system
• `/checkchannel` - Verify bot channel access
• `/forceverify <user_id>` - Force verify user for testing

**📱 Professional Broadcast Example:**
```
/broadcast 🚀 Premium Update Available!
Access the latest features now.

BUTTON:🔐 Get Key|get_activation_key
BUTTON:📱 Download APK|get_premium_apk
URL:🌟 Join Channel|https://t.me/flex_public
```

**🎯 All commands are admin-exclusive and secured.**
**📈 Current Status:** Bot Online & Enhanced Features Active"""

    await message.reply(help_text, parse_mode="Markdown")

@dp.message(F.text)
async def handle_text_messages(message: Message):
    try:
        text = message.text.lower()
        user_id = message.from_user.id

        if user_id in blocked_users:
            return

        key_triggers = ['key', 'activation', 'code', 'password', 'unlock']
        apk_triggers = ['apk', 'app', 'download', 'file', 'bgmi']

        if any(trigger in text for trigger in key_triggers):
            is_member = await check_channel_membership(user_id)
            if not is_member:
                await message.reply("❌ **Premium Membership Required**", reply_markup=get_welcome_keyboard())
                return

            await show_typing_animation(user_id, ChatAction.TYPING)
            try:
                with open("key.txt", "r", encoding="utf-8") as f:
                    key_text = f.read().strip()
                await bot.send_message(user_id, f"🔐 **Premium Key**\n\n`{key_text}`", parse_mode="Markdown")
            except FileNotFoundError:
                await message.reply("❌ **Key unavailable at the moment**")

        elif any(trigger in text for trigger in apk_triggers):
            is_member = await check_channel_membership(user_id)
            if not is_member:
                await message.reply("❌ **Premium Membership Required**", reply_markup=get_welcome_keyboard())
                return

            await show_typing_animation(user_id, ChatAction.UPLOAD_DOCUMENT)
            try:
                with open("apk_file_id.txt", "r") as f:
                    file_id = f.read().strip()
                with open("apk_caption.txt", "r", encoding="utf-8") as f:
                    caption = f.read().strip()
                await bot.send_document(user_id, file_id, caption=caption)
            except FileNotFoundError:
                await message.reply("❌ **APK currently unavailable**")
        else:
            await message.reply("🎯 **How can I help you?**", reply_markup=get_content_keyboard())
    except Exception as e:
        print(f"Error in text handler: {e}")

async def main():
    print("🤖 Starting FlexBot Premium Services...")
    print(f"📢 Channel: {CHANNEL_ID}")
    print(f"🔑 Admin ID: {ADMIN_ID}")
    print(f"👥 Loaded {len(user_ids)} users")
    print(f"✅ Loaded {len(verified_users)} verified users")
    print(f"🚫 Loaded {len(blocked_users)} blocked users")
    print("🎛️ Enhanced broadcast with custom buttons enabled")

    try:
        print("🚀 Bot starting polling...")
        await dp.start_polling(bot, skip_updates=True)
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        # Try to restart after error
        await asyncio.sleep(5)
        print("🔄 Attempting to restart...")
        await main()
    finally:
        try:
            await bot.session.close()
        except:
            pass

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped")
    except Exception as e:
        print(f"❌ Critical error: {e}")