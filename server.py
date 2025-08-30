"""Web server module for file streaming"""

import os
import logging
import mimetypes
from typing import Optional
from datetime import datetime

from aiohttp import web
from aiohttp.web import Response, StreamResponse
from pyrogram.file_id import FileId
from pyrogram.errors import MessageNotFound

from config import Config
from database import FileStats, update_file_stats
from utils import get_readable_file_size, get_readable_time


class WebServer:
    """Web server for streaming files"""
    
    def __init__(self, bot, config: Config, db_session):
        self.bot = bot
        self.config = config
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
        
    def create_app(self) -> web.Application:
        """Create and configure the web application"""
        app = web.Application()
        
        # Add routes
        app.router.add_get("/", self.index_handler)
        app.router.add_get("/stats", self.stats_handler)
        app.router.add_get("/watch/{message_id}/{filename}", self.stream_handler)
        app.router.add_get("/dl/{message_id}/{filename}", self.download_handler)
        app.router.add_get("/{file_hash}", self.short_link_handler)
        app.router.add_get("/thumb/{message_id}", self.thumbnail_handler)
        
        # Static files
        app.router.add_static("/static", "static", show_index=True)
        
        return app
        
    async def index_handler(self, request: web.Request) -> Response:
        """Handle index page"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Stream Bot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 600px;
            width: 90%;
        }
        
        h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .emoji {
            font-size: 5rem;
            margin-bottom: 1rem;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        
        p {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .feature {
            padding: 1.5rem;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        
        .feature:hover {
            transform: translateY(-5px);
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .feature-title {
            font-weight: 600;
            margin-bottom: 0.25rem;
        }
        
        .feature-desc {
            font-size: 0.9rem;
            color: #666;
        }
        
        .cta {
            margin-top: 2rem;
        }
        
        .btn {
            display: inline-block;
            padding: 1rem 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 30px;
            font-weight: 600;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 20px rgba(0, 0, 0, 0.3);
        }
        
        .stats {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-around;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #666;
            margin-top: 0.25rem;
        }
        
        footer {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #e0e0e0;
            color: #999;
            font-size: 0.9rem;
        }
        
        footer a {
            color: #667eea;
            text-decoration: none;
        }
        
        footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">📁</div>
        <h1>File Stream Bot</h1>
        <p>Transform your Telegram files into instant streaming links!</p>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">🚀</div>
                <div class="feature-title">Fast Streaming</div>
                <div class="feature-desc">Lightning-fast file delivery</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🔒</div>
                <div class="feature-title">Secure</div>
                <div class="feature-desc">Your files are safe with us</div>
            </div>
            <div class="feature">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Statistics</div>
                <div class="feature-desc">Track views and downloads</div>
            </div>
            <div class="feature">
                <div class="feature-icon">♾️</div>
                <div class="feature-title">No Limits</div>
                <div class="feature-desc">Files up to 2GB supported</div>
            </div>
        </div>
        
        <div class="cta">
            <a href="https://t.me/{bot_username}" class="btn">Start Using Bot</a>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number" id="total-files">0</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="total-users">0</div>
                <div class="stat-label">Active Users</div>
            </div>
            <div class="stat">
                <div class="stat-number" id="total-views">0</div>
                <div class="stat-label">Total Views</div>
            </div>
        </div>
        
        <footer>
            Made with ❤️ by <a href="https://t.me/yourusername">Your Name</a>
        </footer>
    </div>
    
    <script>
        // Animate numbers
        function animateNumber(id, target) {
            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                document.getElementById(id).textContent = Math.floor(current).toLocaleString();
            }, 20);
        }
        
        // Load stats
        fetch('/stats')
            .then(res => res.json())
            .then(data => {
                animateNumber('total-files', data.total_files);
                animateNumber('total-users', data.total_users);
                animateNumber('total-views', data.total_views);
            });
    </script>
</body>
</html>
""".replace("{bot_username}", self.bot.username or "filestream_bot")
        
        return web.Response(text=html, content_type="text/html")
        
    async def stats_handler(self, request: web.Request) -> Response:
        """Handle stats API endpoint"""
        from database import BotStats
        
        stats = self.db_session.query(BotStats).first()
        if not stats:
            stats = BotStats()
            
        data = {
            "total_files": stats.total_files,
            "total_users": stats.total_users,
            "total_views": stats.total_views,
            "total_downloads": stats.total_downloads,
            "uptime": get_readable_time(
                int((datetime.utcnow() - stats.uptime_start).total_seconds())
            )
        }
        
        return web.json_response(data)
        
    async def stream_handler(self, request: web.Request) -> StreamResponse:
        """Handle file streaming"""
        message_id = int(request.match_info['message_id'])
        filename = request.match_info['filename']
        file_hash = request.query.get('hash')
        
        if not file_hash:
            return web.Response(text="Invalid request", status=400)
            
        return await self._serve_file(message_id, filename, file_hash, "stream")
        
    async def download_handler(self, request: web.Request) -> StreamResponse:
        """Handle file downloads"""
        message_id = int(request.match_info['message_id'])
        filename = request.match_info['filename']
        file_hash = request.query.get('hash')
        
        if not file_hash:
            return web.Response(text="Invalid request", status=400)
            
        return await self._serve_file(message_id, filename, file_hash, "download")
        
    async def short_link_handler(self, request: web.Request) -> Response:
        """Handle short links"""
        file_hash = request.match_info['file_hash']
        
        # Find file by hash
        file_stat = None
        for fs in self.db_session.query(FileStats).all():
            msg = await self.bot.get_messages(self.config.BIN_CHANNEL, fs.message_id)
            if get_hash(msg) == file_hash:
                file_stat = fs
                break
                
        if not file_stat:
            return web.Response(text="File not found", status=404)
            
        # Create HTML page with file info
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{file_stat.file_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }}
        
        .card {{
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 90%;
            text-align: center;
        }}
        
        .file-icon {{
            font-size: 4rem;
            margin-bottom: 1rem;
        }}
        
        h1 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
            word-break: break-word;
        }}
        
        .info {{
            color: #666;
            margin-bottom: 2rem;
        }}
        
        .info-item {{
            margin: 0.5rem 0;
        }}
        
        .buttons {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .btn {{
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: background 0.3s ease;
        }}
        
        .btn:hover {{
            background: #5a67d8;
        }}
        
        .btn-secondary {{
            background: #48bb78;
        }}
        
        .btn-secondary:hover {{
            background: #38a169;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="file-icon">📄</div>
        <h1>{file_stat.file_name}</h1>
        <div class="info">
            <div class="info-item">📊 Size: {get_readable_file_size(file_stat.file_size)}</div>
            <div class="info-item">📁 Type: {file_stat.file_type}</div>
            <div class="info-item">👁 Views: {file_stat.views}</div>
            <div class="info-item">📥 Downloads: {file_stat.downloads}</div>
        </div>
        <div class="buttons">
            <a href="/watch/{file_stat.message_id}/{file_stat.file_name}?hash={file_hash}" class="btn">▶️ Stream</a>
            <a href="/dl/{file_stat.message_id}/{file_stat.file_name}?hash={file_hash}" class="btn btn-secondary">📥 Download</a>
        </div>
    </div>
</body>
</html>
"""
        
        return web.Response(text=html, content_type="text/html")
        
    async def thumbnail_handler(self, request: web.Request) -> Response:
        """Handle thumbnail requests"""
        message_id = int(request.match_info['message_id'])
        
        try:
            message = await self.bot.get_messages(self.config.BIN_CHANNEL, message_id)
            if message.photo:
                # Download thumbnail
                thumb_path = await self.bot.download_media(
                    message.photo.file_id,
                    file_name=f"thumb_{message_id}.jpg"
                )
                
                with open(thumb_path, 'rb') as f:
                    data = f.read()
                    
                os.remove(thumb_path)
                
                return web.Response(
                    body=data,
                    content_type='image/jpeg',
                    headers={
                        'Cache-Control': 'public, max-age=3600'
                    }
                )
        except Exception as e:
            self.logger.error(f"Thumbnail error: {e}")
            
        # Return default thumbnail
        return web.Response(text="No thumbnail", status=404)
        
    async def _serve_file(self, message_id: int, filename: str, 
                         file_hash: str, mode: str) -> StreamResponse:
        """Serve file for streaming or download"""
        try:
            # Get message from channel
            message = await self.bot.get_messages(self.config.BIN_CHANNEL, message_id)
            
            if not message or not message.media:
                return web.Response(text="File not found", status=404)
                
            # Verify hash
            if get_hash(message) != file_hash:
                return web.Response(text="Invalid hash", status=403)
                
            # Update statistics
            await update_file_stats(self.db_session, message.media.file_id, mode)
            
            # Get file info
            media = get_media_from_message(message)
            file_size = getattr(media, "file_size", 0)
            mime_type = getattr(media, "mime_type", None)
            
            if not mime_type:
                mime_type, _ = mimetypes.guess_type(filename)
                mime_type = mime_type or "application/octet-stream"
                
            # Prepare response
            response = StreamResponse(
                status=200,
                headers={
                    'Content-Type': mime_type,
                    'Content-Length': str(file_size),
                    'Accept-Ranges': 'bytes',
                    'Cache-Control': 'public, max-age=3600'
                }
            )
            
            if mode == "download":
                response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            else:
                response.headers['Content-Disposition'] = f'inline; filename="{filename}"'
                
            # Handle range requests
            range_header = request.headers.get('Range')
            if range_header:
                from_bytes, to_bytes = self._parse_range(range_header, file_size)
                response.status = 206
                response.headers['Content-Range'] = f'bytes {from_bytes}-{to_bytes}/{file_size}'
                response.headers['Content-Length'] = str(to_bytes - from_bytes + 1)
            else:
                from_bytes = 0
                to_bytes = file_size - 1
                
            await response.prepare(request)
            
            # Stream file
            async for chunk in self.bot.stream_media(message, from_bytes, to_bytes - from_bytes + 1):
                await response.write(chunk)
                
            return response
            
        except MessageNotFound:
            return web.Response(text="File not found", status=404)
        except Exception as e:
            self.logger.error(f"File serving error: {e}", exc_info=True)
            return web.Response(text="Internal server error", status=500)
            
    def _parse_range(self, range_header: str, file_size: int) -> tuple[int, int]:
        """Parse range header"""
        try:
            range_value = range_header.replace('bytes=', '')
            from_bytes, to_bytes = range_value.split('-')
            
            from_bytes = int(from_bytes) if from_bytes else 0
            to_bytes = int(to_bytes) if to_bytes else file_size - 1
            
            return max(0, from_bytes), min(to_bytes, file_size - 1)
        except Exception:
            return 0, file_size - 1
            
    def get_hash(self, message) -> str:
        """Get hash from message"""
        from utils import get_hash
        return get_hash(message)