#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram File Stream Bot - Enhanced Version
A beautiful and functional bot for streaming files via web links
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Add WebStreamer to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aiohttp import web
from pyrogram import Client, idle
from pyrogram.errors import FloodWait
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import configurations and utilities
from config import Config
from database import Base, User, FileStats
from bot import TelegramBot
from server import WebServer
from utils import setup_logging, check_environment

# ASCII Art Banner
BANNER = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     ████████╗███████╗██╗     ███████╗    ██████╗  ██████╗████████╗
║     ╚══██╔══╝██╔════╝██║     ██╔════╝    ██╔══██╗██╔═══██╗╚══██╔══╝
║        ██║   █████╗  ██║     █████╗      ██████╔╝██║   ██║   ██║   
║        ██║   ██╔══╝  ██║     ██╔══╝      ██╔══██╗██║   ██║   ██║   
║        ██║   ███████╗███████╗███████╗    ██████╔╝╚██████╔╝   ██║   
║        ╚═╝   ╚══════╝╚══════╝╚══════╝    ╚═════╝  ╚═════╝    ╚═╝   
║                                                          ║
║              File Stream Bot - Enhanced Edition          ║
║                    Powered by Pyrogram                   ║
╚══════════════════════════════════════════════════════════╝
"""

class Application:
    """Main application class that manages the bot and web server"""
    
    def __init__(self):
        self.config = Config()
        self.logger = setup_logging(self.config.LOG_LEVEL)
        self.bot = None
        self.web_server = None
        self.db_engine = None
        self.db_session = None
        
    async def initialize_database(self):
        """Initialize SQLite database for storing statistics"""
        self.logger.info("🔧 Initializing database...")
        db_path = Path("data/bot.db")
        db_path.parent.mkdir(exist_ok=True)
        
        self.db_engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.db_engine)
        Session = sessionmaker(bind=self.db_engine)
        self.db_session = Session()
        self.logger.info("✅ Database initialized successfully")
        
    async def initialize_bot(self):
        """Initialize and start the Telegram bot"""
        self.logger.info("🤖 Initializing Telegram Bot...")
        
        self.bot = TelegramBot(
            name="FileStreamBot",
            api_id=self.config.API_ID,
            api_hash=self.config.API_HASH,
            bot_token=self.config.BOT_TOKEN,
            config=self.config,
            db_session=self.db_session
        )
        
        await self.bot.start()
        bot_info = await self.bot.get_me()
        self.bot.username = bot_info.username
        
        self.logger.info(f"✅ Bot started: @{bot_info.username}")
        self.logger.info(f"   Name: {bot_info.first_name}")
        self.logger.info(f"   ID: {bot_info.id}")
        
    async def initialize_web_server(self):
        """Initialize and start the web server"""
        self.logger.info("🌐 Initializing Web Server...")
        
        self.web_server = WebServer(
            bot=self.bot,
            config=self.config,
            db_session=self.db_session
        )
        
        app = self.web_server.create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        
        bind_address = "0.0.0.0" if self.config.ON_HEROKU else self.config.BIND_ADDRESS
        site = web.TCPSite(runner, bind_address, self.config.PORT)
        await site.start()
        
        self.logger.info(f"✅ Web server started on {bind_address}:{self.config.PORT}")
        self.logger.info(f"   Public URL: {self.config.URL}")
        
    async def start_services(self):
        """Start all services"""
        print(BANNER)
        
        # Check environment
        if not check_environment():
            self.logger.error("❌ Environment check failed. Please check your configuration.")
            sys.exit(1)
            
        try:
            # Initialize components
            await self.initialize_database()
            await self.initialize_bot()
            await self.initialize_web_server()
            
            # Start background tasks
            if self.config.ENABLE_STATS:
                asyncio.create_task(self.bot.update_stats_task())
                
            if self.config.ON_HEROKU:
                asyncio.create_task(self.keep_alive())
                
            self.logger.info("✨ All services started successfully!")
            self.logger.info("🚀 Bot is ready to use!")
            
            # Keep the bot running
            await idle()
            
        except Exception as e:
            self.logger.error(f"❌ Error starting services: {e}", exc_info=True)
            await self.cleanup()
            sys.exit(1)
            
    async def keep_alive(self):
        """Keep the Heroku app alive"""
        while True:
            await asyncio.sleep(self.config.PING_INTERVAL)
            try:
                async with self.bot.session.get(self.config.URL) as resp:
                    self.logger.debug(f"Keep-alive ping: {resp.status}")
            except Exception as e:
                self.logger.error(f"Keep-alive error: {e}")
                
    async def cleanup(self):
        """Cleanup resources"""
        self.logger.info("🧹 Cleaning up resources...")
        
        if self.bot:
            await self.bot.stop()
            
        if self.db_session:
            self.db_session.close()
            
        self.logger.info("👋 Goodbye!")
        
def main():
    """Main entry point"""
    app = Application()
    
    # Create event loop
    if sys.version_info[1] > 9:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
        
    try:
        loop.run_until_complete(app.start_services())
    except KeyboardInterrupt:
        print("\n⏹️  Received interrupt signal")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
    finally:
        loop.run_until_complete(app.cleanup())
        loop.close()

if __name__ == "__main__":
    main()