"""Database models and utilities"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

Base = declarative_base()

class User(Base):
    """User model for storing user information and preferences"""
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), default='en')
    
    # Statistics
    files_uploaded = Column(Integer, default=0)
    total_size_uploaded = Column(BigInteger, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User status
    is_banned = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    joined_date = Column(DateTime, default=datetime.utcnow)
    
    # Settings
    notification_enabled = Column(Boolean, default=True)
    show_file_info = Column(Boolean, default=True)
    custom_caption = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
        
    @property
    def full_name(self):
        """Get user's full name"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) or "Anonymous"

class FileStats(Base):
    """File statistics model"""
    __tablename__ = 'file_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_id = Column(String(255), unique=True, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    
    # File information
    file_name = Column(String(500), nullable=True)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(50), nullable=False)
    mime_type = Column(String(100), nullable=True)
    
    # Statistics
    views = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FileStats(file_id={self.file_id}, views={self.views})>"

class BotStats(Base):
    """Global bot statistics"""
    __tablename__ = 'bot_stats'
    
    id = Column(Integer, primary_key=True, default=1)
    
    # User statistics
    total_users = Column(Integer, default=0)
    active_users_daily = Column(Integer, default=0)
    active_users_weekly = Column(Integer, default=0)
    active_users_monthly = Column(Integer, default=0)
    banned_users = Column(Integer, default=0)
    
    # File statistics
    total_files = Column(Integer, default=0)
    total_size = Column(BigInteger, default=0)
    total_views = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    
    # Performance metrics
    avg_response_time = Column(Float, default=0.0)
    uptime_start = Column(DateTime, default=datetime.utcnow)
    
    # Last updated
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<BotStats(users={self.total_users}, files={self.total_files})>"

class Broadcast(Base):
    """Broadcast messages history"""
    __tablename__ = 'broadcasts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, nullable=False)
    message = Column(Text, nullable=False)
    
    # Statistics
    total_users = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # Status
    status = Column(String(20), default='pending')  # pending, in_progress, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Broadcast(id={self.id}, status={self.status})>"

class AdminLog(Base):
    """Admin action logs"""
    __tablename__ = 'admin_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, nullable=False)
    action = Column(String(100), nullable=False)
    target_user_id = Column(BigInteger, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AdminLog(admin={self.admin_id}, action={self.action})>"

# Database helper functions
async def get_or_create_user(session, user_id, **kwargs):
    """Get existing user or create new one"""
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        user = User(id=user_id, **kwargs)
        session.add(user)
        session.commit()
    else:
        # Update user info if provided
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        session.commit()
    return user

async def update_file_stats(session, file_id, action='view'):
    """Update file statistics"""
    file_stat = session.query(FileStats).filter_by(file_id=file_id).first()
    if file_stat:
        if action == 'view':
            file_stat.views += 1
        elif action == 'download':
            file_stat.downloads += 1
        file_stat.last_accessed = datetime.utcnow()
        session.commit()

async def get_bot_stats(session):
    """Get or create bot statistics"""
    stats = session.query(BotStats).first()
    if not stats:
        stats = BotStats()
        session.add(stats)
        session.commit()
    return stats