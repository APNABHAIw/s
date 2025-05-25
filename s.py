import os
import time
import logging
import asyncio
import random
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler
from telegram.helpers import escape_markdown
import paramiko
from scp import SCPClient

# Suppress HTTP request logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Bot Configuration
TELEGRAM_BOT_TOKEN = '7673615517:AAHC_RCOOM-1pCUmvP2Bqm83-V9aA2XFhW8'
OWNER_USERNAME = "LASTWISHES0"
CO_OWNERS = []  # List of user IDs for co-owners
OWNER_CONTACT = "Contact @LASTWISHES0 to buy keys"
ALLOWED_GROUP_IDS = [-1002569945697]
MAX_THREADS = 1200
max_duration = 120
bot_open = False
SPECIAL_MAX_DURATION = 600
SPECIAL_MAX_THREADS = 1200
BOT_START_TIME = time.time()

# Display Name Configuration
GROUP_DISPLAY_NAMES = {}  # Key: group_id, Value: display_name
DISPLAY_NAME_FILE = "display_names.json"

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
        'url': 'https://i.postimg.cc/y87JxR3H/IMG-20250513-193708.jpg',
        'caption':(
            '🔥 *Welcome to the Ultimate DDoS Bot!*\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 1200`\n\n'
            '💀 *Bsdk threads ha 1200 dalo time 120 dalne ke baad* 💀\n\n'
            '🔑 *KYA GUNDA BANEGA RE TU😂*\n\n'
            '⚠️ *KYA BOLTI TU*⚠️\n\n'
            '⚠️ *DM FOR BUY KEY - @LASTWISHES0*\n\n'
            
        )
    },
    {
        'url': 'https://www.craiyon.com/image/KC4CfJPuQTuKdSdlrkiczg',
        'caption':(
            '🔥 *Welcome to the Ultimate DDoS Bot!*\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 100`\n\n'
            '💀 *Bsdk threads ha 100 dalo time 120 dalne ke baad* 💀\n\n'
            '🔑 *KYA GUNDA BANEGARE TUI*\n\n'
            '⚠️ *KABI PAID BI LELE BOSDK❤️*⚠️\n\n'
            '⚠️ *DM FOR BUY KEY - @LASTWISHES0*\n\n'
        )
    },
    {
        'url': 'https://www.craiyon.com/image/A3ol0NRAQc2N3C62DXcfpA',
        'caption': (
            '🔥 *Welcome to the Ultimate DDoS Bot!*\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 1200`\n\n'
            '💀 *Bsdk threads ha 1200 dalo time 120 dalne ke baad* 💀\n\n'
            '🔑 *KYA GUNDA BANEGA RE TU🤣*\n\n'
            '⚠️ *JALDI MAARO ATTACK  ❤️*⚠️\n\n'
            '⚠️ *DM FOR BUY KEY - @LASTWISHES0*\n\n'
        )
    },
    {
        'url': 'https://www.craiyon.com/image/IErJnUlDTkCvcWBeTZX8qQ',
        'caption': (
            '🔥 *Welcome to the Ultimate DDoS Bot!*\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 1200`\n\n'
            '💀 *Bsdk threads ha 1200 dalo time 120 dalne ke baad* 💀\n\n'
            '🔑 *KYA GUNDA BANEGA RE TU😂*\n\n'
            '⚠️ *YEE KYA BAK RAHE HO MADARCHOD*⚠️\n\n'
            '⚠️ *DM FOR BUY KEY - @LASTWISHES0*\n\n'
        )
    },
    {
        'url': 'https://www.craiyon.com/image/073Vnr7jQpGUkSMr6Rrvjw',
        'caption': (
            '🔥 *Welcome to the Ultimate DDoS Bot!*\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 100`\n\n'
            '💀 *Bsdk threads ha 100 dalo time 120 dalne ke baad* 💀\n\n'
            '🔑 *KYA GUNDA BANEGA RE TU 😂*\n\n'
            '⚠️ *MOST WELCOME PAID ENTRY ❤️😊*⚠️\n\n'
            '⚠️ *DM FOR BUY KEY - @LASTWISHES0*\n\n'
        )
    },
    {
        'url': 'https://www.craiyon.com/image/XgSNsdopTYGnlDsVC4PnSw',
        'caption': (
            '🔥 *Welcome to the Ultimate DDoS Bot!*\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 100`\n\n'
            '💀 *Bsdk threads ha 100 dalo time 120 dalne ke baad* 💀\n\n'
            '🔑 *KYA GUNDA BANEGA RE TU🤣*\n\n'
            '⚠️ *MOST WELCOME PAID GROUP ❤️😊*⚠️\n\n'
            '⚠️ *DM FOR BUY KEY - @LASTWISHES0*\n\n'
        )
    },
    {
        'url': 'https://www.craiyon.com/image/JbBsmO9RQcy2CKQiOf_MOw',
        'caption': (
            '🔥 *Welcome to the Ultimate DDoS Bot!*\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 100`\n\n'
            '💀 *Bsdk threads ha 100 dalo time 120 dalne ke baad* 💀\n\n'
            '🔑 *Ritik ki ma chodne wala @Riyahacksyt*\n\n'
            '⚠️ *4 LOGO NE MILKE BGMI KI MUMMY KA KIYA RAPE OR CHUT PHAAD DI*⚠️\n\n'
            '⚠️ *DM FOR BUY KEY - @LASTWISHES0 🤬*\n\n'
        )
    },
    {
        'url': 'https://www.craiyon.com/image/yF1wqEx7TuuAfoBLK0Zmag',
        'caption': (
            '🔥 *Welcome to the Ultimate DDoS Bot!*\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 100`\n\n'
            '💀 *Bsdk threads ha 100 dalo time 120 dalne ke baad* 💀\n\n'
            '🔑 *KYA GUNDA BANEGA RE TU😂*\n\n'
            '⚠️ *WELCOME TO BEST PAID DDOS ❤️😊*⚠️\n\n'
            '⚠️ *DM FOR BUY KEY - @LASTWISHES0*\n\n'
        )
    },
    {
        'url': 'https://www.craiyon.com/image/XuS2HNGdTFKqGkpAGzzrqg',
        'caption': (
            '🔥 *Welcome to the Ultimate DDoS Bot!*\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 100`\n\n'
            '💀 *Bsdk threads ha 100 dalo time 120 dalne ke baad* 💀\n\n'
            '🔑 *KYA GUNDA BANEGA RE TU😂*\n\n'
            '⚠️ *ALONE MY BEST FRIENDS ❤️😘*⚠️\n\n'
            '⚠️ *DM FOR BUY KEY - @LASTWISHES0*\n\n'
        )
    },
    {
        'url': 'https://www.craiyon.com/image/iRyN9awaQIeFgjqVVucIlA',
        'caption': (
            '🔥 *Welcome to the Ultimate DDoS Bot!*\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 100`\n\n'
            '💀 *Bsdk threads ha 100 dalo time 120 dalne ke baad* 💀\n\n'
            '🔑 *KYA GUNDA BANEGA RE TU😂*\n\n'
            '⚠️ *LATEST NEWS⚠️ BGMI CHUDEGA BHAI HAI *⚠️\n\n'
            '⚠️ *DM FOR BUY KEY - @LASTWISHES0*\n\n'
        )
    },
    {
        'url': 'https://www.craiyon.com/image/bAhq_xScRm-wk-hD9GzUrw',
        'caption': (
            '🔥 *Welcome to the Ultimate DDoS Bot!*\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 100`\n\n'
            '💀 *Bsdk threads ha 100 dalo time 120 dalne ke baad* 💀\n\n'
            '🔑 *KYA GUNDA BANEGA RE TU😂*\n\n'
            '⚠️ *LATEST NEWS⚠️ RITIK DEMON RIYAAZ BHAI HAI*⚠️\n\n'
            '⚠️ *DM FOR BUY KEY - @LASTWISHES0*\n\n'
       )
    },
    {
        'url': 'https://mobilehd.blob.core.windows.net/main/2017/02/girl-sexy-black-swimsuit-look-1080x1920.jpg',
        'caption':(
            '🔥 *Welcome to the Ultimate DDoS Bot!*\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 100`\n\n'
            '💀 *Bsdk threads ha 100 dalo time 120 dalne ke baad* 💀\n\n'
            '🔑 *KYA GUNDA BANEGA RE TU😂*\n\n'
            '⚠️ *MY BEST FRIENDS ME ME ME ME MAFIA *⚠️\n\n'
            '⚠️ *DM FOR BUY KEY - @LASTWISHES0*\n\n'
        )
    },
    {
        'url': 'https://s2.best-wallpaper.net/wallpaper/iphone/2007/Beautiful-long-hair-girl-look-sunshine-summer_iphone_640x1136.jpg',
        'caption':(
            '🔥 *Welcome to the Ultimate DDoS Bot!*\n\n'
            '💻 *Example:* `20.235.43.9 14533 120 100`\n\n'
            '💀 *Bsdk threads ha 100 dalo time 120 dalne ke baad* 💀\n\n'
            '🔑 *KYA GUNDA BANEGA RE TU😂*\n\n'
            '⚠️ *MY BEST FRIENDS MAFIA SOURAV YASH HAVK*⚠️\n\n'
            '⚠️ *DM FOR BUY KEY - @LASTWISHES0*\n\n'
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
    ['Start', 'Attack'],
    ['Redeem Key', 'Rules'],
    ['🔍 Status', '⏳ Uptime']
]
group_user_markup = ReplyKeyboardMarkup(group_user_keyboard, resize_keyboard=True)

reseller_keyboard = [
    ['Start', 'Attack', 'Redeem Key'],
    ['Rules', 'Balance', 'Generate Key'],
    ['🔑 Special Key', 'Keys', '⏳ Uptime']
]
reseller_markup = ReplyKeyboardMarkup(reseller_keyboard, resize_keyboard=True)

owner_keyboard = [
    ['Start', 'Attack', 'Redeem Key'],
    ['Rules', 'Set Duration', 'Set Threads'],
    ['Generate Key', 'Keys', 'Delete Key'],
    ['Add Reseller', 'Remove Reseller', 'Add Coin'],
    ['Set Cooldown', 'OpenBot', 'CloseBot'],
    ['🔑 Special Key', 'Menu', '⏳ Uptime']
]
owner_markup = ReplyKeyboardMarkup(owner_keyboard, resize_keyboard
