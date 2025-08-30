"""Main bot module with handlers and commands"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, ChatMember
)
from pyrogram.errors import FloodWait, UserNotParticipant, ChatAdminRequired

from config import Config
from database import (
    User, FileStats, BotStats, 
    get_or_create_user, update_file_stats, get_bot_stats
)
from utils import (
    get_hash, get_name, get_file_size, get_file_type,
    format_size, format_duration, get_media_from_message,
    validate_file_size, validate_file_extension, create_progress_bar
)


class TelegramBot(Client):
    """Enhanced Telegram Bot with additional features"""
    
    def __init__(self, name: str, api_id: int, api_hash: str, 
                 bot_token: str, config: Config, db_session):
        super().__init__(
            name=name,
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
            workers=config.WORKERS,
            sleep_threshold=config.SLEEP_THRESHOLD,
            plugins=dict(root="plugins")
        )
        
        self.config = config
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
        self.username = None
        
        # Register handlers
        self.register_handlers()
        
    def register_handlers(self):
        """Register all bot handlers"""
        # Start command
        self.add_handler(self.start_handler, filters.command("start") & filters.private)
        
        # Help command
        self.add_handler(self.help_handler, filters.command("help") & filters.private)
        
        # Stats command
        self.add_handler(self.stats_handler, filters.command("stats") & filters.private)
        
        # Admin commands
        self.add_handler(self.admin_handler, filters.command("admin") & filters.private & filters.user(self.config.ADMINS))
        self.add_handler(self.broadcast_handler, filters.command("broadcast") & filters.private & filters.user(self.config.ADMINS))
        self.add_handler(self.users_handler, filters.command("users") & filters.private & filters.user(self.config.ADMINS))
        
        # File handler
        self.add_handler(
            self.file_handler, 
            filters.private & (
                filters.document | filters.video | filters.audio |
                filters.animation | filters.voice | filters.video_note |
                filters.photo | filters.sticker
            )
        )
        
        # Callback handlers
        self.add_handler(self.callback_handler, filters.callback_query)
        
    def add_handler(self, handler, filters):
        """Add a handler to the bot"""
        @self.on_message(filters)
        async def wrapper(client, message):
            await handler(message)
            
    async def start_handler(self, message: Message):
        """Handle /start command"""
        user_id = message.from_user.id
        
        # Create or update user in database
        await get_or_create_user(
            self.db_session,
            user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code
        )
        
        # Check if user needs to join channel
        if self.config.ENABLE_FORCE_SUB and self.config.FORCE_SUB_CHANNEL:
            try:
                member = await self.get_chat_member(
                    self.config.FORCE_SUB_CHANNEL,
                    user_id
                )
                if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.MEMBER]:
                    raise UserNotParticipant
            except UserNotParticipant:
                await self.send_force_sub_message(message)
                return
            except Exception as e:
                self.logger.error(f"Force sub check error: {e}")
                
        # Send welcome message
        await self.send_welcome_message(message)
        
    async def send_welcome_message(self, message: Message):
        """Send welcome message with beautiful formatting"""
        user_mention = message.from_user.mention
        
        welcome_text = f"""
🎉 **Welcome, {user_mention}!**

I'm a **File Stream Bot** that can generate direct download links for your files.

**✨ Features:**
• 📁 Support for all file types
• 🔗 Instant streaming links
• 📊 File statistics tracking
• 🚀 High-speed streaming
• 🔒 Secure and private

**📤 How to use:**
Simply send me any file, and I'll give you a direct link!

**🤖 Commands:**
/help - Show help message
/stats - View your statistics
/about - About this bot

**💡 Pro tip:** You can also forward files from other chats!
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📚 Help", callback_data="help"),
                InlineKeyboardButton("📊 Stats", callback_data="stats")
            ],
            [
                InlineKeyboardButton("ℹ️ About", callback_data="about"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ],
            [
                InlineKeyboardButton("👥 Support Group", url="https://t.me/your_support_group"),
                InlineKeyboardButton("📢 Updates", url="https://t.me/your_updates_channel")
            ]
        ])
        
        await message.reply_text(
            welcome_text,
            reply_markup=keyboard,
            quote=True
        )
        
    async def send_force_sub_message(self, message: Message):
        """Send force subscribe message"""
        text = f"""
❌ **Access Denied!**

You need to join our channel to use this bot.

👉 **Join Channel:** {self.config.FORCE_SUB_CHANNEL}

After joining, click **"✅ Check"** button below.
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{self.config.FORCE_SUB_CHANNEL[1:]}"),
                InlineKeyboardButton("✅ Check", callback_data="check_sub")
            ]
        ])
        
        await message.reply_text(text, reply_markup=keyboard, quote=True)
        
    async def help_handler(self, message: Message):
        """Handle /help command"""
        help_text = """
📚 **Help Menu**

**🤖 Available Commands:**

**General Commands:**
• /start - Start the bot
• /help - Show this help message
• /stats - View your statistics
• /about - About this bot

**File Commands:**
• Just send me any file to get a streaming link!

**Supported File Types:**
📄 Documents
🎥 Videos
🎵 Audio files
🖼 Photos
🎤 Voice messages
📹 Video notes
✨ Animations (GIFs)
🎨 Stickers

**Features:**
• **Instant Links** - Get streaming links immediately
• **No Size Limit** - Upload files up to 2GB
• **Statistics** - Track your file views and downloads
• **High Speed** - Fast streaming servers
• **24/7 Available** - Always online and ready

**Tips:**
💡 You can forward files from any chat
💡 Links never expire
💡 Share links with anyone
💡 No registration required

**Need help?** Join our @support_group
"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Home", callback_data="home")],
            [InlineKeyboardButton("👥 Support", url="https://t.me/your_support_group")]
        ])
        
        await message.reply_text(help_text, reply_markup=keyboard, quote=True)
        
    async def stats_handler(self, message: Message):
        """Handle /stats command"""
        user_id = message.from_user.id
        
        # Get user from database
        user = self.db_session.query(User).filter_by(id=user_id).first()
        if not user:
            await message.reply_text("❌ User not found in database!")
            return
            
        # Get file statistics
        user_files = self.db_session.query(FileStats).filter_by(user_id=user_id).all()
        total_views = sum(f.views for f in user_files)
        total_downloads = sum(f.downloads for f in user_files)
        
        # Calculate time since joined
        time_joined = datetime.utcnow() - user.joined_date
        days_joined = time_joined.days
        
        stats_text = f"""
📊 **Your Statistics**

👤 **User Info:**
• **Name:** {user.full_name}
• **User ID:** `{user_id}`
• **Joined:** {days_joined} days ago

📁 **File Statistics:**
• **Total Files:** {user.files_uploaded}
• **Total Size:** {format_size(user.total_size_uploaded)}
• **Total Views:** {total_views:,}
• **Total Downloads:** {total_downloads:,}

📈 **Activity:**
• **Last Active:** {user.last_activity.strftime('%Y-%m-%d %H:%M')}
• **Status:** {'🟢 Active' if not user.is_banned else '🔴 Banned'}
• **Account Type:** {'⭐ Premium' if user.is_premium else '👤 Free'}

🏆 **Achievements:**
{self._get_achievements(user, user_files)}
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats"),
                InlineKeyboardButton("📈 Detailed", callback_data="detailed_stats")
            ],
            [InlineKeyboardButton("🏠 Home", callback_data="home")]
        ])
        
        await message.reply_text(stats_text, reply_markup=keyboard, quote=True)
        
    def _get_achievements(self, user: User, files: list) -> str:
        """Get user achievements"""
        achievements = []
        
        if user.files_uploaded >= 1:
            achievements.append("🎯 First Upload")
        if user.files_uploaded >= 10:
            achievements.append("📦 10 Files Uploaded")
        if user.files_uploaded >= 100:
            achievements.append("💎 100 Files Master")
        if user.total_size_uploaded >= 1024 * 1024 * 1024:  # 1GB
            achievements.append("💾 1GB+ Uploaded")
        if sum(f.views for f in files) >= 1000:
            achievements.append("👁 1K+ Views")
            
        return "\n".join(f"• {a}" for a in achievements) or "• No achievements yet"
        
    async def file_handler(self, message: Message):
        """Handle file uploads"""
        user_id = message.from_user.id
        
        # Check force subscribe
        if self.config.ENABLE_FORCE_SUB and self.config.FORCE_SUB_CHANNEL:
            try:
                member = await self.get_chat_member(
                    self.config.FORCE_SUB_CHANNEL,
                    user_id
                )
                if member.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.MEMBER]:
                    raise UserNotParticipant
            except UserNotParticipant:
                await self.send_force_sub_message(message)
                return
                
        # Get file info
        file_size = get_file_size(message)
        file_name = get_name(message)
        file_type = get_file_type(message)
        
        # Validate file
        valid, error_msg = validate_file_size(
            file_size, 
            self.config.MIN_FILE_SIZE, 
            self.config.MAX_FILE_SIZE
        )
        if not valid:
            await message.reply_text(f"❌ {error_msg}", quote=True)
            return
            
        valid, error_msg = validate_file_extension(
            file_name,
            self.config.ALLOWED_EXTENSIONS
        )
        if not valid:
            await message.reply_text(f"❌ {error_msg}", quote=True)
            return
            
        # Send processing message
        process_msg = await message.reply_text(
            "⏳ **Processing your file...**\n"
            f"📁 Name: `{file_name}`\n"
            f"📊 Size: {format_size(file_size)}",
            quote=True
        )
        
        try:
            # Forward to channel
            forwarded = await message.forward(self.config.BIN_CHANNEL)
            
            # Generate links
            file_hash = get_hash(forwarded)
            stream_link = f"{self.config.URL}watch/{forwarded.message_id}/{file_name}?hash={file_hash}"
            download_link = f"{self.config.URL}dl/{forwarded.message_id}/{file_name}?hash={file_hash}"
            short_link = f"{self.config.URL}{file_hash}"
            
            # Save to database
            media = get_media_from_message(message)
            file_stats = FileStats(
                file_id=media.file_id,
                message_id=forwarded.message_id,
                user_id=user_id,
                file_name=file_name,
                file_size=file_size,
                file_type=file_type,
                mime_type=getattr(media, "mime_type", None)
            )
            self.db_session.add(file_stats)
            
            # Update user stats
            user = self.db_session.query(User).filter_by(id=user_id).first()
            user.files_uploaded += 1
            user.total_size_uploaded += file_size
            user.last_activity = datetime.utcnow()
            
            self.db_session.commit()
            
            # Send success message
            success_text = f"""
✅ **File Uploaded Successfully!**

📁 **File Details:**
• **Name:** `{file_name}`
• **Size:** {format_size(file_size)}
• **Type:** {file_type.title()}

🔗 **Your Links:**
• **Stream Link:** [Click Here]({stream_link})
• **Download Link:** [Click Here]({download_link})
• **Short Link:** `{short_link}`

📊 **Statistics:**
• **Views:** 0
• **Downloads:** 0

💡 **Tip:** Share these links with anyone to let them stream or download your file!
"""
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("▶️ Stream", url=stream_link),
                    InlineKeyboardButton("📥 Download", url=download_link)
                ],
                [
                    InlineKeyboardButton("📊 Stats", callback_data=f"file_stats:{file_hash}"),
                    InlineKeyboardButton("🗑 Delete", callback_data=f"delete_file:{file_hash}")
                ],
                [
                    InlineKeyboardButton("🔗 Share", switch_inline_query=short_link)
                ]
            ])
            
            await process_msg.edit_text(
                success_text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            
            self.logger.info(f"File uploaded: {file_name} by user {user_id}")
            
        except FloodWait as e:
            await process_msg.edit_text(
                f"⏳ FloodWait: Please wait {e.x} seconds..."
            )
            await asyncio.sleep(e.x)
            await self.file_handler(message)  # Retry
            
        except Exception as e:
            self.logger.error(f"File upload error: {e}", exc_info=True)
            await process_msg.edit_text(
                "❌ **Error uploading file!**\n"
                "Please try again later or contact support."
            )
            
    async def admin_handler(self, message: Message):
        """Handle /admin command"""
        admin_text = """
👮 **Admin Panel**

**Available Commands:**

**User Management:**
• /users - List all users
• /user <user_id> - Get user info
• /ban <user_id> - Ban a user
• /unban <user_id> - Unban a user

**Broadcast:**
• /broadcast - Send message to all users
• /broadcast_stats - View broadcast statistics

**Statistics:**
• /stats_global - Global bot statistics
• /stats_files - File statistics
• /stats_users - User statistics

**Maintenance:**
• /backup - Backup database
• /logs - View recent logs
• /restart - Restart bot
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👥 Users", callback_data="admin_users"),
                InlineKeyboardButton("📊 Stats", callback_data="admin_stats")
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                InlineKeyboardButton("⚙️ Settings", callback_data="admin_settings")
            ],
            [InlineKeyboardButton("🏠 Home", callback_data="home")]
        ])
        
        await message.reply_text(admin_text, reply_markup=keyboard, quote=True)
        
    async def broadcast_handler(self, message: Message):
        """Handle /broadcast command"""
        if len(message.command) < 2:
            await message.reply_text(
                "**Usage:** /broadcast <message>\n"
                "**Example:** /broadcast Hello everyone!"
            )
            return
            
        broadcast_text = message.text.split(None, 1)[1]
        
        # Get all users
        users = self.db_session.query(User).filter_by(is_banned=False).all()
        total_users = len(users)
        
        # Send initial message
        status_msg = await message.reply_text(
            f"📢 **Broadcasting to {total_users} users...**\n"
            f"Progress: {create_progress_bar(0, total_users)}"
        )
        
        success_count = 0
        failed_count = 0
        
        for i, user in enumerate(users):
            try:
                await self.send_message(
                    user.id,
                    f"📢 **Broadcast Message**\n\n{broadcast_text}"
                )
                success_count += 1
            except Exception as e:
                failed_count += 1
                self.logger.error(f"Broadcast error for user {user.id}: {e}")
                
            # Update progress every 10 users
            if (i + 1) % 10 == 0 or i == total_users - 1:
                progress = create_progress_bar(i + 1, total_users)
                await status_msg.edit_text(
                    f"📢 **Broadcasting...**\n"
                    f"Progress: {progress}\n"
                    f"✅ Success: {success_count}\n"
                    f"❌ Failed: {failed_count}"
                )
                
        # Final message
        await status_msg.edit_text(
            f"✅ **Broadcast Completed!**\n\n"
            f"📊 **Results:**\n"
            f"• Total Users: {total_users}\n"
            f"• Success: {success_count}\n"
            f"• Failed: {failed_count}\n"
            f"• Success Rate: {(success_count/total_users*100):.1f}%"
        )
        
    async def users_handler(self, message: Message):
        """Handle /users command"""
        # Get statistics
        total_users = self.db_session.query(User).count()
        active_users = self.db_session.query(User).filter(
            User.last_activity >= datetime.utcnow() - timedelta(days=7)
        ).count()
        banned_users = self.db_session.query(User).filter_by(is_banned=True).count()
        premium_users = self.db_session.query(User).filter_by(is_premium=True).count()
        
        text = f"""
👥 **User Statistics**

**📊 Overview:**
• **Total Users:** {total_users:,}
• **Active (7d):** {active_users:,}
• **Banned:** {banned_users:,}
• **Premium:** {premium_users:,}

**📈 Growth:**
• **Today:** +{self._get_new_users_count(1)}
• **This Week:** +{self._get_new_users_count(7)}
• **This Month:** +{self._get_new_users_count(30)}

Use /user <user_id> to get specific user info.
"""
        
        await message.reply_text(text, quote=True)
        
    def _get_new_users_count(self, days: int) -> int:
        """Get count of new users in last N days"""
        since = datetime.utcnow() - timedelta(days=days)
        return self.db_session.query(User).filter(
            User.joined_date >= since
        ).count()
        
    async def callback_handler(self, callback_query: CallbackQuery):
        """Handle callback queries"""
        data = callback_query.data
        
        if data == "home":
            await self.send_welcome_message(callback_query.message)
            
        elif data == "help":
            await self.help_handler(callback_query.message)
            
        elif data == "stats":
            await self.stats_handler(callback_query.message)
            
        elif data == "about":
            await self.send_about_message(callback_query.message)
            
        elif data == "check_sub":
            await self.check_subscription(callback_query)
            
        elif data.startswith("file_stats:"):
            file_hash = data.split(":")[1]
            await self.show_file_stats(callback_query, file_hash)
            
        elif data.startswith("delete_file:"):
            file_hash = data.split(":")[1]
            await self.delete_file(callback_query, file_hash)
            
        await callback_query.answer()
        
    async def send_about_message(self, message: Message):
        """Send about message"""
        about_text = """
ℹ️ **About This Bot**

**🤖 Bot Information:**
• **Name:** File Stream Bot
• **Version:** 2.0
• **Language:** Python 3.10
• **Framework:** Pyrogram

**👨‍💻 Developer:**
• **Name:** Your Name
• **Contact:** @yourusername

**🔧 Features:**
• High-speed file streaming
• Support for all file types
• Real-time statistics
• User-friendly interface
• 24/7 availability

**📊 Server Stats:**
• **Uptime:** 99.9%
• **Response Time:** <100ms
• **Storage:** Unlimited

**🙏 Credits:**
Special thanks to all contributors and users!

**📝 Source Code:**
This bot is open source!
[GitHub Repository](https://github.com/yourusername/repo)
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/yourusername"),
                InlineKeyboardButton("📦 Source", url="https://github.com/yourusername/repo")
            ],
            [InlineKeyboardButton("🏠 Home", callback_data="home")]
        ])
        
        await message.edit_text(about_text, reply_markup=keyboard)
        
    async def check_subscription(self, callback_query: CallbackQuery):
        """Check if user has subscribed"""
        user_id = callback_query.from_user.id
        
        try:
            member = await self.get_chat_member(
                self.config.FORCE_SUB_CHANNEL,
                user_id
            )
            if member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.MEMBER]:
                await callback_query.message.edit_text(
                    "✅ **Thank you for subscribing!**\n"
                    "You can now use the bot. Send /start to begin."
                )
            else:
                await callback_query.answer(
                    "❌ You haven't joined the channel yet!",
                    show_alert=True
                )
        except Exception as e:
            self.logger.error(f"Subscription check error: {e}")
            await callback_query.answer(
                "❌ Error checking subscription. Please try again.",
                show_alert=True
            )
            
    async def show_file_stats(self, callback_query: CallbackQuery, file_hash: str):
        """Show file statistics"""
        # Implementation for showing file stats
        pass
        
    async def delete_file(self, callback_query: CallbackQuery, file_hash: str):
        """Delete a file"""
        # Implementation for deleting files
        pass
        
    async def update_stats_task(self):
        """Background task to update bot statistics"""
        while True:
            try:
                stats = await get_bot_stats(self.db_session)
                
                # Update statistics
                stats.total_users = self.db_session.query(User).count()
                stats.active_users_daily = self.db_session.query(User).filter(
                    User.last_activity >= datetime.utcnow() - timedelta(days=1)
                ).count()
                stats.total_files = self.db_session.query(FileStats).count()
                
                self.db_session.commit()
                
            except Exception as e:
                self.logger.error(f"Stats update error: {e}")
                
            await asyncio.sleep(300)  # Update every 5 minutes