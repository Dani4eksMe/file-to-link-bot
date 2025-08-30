# 📁 Telegram File Stream Bot - Enhanced Edition

A powerful and beautiful Telegram bot for streaming files with advanced features and modern UI.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Pyrogram](https://img.shields.io/badge/pyrogram-2.0.106-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

## ✨ Features

### 🚀 Core Features
- **High-Speed Streaming** - Lightning-fast file delivery with multi-threaded support
- **Universal File Support** - Handle any file type up to 2GB
- **Beautiful Web Interface** - Modern, responsive design for file pages
- **Real-time Statistics** - Track views, downloads, and user activity
- **Smart URL System** - Short links, streaming links, and download links

### 👥 User Features
- **User Dashboard** - Personal statistics and file management
- **Multi-language Support** - Automatic language detection
- **File History** - Track all uploaded files
- **Achievement System** - Gamification for user engagement
- **Custom Captions** - Personalize file descriptions

### 👮 Admin Features
- **Admin Panel** - Complete bot management interface
- **User Management** - Ban/unban users, view user details
- **Broadcast System** - Send messages to all users
- **Detailed Analytics** - Global statistics and insights
- **Database Backup** - Automated backup system

### 🛡️ Security Features
- **Force Subscribe** - Require channel membership
- **File Validation** - Size and type restrictions
- **Rate Limiting** - Prevent abuse
- **Secure Hashing** - Protected file URLs

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Telegram API credentials from [my.telegram.org](https://my.telegram.org)
- A Telegram bot token from [@BotFather](https://t.me/botfather)
- A channel for storing files

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/telegram-file-stream-bot.git
cd telegram-file-stream-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Run the bot**
```bash
python app.py
```

## 📋 Configuration

### Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `API_ID` | Telegram API ID | `12345678` |
| `API_HASH` | Telegram API Hash | `abcdef1234567890` |
| `BOT_TOKEN` | Bot token from BotFather | `123456:ABC-DEF1234...` |
| `BIN_CHANNEL` | Channel ID for file storage | `-1001234567890` |

### Optional Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Web server port | `8080` |
| `ADMINS` | Admin user IDs (space-separated) | `""` |
| `FORCE_SUB_CHANNEL` | Channel for force subscribe | `None` |
| `MAX_FILE_SIZE` | Maximum file size in bytes | `2147483648` (2GB) |
| `DATABASE_URL` | Database connection URL | `sqlite:///data/bot.db` |

## 🏗️ Project Structure

```
telegram-file-stream-bot/
├── app.py              # Main application file
├── bot.py              # Bot handlers and commands
├── server.py           # Web server for streaming
├── database.py         # Database models
├── config.py           # Configuration management
├── utils.py            # Utility functions
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables example
├── static/             # Static web assets
├── data/              # Database and temporary files
└── plugins/           # Additional bot plugins
```

## 🤖 Bot Commands

### User Commands
- `/start` - Start the bot and see welcome message
- `/help` - Show help information
- `/stats` - View your personal statistics
- `/about` - Information about the bot

### Admin Commands
- `/admin` - Access admin panel
- `/broadcast <message>` - Send message to all users
- `/users` - View user statistics
- `/user <id>` - Get specific user information
- `/ban <id>` - Ban a user
- `/unban <id>` - Unban a user

## 🌐 Web Interface

The bot includes a beautiful web interface accessible at your configured URL:

- **Home Page** (`/`) - Landing page with bot information
- **File Page** (`/{hash}`) - Individual file information and download
- **Streaming** (`/watch/{id}/{name}`) - Stream files directly in browser
- **Download** (`/dl/{id}/{name}`) - Direct download links
- **Statistics** (`/stats`) - Real-time bot statistics API

## 📊 Database Schema

The bot uses SQLAlchemy with the following models:

- **User** - User information and preferences
- **FileStats** - File upload and view statistics
- **BotStats** - Global bot statistics
- **Broadcast** - Broadcast history
- **AdminLog** - Admin action logs

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production (SystemD)
```bash
sudo cp telegram-file-bot.service /etc/systemd/system/
sudo systemctl enable telegram-file-bot
sudo systemctl start telegram-file-bot
```

### Docker
```bash
docker build -t file-stream-bot .
docker run -d --name bot -p 8080:8080 --env-file .env file-stream-bot
```

### Heroku
```bash
heroku create your-app-name
heroku config:set $(cat .env | xargs)
git push heroku main
```

## 🛠️ Advanced Configuration

### Multi-Client Mode
For handling high loads, enable multi-client mode:
```env
MULTI_CLIENT=True
MULTI_TOKEN=token1 token2 token3
```

### Custom Domain
Configure custom domain with SSL:
```env
FQDN=files.yourdomain.com
HAS_SSL=True
NO_PORT=True
```

### Database Options
Use PostgreSQL for production:
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

## 📈 Monitoring

The bot includes comprehensive logging and monitoring:

- **Colored Console Logs** - Easy-to-read development logs
- **File Logging** - Persistent logs in `bot.log`
- **Sentry Integration** - Error tracking (optional)
- **Performance Metrics** - Response time tracking

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pyrogram](https://github.com/pyrogram/pyrogram) - MTProto API framework
- [aiohttp](https://github.com/aio-libs/aiohttp) - Async HTTP server
- Original FileStreamBot developers
- All contributors and users

## 📞 Support

- **Telegram Group**: [@your_support_group](https://t.me/your_support_group)
- **Updates Channel**: [@your_updates_channel](https://t.me/your_updates_channel)
- **Issues**: [GitHub Issues](https://github.com/yourusername/repo/issues)

---

Made with ❤️ by [Your Name](https://t.me/yourusername)