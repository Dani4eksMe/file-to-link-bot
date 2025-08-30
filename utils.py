"""Utility functions for the bot"""

import os
import sys
import logging
import hashlib
import humanize
from typing import Union, Optional
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from colorlog import ColoredFormatter
from pyrogram.types import Message
from pyrogram.file_id import FileId


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup colored logging"""
    log_format = "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Console handler with colors
    console_formatter = ColoredFormatter(
        log_format,
        datefmt=date_format,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    
    # File handler without colors
    file_handler = logging.FileHandler("bot.log", mode="a", encoding="utf-8")
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt=date_format
    )
    file_handler.setFormatter(file_formatter)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Reduce noise from other libraries
    logging.getLogger("pyrogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


def check_environment() -> bool:
    """Check if all required environment variables are set"""
    required_vars = ["API_ID", "API_HASH", "BOT_TOKEN", "BIN_CHANNEL"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
            
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("   Please check your .env file or environment settings.")
        return False
        
    return True


def get_hash(message: Message) -> str:
    """Generate unique hash for a message"""
    media = get_media_from_message(message)
    if media:
        return hashlib.md5(media.file_unique_id.encode()).hexdigest()[:12]
    return ""


def get_media_from_message(message: Message):
    """Extract media from message"""
    media_types = [
        "document", "video", "audio", "animation",
        "voice", "video_note", "photo", "sticker"
    ]
    
    for media_type in media_types:
        media = getattr(message, media_type, None)
        if media:
            return media
    return None


def get_name(message: Message) -> str:
    """Get file name from message"""
    media = get_media_from_message(message)
    
    if not media:
        return "file"
        
    # Get filename from different media types
    if hasattr(media, "file_name") and media.file_name:
        return media.file_name
    elif message.photo:
        return f"photo_{message.photo.file_unique_id}.jpg"
    elif message.video:
        return f"video_{media.file_unique_id}.mp4"
    elif message.audio:
        title = media.title or "audio"
        performer = media.performer or "unknown"
        return f"{performer} - {title}.mp3"
    elif message.voice:
        return f"voice_{media.file_unique_id}.ogg"
    elif message.video_note:
        return f"video_note_{media.file_unique_id}.mp4"
    elif message.sticker:
        return f"sticker_{media.file_unique_id}.webp"
    elif message.animation:
        return f"animation_{media.file_unique_id}.gif"
        
    return f"file_{media.file_unique_id}"


def get_file_size(message: Message) -> int:
    """Get file size from message"""
    media = get_media_from_message(message)
    if media and hasattr(media, "file_size"):
        return media.file_size or 0
    return 0


def get_file_type(message: Message) -> str:
    """Get file type from message"""
    if message.document:
        return "document"
    elif message.video:
        return "video"
    elif message.audio:
        return "audio"
    elif message.photo:
        return "photo"
    elif message.voice:
        return "voice"
    elif message.video_note:
        return "video_note"
    elif message.sticker:
        return "sticker"
    elif message.animation:
        return "animation"
    return "unknown"


def format_size(size: int) -> str:
    """Format file size in human readable format"""
    return humanize.naturalsize(size, binary=True)


def format_duration(seconds: int) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def get_readable_time(seconds: int) -> str:
    """Convert seconds to readable time format"""
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f"{days}d "
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f"{hours}h "
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f"{minutes}m "
    seconds = int(seconds)
    result += f"{seconds}s"
    return result


def get_readable_file_size(size_in_bytes: Union[int, float]) -> str:
    """Convert bytes to readable file size"""
    if size_in_bytes is None:
        return "0B"
    size_in_bytes = int(size_in_bytes)
    if size_in_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB")
    i = 0
    while size_in_bytes >= 1024 and i < len(size_name) - 1:
        size_in_bytes /= 1024
        i += 1
    return f"{size_in_bytes:.2f} {size_name[i]}"


def encode_file_id(file_id: str) -> str:
    """Encode file_id for URL"""
    return quote_plus(file_id)


def decode_file_id(encoded_id: str) -> str:
    """Decode file_id from URL"""
    return encoded_id


def get_file_ids(message: Message) -> Optional[FileId]:
    """Get file_id from message"""
    media = get_media_from_message(message)
    if media and hasattr(media, "file_id"):
        return FileId.decode(media.file_id)
    return None


def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Create a text progress bar"""
    filled = int(length * current // total)
    bar = "█" * filled + "░" * (length - filled)
    percentage = current * 100 / total
    return f"[{bar}] {percentage:.1f}%"


async def progress_callback(current: int, total: int, message: Message, start_time: float, text: str = ""):
    """Progress callback for uploads/downloads"""
    now = datetime.now()
    diff = (now - datetime.fromtimestamp(start_time)).total_seconds()
    
    if diff < 1 or current == total:
        return
        
    speed = current / diff
    time_left = (total - current) / speed
    
    progress = create_progress_bar(current, total, 15)
    size_done = get_readable_file_size(current)
    size_total = get_readable_file_size(total)
    speed_str = get_readable_file_size(speed) + "/s"
    eta = get_readable_time(int(time_left))
    
    text = f"{text}\n" if text else ""
    text += f"**Progress:** {progress}\n"
    text += f"**Done:** {size_done} / {size_total}\n"
    text += f"**Speed:** {speed_str}\n"
    text += f"**ETA:** {eta}"
    
    try:
        await message.edit_text(text)
    except Exception:
        pass


def validate_file_size(size: int, min_size: int = 0, max_size: int = 2147483648) -> tuple[bool, str]:
    """Validate file size"""
    if size < min_size:
        return False, f"File too small. Minimum size: {format_size(min_size)}"
    if size > max_size:
        return False, f"File too large. Maximum size: {format_size(max_size)}"
    return True, ""


def validate_file_extension(filename: str, allowed_extensions: list) -> tuple[bool, str]:
    """Validate file extension"""
    if not allowed_extensions:
        return True, ""
        
    ext = os.path.splitext(filename)[1].lower()
    if ext and ext[1:] in allowed_extensions:
        return True, ""
        
    return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"