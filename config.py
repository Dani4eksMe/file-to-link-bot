"""Configuration module for the bot"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration class"""
    
    # Required settings
    API_ID: int = int(os.environ.get("API_ID", "0"))
    API_HASH: str = os.environ.get("API_HASH", "")
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
    
    # Channel settings
    BIN_CHANNEL: int = int(os.environ.get("BIN_CHANNEL", "0"))
    LOG_CHANNEL: Optional[int] = int(os.environ.get("LOG_CHANNEL", "0")) if os.environ.get("LOG_CHANNEL") else None
    
    # Web server settings
    PORT: int = int(os.environ.get("PORT", "8080"))
    BIND_ADDRESS: str = os.environ.get("WEB_SERVER_BIND_ADDRESS", "0.0.0.0")
    FQDN: str = os.environ.get("FQDN", BIND_ADDRESS)
    HAS_SSL: bool = os.environ.get("HAS_SSL", "False").lower() == "true"
    NO_PORT: bool = os.environ.get("NO_PORT", "False").lower() == "true"
    
    # Bot settings
    WORKERS: int = int(os.environ.get("WORKERS", "8"))
    SLEEP_THRESHOLD: int = int(os.environ.get("SLEEP_THRESHOLD", "60"))
    PING_INTERVAL: int = int(os.environ.get("PING_INTERVAL", "1200"))
    
    # Admin settings
    ADMINS: list = list(map(int, os.environ.get("ADMINS", "").split())) if os.environ.get("ADMINS") else []
    OWNER_ID: int = int(os.environ.get("OWNER_ID", "0"))
    
    # Feature flags
    ENABLE_STATS: bool = os.environ.get("ENABLE_STATS", "True").lower() == "true"
    ENABLE_BROADCAST: bool = os.environ.get("ENABLE_BROADCAST", "True").lower() == "true"
    ENABLE_FORCE_SUB: bool = os.environ.get("ENABLE_FORCE_SUB", "False").lower() == "true"
    FORCE_SUB_CHANNEL: Optional[str] = os.environ.get("FORCE_SUB_CHANNEL")
    
    # Limits
    MAX_FILE_SIZE: int = int(os.environ.get("MAX_FILE_SIZE", str(2 * 1024 * 1024 * 1024)))  # 2GB default
    MIN_FILE_SIZE: int = int(os.environ.get("MIN_FILE_SIZE", "0"))
    ALLOWED_EXTENSIONS: list = os.environ.get("ALLOWED_EXTENSIONS", "").split() if os.environ.get("ALLOWED_EXTENSIONS") else []
    
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///data/bot.db")
    
    # Logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    
    # Other settings
    MULTI_CLIENT: bool = os.environ.get("MULTI_CLIENT", "False").lower() == "true"
    MULTI_TOKEN: list = os.environ.get("MULTI_TOKEN", "").split() if os.environ.get("MULTI_TOKEN") else []
    
    # Heroku detection
    ON_HEROKU: bool = "DYNO" in os.environ
    APP_NAME: Optional[str] = os.environ.get("APP_NAME") if ON_HEROKU else None
    
    @property
    def URL(self) -> str:
        """Generate the public URL"""
        if self.ON_HEROKU:
            return f"https://{self.APP_NAME}.herokuapp.com/"
        else:
            protocol = "https" if self.HAS_SSL else "http"
            port_part = "" if self.NO_PORT else f":{self.PORT}"
            return f"{protocol}://{self.FQDN}{port_part}/"
            
    def validate(self) -> bool:
        """Validate required configuration"""
        if not self.API_ID or self.API_ID == 0:
            return False
        if not self.API_HASH:
            return False
        if not self.BOT_TOKEN:
            return False
        if not self.BIN_CHANNEL or self.BIN_CHANNEL == 0:
            return False
        return True