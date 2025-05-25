import os
import time
import logging
from telegram.constants import ParseMode
import asyncio
import random
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from telegram.ext import ChatMemberHandler
from telegram.helpers import escape_markdown
import paramiko
from scp import SCPClient
import sys
import subprocess
import threading
from pathlib import Path
import re

def escape_markdown(text: str, version: int = 1) -> str:
    if version == 2:
        escape_chars = r'\_*[]()~`>#+-=|{}.!'
    else:
        escape_chars = r'\_*[]()'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)



# Suppress HTTP request logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Bot management system
BOT_INSTANCES = {}  # Stores running bot processes
BOT_CONFIG_FILE = "bot_configs.json"
BOT_DATA_DIR = "bot_data"  # Directory to store each bot's data

# Bot Configuration
TELEGRAM_BOT_TOKEN = '7052787265:AAHF9957hIRSGZtaENdHZAA_9Cx0iROS9k0'
OWNER_ID = 6882674372  # 👈 Put your real Telegram user ID here
CO_OWNERS = []  # List of user IDs for co-owners
OWNER_CONTACT = "Contact to buy keys"
ALLOWED_GROUP_IDS = [-1002569945697,-1002267337768]
MAX_THREADS = 1000
max_duration = 120
bot_open = False
OWNER_USERNAME = "LASTWISHES0"
SPECIAL_MAX_DURATION = 600
SPECIAL_MAX_THREADS = 2000
BOT_START_TIME = time.time()

ACTIVE_VPS_COUNT = 10000  # डिफॉल्ट रूप से 6 VPS इस्तेमाल होंगे
# Display Name Configuration
GROUP_DISPLAY_NAMES = {}  # Key: group_id, Value: display_name
DISPLAY_NAME_FILE = "display_names.json"

# Link Management
LINK_FILE = "links.json"
LINKS = {}

# VPS Configuration
VPS_FILE = "vps.txt"
BINARY_NAME = "Veno"
BINARY_PATH = f"/home/master/{BINARY_NAME}"
VPS_LIST = []

# Key Prices
KEY_PRICES = {
    "1H": 5,
    "2H": 10,  # Price for 1-hour key
    "3H": 15,  # Price for 1-hour key
    "4H": 20,  # Price for 1-hour key
    "5H": 25,  # Price for 1-hour key
    "6H": 30,  # Price for 1-hour key
    "7H": 35,  # Price for 1-hour key
    "8H": 40,  # Price for 1-hour key
    "9H": 45,  # Price for 1-hour key
    "10H": 50, # Price for 1-hour key
    "1D": 60,  # Price for 1-day key
    "2D": 100,  # Price for 1-day key
    "3D": 160, # Price for 1-day key
    "5D": 250, # Price for 2-day key
    "7D": 320, # Price for 2-day key
    "15D": 700, # Price for 2-day key
    "30D": 1250, # Price for 2-day key
    "60D": 2000, # Price for 2-day key,
}

# Special Key Prices
SPECIAL_KEY_PRICES = {
    "1D": 70,  
    "2D": 130,  # 30 days special key price
    "3D": 250,  # 30 days special key price
    "4D": 300,  # 30 days special key price
    "5D": 400,  # 30 days special key price
    "6D": 500,  # 30 days special key price
    "7D": 550,  # 30 days special key price
    "8D": 600,  # 30 days special key price
    "9D": 750,  # 30 days special key price
    "10D": 800,  # 30 days special key price
    "11D": 850,  # 30 days special key price
    "12D": 900,  # 30 days special key price
    "13D": 950,  # 30 days special key price
    "14D": 1000,  # 30 days special key price
    "15D": 1050,  # 30 days special key price
    "30D": 1500,  # 30 days special key price
}

# Image configuration
START_IMAGES = [
    {
        'url': 'https://files.catbox.moe/0s0dn0.png',
        'caption': (
            '🔥 *Welcome to the Ultimate DDoS Bot !*' + '\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 100`' + '\n\n'
            '💀 *Bsdk threads ha 100 dalo time 120 dalne ke baad*' + '\n\n'
            '⚠️ *🥰🥰🥰🥰🥰🥰🥰🥰🥰🥰🤬*⚠️' + '\n\n'
            '⚠️ *JOIN CHANNEL  @NXTLVLPUBLIC *' + '\n\n'
        )
    },
    
]

# File to store key data
KEY_FILE = "keys.txt"

# Key System
keys = {}
special_keys = {}
redeemed_users = {}
redeemed_keys_info = {}
feedback_waiting = {}

# Reseller System
resellers = set()
reseller_balances = {}

# Global Cooldown
global_cooldown = 0
last_attack_time = 0

# Track running attacks
running_attacks = {}

# Keyboards
group_user_keyboard = [
    ['/Start', 'Attack'],
    ['Redeem Key', 'Rules'],
    ['🔍 Status', '⏳ Uptime']
]
group_user_markup = ReplyKeyboardMarkup(group_user_keyboard, resize_keyboard=True)

reseller_keyboard = [
    ['/Start', 'Attack', 'Redeem Key'],
    ['Rules', 'Balance', 'Generate Key'],
    ['🔑 Special Key', 'Keys', '⏳ Uptime']
]
reseller_markup = ReplyKeyboardMarkup(reseller_keyboard, resize_keyboard=True)

# Settings menu keyboard with Reset VPS button
settings_keyboard = [
    ['Set Duration', 'Add Reseller'],
    ['Remove Reseller', 'Set Threads'],
    ['Add Coin', 'Set Cooldown'],
    ['Reset VPS', 'Back to Home']
]
settings_markup = ReplyKeyboardMarkup(settings_keyboard, resize_keyboard=True)

# Owner Settings menu keyboard with bot management buttons
owner_settings_keyboard = [
    ['Add Bot', 'Remove Bot'],
    ['Bot List', 'Start Selected Bot'],
    ['Stop Selected Bot', 'Promote'],
    ['🔗 Manage Links', '📢 Broadcast'],
    ['Back to Home']
]
owner_settings_markup = ReplyKeyboardMarkup(owner_settings_keyboard, resize_keyboard=True)

owner_keyboard = [
    ['/Start', 'Attack', 'Redeem Key'],
    ['Rules', 'Settings', 'Generate Key'],
    ['Delete Key', '🔑 Special Key', '⏳ Uptime'],
    ['OpenBot', 'CloseBot', 'Menu'],
    ['⚙️ Owner Settings', '👥 Check Users']
]
owner_markup = ReplyKeyboardMarkup(owner_keyboard, resize_keyboard=True)

co_owner_keyboard = [
    ['/Start', 'Attack', 'Redeem Key'],
    ['Rules', 'Delete Key', 'Generate Key'],
    ['OpenBot', '🔑 Special Key', 'CloseBot'],
    ['Settings', '⏳ Uptime', 'Menu']
]
co_owner_markup = ReplyKeyboardMarkup(co_owner_keyboard, resize_keyboard=True)

# Menu keyboards
owner_menu_keyboard = [
    ['Add Group ID', 'Remove Group ID'],
    ['RE Status', 'VPS Status'],
    ['Add VPS', 'Remove VPS'],
    ['Add Co-Owner', 'Remove Co-Owner'],
    ['Set Display Name', 'Upload Binary'],
    ['Delete Binary', 'Back to Home']  # Added Delete Binary button
]
owner_menu_markup = ReplyKeyboardMarkup(owner_menu_keyboard, resize_keyboard=True)

co_owner_menu_keyboard = [
    ['Add Group ID', 'Remove Group ID'],
    ['RE Status', 'VPS Status'],
    ['Set Display Name', 'Add VPS'],
    ['Back to Home', 'Upload Binary']
]
co_owner_menu_markup = ReplyKeyboardMarkup(co_owner_menu_keyboard, resize_keyboard=True)

# Conversation States
GET_DURATION = 1
GET_KEY = 2
GET_ATTACK_ARGS = 3
GET_SET_DURATION = 4
GET_SET_THREADS = 5
GET_DELETE_KEY = 6
GET_RESELLER_ID = 7
GET_REMOVE_RESELLER_ID = 8
GET_ADD_COIN_USER_ID = 9
GET_ADD_COIN_AMOUNT = 10
GET_SET_COOLDOWN = 11
GET_SPECIAL_KEY_DURATION = 12
GET_SPECIAL_KEY_FORMAT = 13
ADD_GROUP_ID = 14
REMOVE_GROUP_ID = 15
MENU_SELECTION = 16
GET_RESELLER_INFO = 17
GET_VPS_INFO = 18
GET_VPS_TO_REMOVE = 19
CONFIRM_BINARY_UPLOAD = 20
GET_ADD_CO_OWNER_ID = 21
GET_REMOVE_CO_OWNER_ID = 22
GET_DISPLAY_NAME = 23
GET_GROUP_FOR_DISPLAY_NAME = 24
GET_BOT_TOKEN = 25
GET_OWNER_USERNAME = 26
SELECT_BOT_TO_START = 27
SELECT_BOT_TO_STOP = 28
CONFIRM_BINARY_DELETE = 29
GET_LINK_NUMBER = 30
GET_LINK_URL = 31
GET_BROADCAST_MESSAGE = 31
GET_VPS_COUNT = 32

def get_uptime():
    uptime_seconds = int(time.time() - BOT_START_TIME)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def get_display_name(group_id=None):
    """Returns the current display name for the owner in specific group or default"""
    if group_id is None:
        return GROUP_DISPLAY_NAMES.get('default', f"@{OWNER_USERNAME}")
    return GROUP_DISPLAY_NAMES.get(group_id, GROUP_DISPLAY_NAMES.get('default', f"@{OWNER_USERNAME}"))

async def owner_settings(update: Update, context: CallbackContext):
    if not is_owner(update):
        await update.message.reply_text("❌ *Only the owner can access these settings!*", parse_mode='Markdown')
        return
    
    # Make sure current_display_name is defined here or before this
    current_display_name = get_display_name_from_update(update)
    
    escaped_display_name = escape_markdown(current_display_name)
    
    await update.message.reply_text(
        f"⚙️ *Owner Settings Menu*\n\n"
        f"Select an option below:\n\n"
        f"👑 *Bot Owner:* {escaped_display_name}",
        parse_mode='Markdown',
        reply_markup=owner_settings_markup
    )



async def set_display_name(update: Update, new_name: str, group_id=None):
    """Updates the display name for specific group or default"""
    if group_id is not None:
        GROUP_DISPLAY_NAMES[group_id] = new_name
    else:
        GROUP_DISPLAY_NAMES['default'] = new_name
    
    with open(DISPLAY_NAME_FILE, 'w') as f:
        json.dump(GROUP_DISPLAY_NAMES, f)
    
    if update:
        await update.message.reply_text(
            f"✅ Display name updated to: {new_name}" + 
            (f" for group {group_id}" if group_id else " as default name"),
            parse_mode='Markdown'
        )

def load_vps():
    global VPS_LIST
    VPS_LIST = []
    if os.path.exists(VPS_FILE):
        with open(VPS_FILE, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line and len(line.split(',')) == 3:  # IP,username,password फॉर्मेट चेक करें
                    VPS_LIST.append(line.split(','))

async def set_vps_count(update: Update, context: CallbackContext):
    if not (is_owner(update) or is_co_owner(update)):
        await update.message.reply_text("❌ Only owner or co-owners can set VPS count!", parse_mode='Markdown')
        return ConversationHandler.END
    
    await update.message.reply_text(
        f"⚠️ Enter number of VP
