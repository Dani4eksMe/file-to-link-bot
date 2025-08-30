#!/bin/bash

# Enhanced Telegram File Stream Bot Runner Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║          📁 Telegram File Stream Bot Runner 📁           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo -e "${GREEN}✓ Python $python_version is installed${NC}"
else
    echo -e "${RED}✗ Python 3.10+ is required. Found: $python_version${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}No .env file found. Creating from example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file. Please edit it with your credentials.${NC}"
        exit 1
    else
        echo -e "${RED}✗ No .env.example file found!${NC}"
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install/upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p data static plugins
echo -e "${GREEN}✓ Directories created${NC}"

# Check environment variables
echo -e "${YELLOW}Checking environment variables...${NC}"
source .env

if [ -z "$API_ID" ] || [ -z "$API_HASH" ] || [ -z "$BOT_TOKEN" ] || [ -z "$BIN_CHANNEL" ]; then
    echo -e "${RED}✗ Missing required environment variables!${NC}"
    echo -e "${RED}Please edit .env file with your credentials.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment variables loaded${NC}"

# Run the bot
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║               🚀 Starting the bot... 🚀                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

python app.py