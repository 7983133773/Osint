# =====================================================================
# 🚀 AYUSH OSINT BOT - PROFESSIONAL INTELLIGENCE CORE
# Developer: @GOD_AYUSH
# =====================================================================

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os
import asyncio
import time
import datetime
import random
import string
import logging
import json
import io
from html import escape as html_escape
from pathlib import Path
import aiohttp

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InputFile
)

BOT_PAUSED = False
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.error import TelegramError, NetworkError, InvalidToken

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("AYUSH_OSINT")

BASE_DIR = Path(__file__).resolve().parent

def load_dotenv_simple(path=BASE_DIR / ".env"):
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("\"'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception as e:
        logger.warning(f"Could not read .env: {e}")

load_dotenv_simple()

BOT_TOKEN = os.getenv("BOT_TOKEN", "9258364674:AAHNEj83g5M3Cmgdhmn8KzKuLRS5YEwGQGk").strip()
BRAND_NAME = "AYUSH-OSINT"
OWNER_NAME = "AYUSH"
OWNER_USERNAME = "GOD_AYUSH"
MAIN_OWNER = 7758917200
ADMIN_IDS = [7758917200]
MAIN_CHANNEL = "Ayush_Hackz"
OFFICIAL_GROUP = "AYUSHxOSINT"
BOT_USERNAME = os.getenv("BOT_USERNAME", "AyushOsint_Robot").strip().lstrip("@")

FORCE_JOIN_CHANNELS = ["Ayush_Hackz", "Ayush_Cyber_Updates", "AYUSHxOSINT"]

DATA_FILE = BASE_DIR / "bot_data.json"
API_CONFIG_FILE = BASE_DIR / "api_config.json"
START_IMAGE_PATH = BASE_DIR / "assets" / "start.jpg"
START_VIDEO_PATH = BASE_DIR / "assets" / "start_video.mp4"

# ==================== PROVIDED OSINT APIs ONLY ====================
API_BASE = "https://shuruuu-api.vercel.app"
AYUSH_KEY = "AYUSH$PRO"

PROVIDED_APIS = {
    "vehicle":    {"url": f"{API_BASE}/vehicle_info?key={AYUSH_KEY}&query={{arg}}",    "label": "🚗 Vehicle Info", "input_hint": "Vehicle number (e.g. MH12AB1234)", "icon": "🚗"},
    "aadhar":     {"url": f"{API_BASE}/aadhar_info?key={AYUSH_KEY}&query={{arg}}",     "label": "🪪 Aadhaar Info", "input_hint": "12-digit Aadhaar number", "icon": "🪪"},
    "family":     {"url": f"{API_BASE}/family_info?key={AYUSH_KEY}&query={{arg}}",     "label": "👨‍👩‍👧 Family Info", "input_hint": "Aadhaar number", "icon": "👨‍👩‍👧"},
    "lpg":        {"url": f"{API_BASE}/lpg_info?key={AYUSH_KEY}&query={{arg}}",        "label": "🔥 LPG Info", "input_hint": "LPG consumer number", "icon": "🔥"},
    "pak":        {"url": f"{API_BASE}/pak_info?key={AYUSH_KEY}&query={{arg}}",        "label": "🇵🇰 Pakistan SIM Info", "input_hint": "Pakistan phone number", "icon": "🇵🇰"},
    "pan":        {"url": f"{API_BASE}/pan_osint?key={AYUSH_KEY}&query={{arg}}",       "label": "📄 PAN Card Lookup", "input_hint": "PAN number (e.g. ABCDE1234F)", "icon": "📄"},
    "truecaller": {"url": f"{API_BASE}/truecaller_info?key={AYUSH_KEY}&query={{arg}}", "label": "📞 Truecaller Trace", "input_hint": "10-digit mobile number", "icon": "📞"},
    "num":        {"url": "https://shuruuu-api.vercel.app/num_info?key=@KINGFFAIAK47x&query={arg}", "label": "📱 Phone Number Info", "input_hint": "10-digit phone number", "icon": "📱"},
}

OSINT_CATEGORIES = {
    "identity": {
        "title": "📱 IDENTITY INTELLIGENCE",
        "modules": [("num", "📱 Phone Number Info"), ("truecaller", "📞 Truecaller Trace")]
    },
    "vehicle": {
        "title": "🚘 VEHICLE INTELLIGENCE",
        "modules": [("vehicle", "🚗 Vehicle Info")]
    },
    "profile": {
        "title": "🪪 PROFILE & RECORDS",
        "modules": [("aadhar", "🪪 Aadhaar Info"), ("family", "👨‍👩‍👧 Family Info"), ("pan", "📄 PAN Card Lookup")]
    },
    "utility": {
        "title": "💳 UTILITIES & FINANCIAL",
        "modules": [("lpg", "🔥 LPG Info"), ("pak", "🇵🇰 Pakistan SIM Info")]
    }
}

MODULE_NAMES = {}
for cat in OSINT_CATEGORIES.values():
    for m_cmd, m_label in cat["modules"]:
        MODULE_NAMES[m_cmd] = m_label


class OsintData:
    def __init__(self):
        self.data = {
            "users": {},
            "private_whitelist": [MAIN_OWNER],
            "admins": [MAIN_OWNER],
            "redeem_codes": {},
            "plans": [
                {"name": "Starter", "price": "49", "credits": 5000},
                {"name": "Ultra", "price": "99", "credits": 25000},
                {"name": "VIP Unlimited", "price": "199", "credits": 100000}
            ],
            "stats": {"total_lookups": 0}
        }
        self.load()

    def load(self):
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    for k, v in d.items():
                        self.data[k] = v
                    if MAIN_OWNER not in self.data.get("private_whitelist", []):
                        self.data.setdefault("private_whitelist", []).append(MAIN_OWNER)
                    if MAIN_OWNER not in self.data.get("admins", []):
                        self.data.setdefault("admins", []).append(MAIN_OWNER)
            except Exception as e:
                logger.error(f"Error loading bot_data: {e}")

    def save(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving bot_data: {e}")

    def is_admin(self, uid: int) -> bool:
        if uid == MAIN_OWNER or uid in ADMIN_IDS:
            return True
        return uid in self.data.get("admins", [])

    def is_free_tier(self, uid: int) -> bool:
        if self.is_admin(uid):
            return True
        return uid in self.data.get("private_whitelist", [])

    def is_private_allowed(self, uid: int) -> bool:
        return self.is_free_tier(uid)

    def get_user(self, uid: int, name: str = "User", uname: str = ""):
        k = str(uid)
        today_str = datetime.date.today().isoformat()
        if k not in self.data["users"]:
            self.data["users"][k] = {
                "name": name, "username": uname,
                "credits": 999999999 if self.is_free_tier(uid) else 50,
                "last_daily_bonus": today_str,
                "total_lookups": 0,
                "refer_code": "AYUSH" + str(uid)[-5:],
                "referred_by": None, "referrals": 0,
                "joined_at": int(time.time())
            }
            self.save()
            return self.data["users"][k]

        u = self.data["users"][k]
        u["name"] = name
        if uname:
            u["username"] = uname

        if self.is_free_tier(uid):
            u["credits"] = 999999999

        if u.get("last_daily_bonus") != today_str and not self.is_free_tier(uid):
            u["credits"] = u.get("credits", 0) + 50
            u["last_daily_bonus"] = today_str
            self.save()

        return u


db = OsintData()
VIDEO_FILE_ID = None
_HTTP_SESSION = None


async def get_http_session():
    global _HTTP_SESSION
    if _HTTP_SESSION is None or _HTTP_SESSION.closed:
        connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=600, force_close=True)
        _HTTP_SESSION = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=15, connect=8)
        )
    return _HTTP_SESSION


# ==================== FORCE JOIN ====================

async def check_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if db.is_admin(user.id):
        return True

    missing = []
    for ch in FORCE_JOIN_CHANNELS:
        try:
            member = await context.bot.get_chat_member(f"@{ch}", user.id)
            if member.status not in ["member", "administrator", "creator"]:
                missing.append(ch)
        except Exception:
            missing.append(ch)

    if not missing:
        return True

    kb = []
    for ch in missing:
        kb.append([InlineKeyboardButton(f"📢 Join @{ch}", url=f"https://t.me/{ch}")])
    kb.append([InlineKeyboardButton("✅ I've Joined — Verify", callback_data="check_joined")])

    msg = update.message if update.message else (update.callback_query.message if update.callback_query else None)
    if msg:
        try:
            await msg.reply_text(
                f"⚠️ <b>CHANNEL JOIN REQUIRED!</b>\n\n"
                f"Bot use karne ke liye pehle in channels ko join karo:\n\n"
                + "\n".join([f"• @{ch}" for ch in missing]) +
                f"\n\nJoin karne ke baad '✅ I've Joined — Verify' tap karo.",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
        except Exception:
            pass
    return False


async def reply_with_video(message, text: str, reply_markup=None, parse_mode="HTML"):
    global VIDEO_FILE_ID
    try:
        if VIDEO_FILE_ID:
            await message.reply_video(video=VIDEO_FILE_ID)
        elif START_VIDEO_PATH.exists():
            with open(START_VIDEO_PATH, "rb") as vf:
                vid_msg = await message.reply_video(video=vf)
                if vid_msg and vid_msg.video:
                    VIDEO_FILE_ID = vid_msg.video.file_id
    except Exception as e:
        logger.warning(f"Video send failed: {e}")
    return await message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)


# ==================== COLORFUL KEYBOARDS ====================
def main_reply_keyboard():
    kb = [
        [KeyboardButton("📱 NUM INFO"), KeyboardButton("📞 TRUECALLER")],
        [KeyboardButton("🚗 VEHICLE"), KeyboardButton("🪪 AADHAR")],
        [KeyboardButton("👨‍👩‍👧 FAMILY"), KeyboardButton("📄 PAN")],
        [KeyboardButton("🔥 LPG INFO"), KeyboardButton("🇵🇰 PAK SIM")],
        [KeyboardButton("💵 MY CREDITS"), KeyboardButton("🎁 DAILY BONUS")],
        [KeyboardButton("📊 MY STATS"), KeyboardButton("❓ HELP")],
        [KeyboardButton("🎟️ REDEEM CODE"), KeyboardButton("🔗 REFERRAL")],
        [KeyboardButton("💲 BUY CREDITS"), KeyboardButton("🔴 ADMIN PANEL")],
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)


def osint_matrix_keyboard():
    kb = [
        [InlineKeyboardButton("📱 IDENTITY", callback_data="osint_cat_identity"),
         InlineKeyboardButton("🚘 VEHICLE", callback_data="osint_cat_vehicle")],
        [InlineKeyboardButton("🪪 PROFILE", callback_data="osint_cat_profile"),
         InlineKeyboardButton("💳 UTILITIES", callback_data="osint_cat_utility")],
        [InlineKeyboardButton("👑 OWNER", url=f"https://t.me/{OWNER_USERNAME}"),
         InlineKeyboardButton("➕ ADD TO GROUP", url=f"https://t.me/{BOT_USERNAME}?startgroup=start")]
    ]
    return InlineKeyboardMarkup(kb)


def admin_apis_keyboard(page: int = 0):
    apis = {}
    if API_CONFIG_FILE.exists():
        try:
            with open(API_CONFIG_FILE, "r", encoding="utf-8") as f:
                apis = json.load(f)
        except Exception:
            pass
    if not apis:
        apis = {k: v["url"] for k, v in PROVIDED_APIS.items()}

    items = list(apis.items())
    per_page = 8
    total_pages = max(1, (len(items) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    start_i = page * per_page
    end_i = min(start_i + per_page, len(items))

    kb = []
    for cmd, url in items[start_i:end_i]:
        kb.append([InlineKeyboardButton(f"⚙️ /{cmd}", callback_data=f"adm_api_view_{cmd}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"adm_api_page_{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"adm_api_page_{page+1}"))
    if nav:
        kb.append(nav)

    kb.append([InlineKeyboardButton("➕ Add New API Endpoint", callback_data="adm_api_add_new")])
    kb.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="adm_back_main")])
    return InlineKeyboardMarkup(kb), len(items), page + 1, total_pages


# ==================== DATABASE EXPORT ====================

async def export_database(message, user_id: int, silent=False):
    """Export all database files as .json documents. Admin/Owner only."""
    if not (user_id == MAIN_OWNER or user_id in ADMIN_IDS or user_id in db.data.get("admins", [])):
        if not silent:
            await message.reply_text("❌ Access Denied! Admin/Owner only.")
        return

    status = None
    if not silent:
        status = await message.reply_text("📦 <b>Preparing database export...</b>", parse_mode="HTML")

    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = []

        # 1. bot_data.json
        if DATA_FILE.exists():
            try:
                # Save latest state before exporting
                db.save()
                with open(DATA_FILE, "rb") as f:
                    content = f.read()
                await message.reply_document(
                    document=InputFile(io.BytesIO(content), filename=f"bot_data_{timestamp}.json"),
                    caption=f"📊 <b>bot_data.json</b>\n\n"
                            f"👥 Users: {len(db.data.get('users', {}))}\n"
                            f"🔒 Whitelist: {len(db.data.get('private_whitelist', []))}\n"
                            f"👑 Admins: {len(db.data.get('admins', []))}\n"
                            f"🎟️ Redeem Codes: {len(db.data.get('redeem_codes', {}))}\n"
                            f"🔍 Total Lookups: {db.data.get('stats', {}).get('total_lookups', 0)}\n"
                            f"⏰ {timestamp}",
                    parse_mode="HTML"
                )
                exported_files.append("bot_data.json")
            except Exception as e:
                logger.error(f"Export bot_data error: {e}")
                if not silent:
                    await message.reply_text(f"❌ Failed to export bot_data.json: {e}")

        # 2. api_config.json
        if API_CONFIG_FILE.exists():
            try:
                with open(API_CONFIG_FILE, "rb") as f:
                    content = f.read()
                await message.reply_document(
                    document=InputFile(io.BytesIO(content), filename=f"api_config_{timestamp}.json"),
                    caption=f"🌐 <b>api_config.json</b>\n\n⏰ {timestamp}",
                    parse_mode="HTML"
                )
                exported_files.append("api_config.json")
            except Exception as e:
                logger.error(f"Export api_config error: {e}")

        # 3. .env (sensitive - only MAIN_OWNER)
        if user_id == MAIN_OWNER:
            env_path = BASE_DIR / ".env"
            if env_path.exists():
                try:
                    with open(env_path, "rb") as f:
                        content = f.read()
                    await message.reply_document(
                        document=InputFile(io.BytesIO(content), filename=f"env_{timestamp}.txt"),
                        caption=f"🔐 <b>.env file (SENSITIVE)</b>\n\n⚠️ Store securely!\n⏰ {timestamp}",
                        parse_mode="HTML"
                    )
                    exported_files.append(".env")
                except Exception as e:
                    logger.error(f"Export .env error: {e}")

        summary = (
            f"✅ <b>DATABASE EXPORT COMPLETE!</b>\n\n"
            f"📦 Files exported: <b>{len(exported_files)}</b>\n"
            + "\n".join([f"• <code>{f}</code>" for f in exported_files]) +
            f"\n\n👥 Users: <b>{len(db.data.get('users', {}))}</b>\n"
            f"🔍 Total Lookups: <b>{db.data.get('stats', {}).get('total_lookups', 0)}</b>\n"
            f"⏰ Timestamp: <code>{timestamp}</code>\n\n"
            f"<i>Store these files securely — they contain user data!</i>"
        )

        if status:
            try:
                await status.edit_text(summary, parse_mode="HTML")
            except Exception:
                await message.reply_text(summary, parse_mode="HTML")
        elif not silent:
            await message.reply_text(summary, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Export database error: {e}")
        if status:
            try:
                await status.edit_text(f"❌ Export failed: {e}", parse_mode="HTML")
            except Exception:
                pass
        elif not silent:
            await message.reply_text(f"❌ Export failed: {e}")


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Standalone /export command for admins."""
    user = update.effective_user
    await export_database(update.message, user.id, silent=False)


# ==================== HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if not await check_force_join(update, context):
        return

    u = db.get_user(user.id, user.first_name, user.username)

    if context.args and len(context.args) > 0:
        arg = context.args[0]
        if arg.startswith("REF") and not u.get("referred_by"):
            for uid_s, ud in db.data["users"].items():
                if ud.get("refer_code") == arg and uid_s != str(user.id):
                    u["referred_by"] = uid_s
                    ud["credits"] = ud.get("credits", 0) + 100
                    ud["referrals"] = ud.get("referrals", 0) + 1
                    u["credits"] = u.get("credits", 0) + 100
                    db.save()
                    try:
                        await context.bot.send_message(
                            int(uid_s),
                            f"🎉 <b>New Referral!</b>\nUser {user.first_name} joined using your link!\n+100 Credits added!",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass
                    break

    if chat.type == "private" and not db.is_private_allowed(user.id):
        text = (
            f"🔒 <b>PRIVATE ACCESS RESTRICTED!</b>\n\n"
            f"Hey <b>{html_escape(user.first_name)}</b>,\n"
            f"This bot can only be used inside groups, OR if owner has added your Chat ID.\n\n"
            f"🆔 <b>Your Chat ID:</b> <code>{user.id}</code>\n\n"
            f"👉 <i>Send your Chat ID to @{OWNER_USERNAME} to unlock personal use!</i>\n"
            f"👉 <i>Or use in official group below:</i>"
        )
        kb = [
            [InlineKeyboardButton("📢 Official Group", url=f"https://t.me/{OFFICIAL_GROUP}")],
            [InlineKeyboardButton("👑 Contact Owner", url=f"https://t.me/{OWNER_USERNAME}")]
        ]
        await reply_with_video(update.message, text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
        return

    credit_str = "👑 UNLIMITED" if db.is_free_tier(user.id) else str(u.get('credits', 0))
    caption = (
        f"╭━━━━━ ◈ <b>{BRAND_NAME}</b> ◈ ━━━━━╮\n"
        f"        <b>PROFESSIONAL INTELLIGENCE CORE</b>\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"👋 Welcome <b>{html_escape(user.first_name)}</b>!\n"
        f"💰 <b>Your AYUSH Credits:</b> <code>{credit_str}</code>\n"
        f"🎁 <b>Daily Bonus:</b> +50 AYUSH everyday\n"
        f"🔍 <b>8 Professional OSINT Modules Ready</b>\n"
        f"⚡ <b>Vehicle • Aadhaar • PAN • Family • Truecaller • LPG • Pak SIM • Phone</b>\n\n"
        f"<i>Use buttons below or /help for all commands.</i>"
    )

    sent = False
    if START_VIDEO_PATH.exists():
        try:
            with open(START_VIDEO_PATH, "rb") as video:
                await update.message.reply_video(
                    video=video, caption=caption,
                    reply_markup=main_reply_keyboard(), parse_mode="HTML"
                )
                sent = True
        except Exception as e:
            logger.warning(f"Failed to send start video: {e}")

    if not sent and START_IMAGE_PATH.exists():
        try:
            with open(START_IMAGE_PATH, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, caption=caption,
                    reply_markup=main_reply_keyboard(), parse_mode="HTML"
                )
                sent = True
        except Exception as e:
            logger.warning(f"Failed to send start image: {e}")

    if not sent:
        await reply_with_video(update.message, caption, reply_markup=main_reply_keyboard(), parse_mode="HTML")

    await reply_with_video(update.message,
        "🔎 <b>Select an OSINT Category to begin:</b>",
        reply_markup=osint_matrix_keyboard(),
        parse_mode="HTML"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return

    cmd_lines = []
    for cmd, info in PROVIDED_APIS.items():
        cmd_lines.append(f"/{cmd} — {info['icon']} {info['label']}")

    help_text = (
        f"📖 <b>AYUSH OSINT BOT — HELP</b>\n\n"
        f"<b>🔍 Available OSINT Commands:</b>\n"
        + "\n".join(cmd_lines) +
        f"\n\n<b>📌 Usage:</b> <code>/command &lt;input&gt;</code>\n"
        f"<i>Example: /num 9876543210</i>\n"
        f"<i>Example: /vehicle MH12AB1234</i>\n\n"
        f"<b>👑 Admin Commands:</b>\n"
        f"/export — 📥 Export database (Admin/Owner only)\n\n"
        f"<b>💰 Credits:</b> 50 AYUSH per lookup (FREE for whitelisted/owner)\n"
        f"<b>🎁 Daily Bonus:</b> +50 AYUSH auto-credited\n"
        f"<b>🎟️ Redeem Codes:</b> Unlock extra AYUSH credits\n"
        f"<b>🔗 Referral:</b> Invite friends, earn +100 AYUSH per invite\n\n"
        f"<b>🛡️ Note:</b> This bot is for <b>educational & legal OSINT research only</b>.\n"
        f"Misuse is strictly prohibited.\n\n"
        f"👨‍💻 <b>Developer:</b> @{OWNER_USERNAME}"
    )
    await reply_with_video(update.message, help_text, parse_mode="HTML")


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_PAUSED
    text = (update.message.text or "").strip()
    user = update.effective_user
    chat = update.effective_chat

    if not await check_force_join(update, context):
        return

    if BOT_PAUSED and user.id != MAIN_OWNER and user.id not in ADMIN_IDS:
        await reply_with_video(update.message,
            "🔧 <b>Bot is under maintenance!</b>\n\nPlease try again later or contact @GOD_AYUSH",
            parse_mode="HTML"
        )
        return

    if chat.type == "private" and not db.is_private_allowed(user.id):
        await reply_with_video(update.message,
            f"🔒 Personal access restricted! Contact @{OWNER_USERNAME} with Chat ID: <code>{user.id}</code>",
            parse_mode="HTML"
        )
        return

    u = db.get_user(user.id, user.first_name, user.username)

    shortcut_map = {
        "📱 NUM INFO": "num", "📞 TRUECALLER": "truecaller",
        "🚗 VEHICLE": "vehicle", "🪪 AADHAR": "aadhar",
        "👨‍👩‍👧 FAMILY": "family", "📄 PAN": "pan",
        "🔥 LPG INFO": "lpg", "🇵🇰 PAK SIM": "pak",
    }
    if text in shortcut_map:
        cmd = shortcut_map[text]
        info = PROVIDED_APIS[cmd]
        context.user_data["waiting_for"] = f"osint_input_{cmd}"
        await reply_with_video(update.message,
            f"{info['icon']} <b>{info['label'].upper()}</b>\n\n"
            f"📝 Enter: <i>{info['input_hint']}</i>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="osint_cancel")]]),
            parse_mode="HTML"
        )
        return

    if text == "💵 MY CREDITS":
        credit_disp = "👑 UNLIMITED (FREE ACCESS)" if db.is_free_tier(user.id) else str(u.get('credits', 0))
        await reply_with_video(update.message,
            f"💵 <b>AYUSH WALLET</b>\n\n"
            f"👤 User: <b>{html_escape(user.first_name)}</b>\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"💰 <b>Balance AYUSH:</b> <code>{credit_disp}</code>\n"
            f"🎁 <b>Daily Bonus:</b> +50 AYUSH everyday\n"
            f"🔍 <b>Per Lookup Cost:</b> 50 AYUSH\n\n"
            f"<i>Need more? Tap 💲 BUY CREDITS or use 🔗 REFERRAL!</i>",
            parse_mode="HTML"
        )

    elif text == "🎁 DAILY BONUS":
        today_str = datetime.date.today().isoformat()
        if u.get("last_bonus_claim") == today_str:
            await reply_with_video(update.message,
                "🎁 <b>DAILY BONUS ALREADY CLAIMED!</b>\n\nKal wapas aana naye +50 AYUSH ke liye! ⏰",
                parse_mode="HTML"
            )
        else:
            bonus = random.choices([random.randint(100, 300), 500], weights=[80, 20], k=1)[0]
            if not db.is_free_tier(user.id):
                u["credits"] = u.get("credits", 0) + bonus
            u["last_bonus_claim"] = today_str
            db.save()
            credit_disp = "👑 UNLIMITED" if db.is_free_tier(user.id) else str(u.get('credits', 0))
            await reply_with_video(update.message,
                f"🎁 <b>DAILY BONUS CLAIMED!</b>\n\n"
                f"✨ <b>+{bonus} AYUSH</b> added to your wallet!\n"
                f"💰 Total AYUSH: <code>{credit_disp}</code>\n\n"
                f"<i>Come back tomorrow for another bonus!</i>",
                parse_mode="HTML"
            )

    elif text == "📊 MY STATS":
        credit_disp = "👑 UNLIMITED" if db.is_free_tier(user.id) else str(u.get('credits', 0))
        await reply_with_video(update.message,
            f"📊 <b>AYUSH STATS</b>\n\n"
            f"🆔 User ID: <code>{user.id}</code>\n"
            f"👤 Name: <b>{html_escape(user.first_name)}</b>\n"
            f"💰 Credits AYUSH: <code>{credit_disp}</code>\n"
            f"🔍 Total Lookups: <code>{u.get('total_lookups', 0)}</code>\n"
            f"👥 Referrals: <code>{u.get('referrals', 0)}</code>\n"
            f"🛡️ Whitelisted: {'✅ YES' if db.is_private_allowed(user.id) else '❌ NO'}\n"
            f"📅 Joined: <code>{datetime.datetime.fromtimestamp(u.get('joined_at', int(time.time()))).strftime('%d %b %Y')}</code>",
            parse_mode="HTML"
        )

    elif text == "❓ HELP":
        await help_command(update, context)

    elif text == "💲 BUY CREDITS":
        plans_text = "💳 <b>AYUSH CREDIT PLANS</b>\n\n"
        for p in db.data.get("plans", []):
            plans_text += f"⭐ <b>{p['name']}</b>: ₹{p['price']} = <code>{p['credits']} AYUSH</code>\n"
        plans_text += f"\n👉 Contact Owner to Buy: @{OWNER_USERNAME}"
        kb = [[InlineKeyboardButton("👑 Buy from Owner", url=f"https://t.me/{OWNER_USERNAME}")]]
        await reply_with_video(update.message, plans_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")

    elif text == "🎟️ REDEEM CODE":
        context.user_data["waiting_for"] = "redeem_code"
        await reply_with_video(update.message, "🎟️ Apna Redeem Code enter karo (e.g. AYUSH-XXXXXX):", parse_mode="HTML")

    elif text == "🔗 REFERRAL":
        link = f"https://t.me/{BOT_USERNAME}?start={u.get('refer_code')}"
        await reply_with_video(update.message,
            f"🔗 <b>REFER & EARN AYUSH CREDITS!</b>\n\n"
            f"Har friend join hone par <b>+100 AYUSH</b>!\n\n"
            f"👉 <b>Your Link:</b>\n<code>{link}</code>\n\n"
            f"👥 Total Invited: <b>{u.get('referrals', 0)}</b>",
            parse_mode="HTML"
        )

    elif text == "🔴 ADMIN PANEL":
        if not db.is_admin(user.id):
            await reply_with_video(update.message, "❌ Sirf Admins & Owner ye panel open kar sakte hain!", parse_mode="HTML")
            return
        pause_label = "▶️ Resume Bot" if BOT_PAUSED else "⏸ Pause Bot"
        pause_data = "adm_resume_bot" if BOT_PAUSED else "adm_pause_bot"
        kb = [
            [InlineKeyboardButton("🌐 OSINT APIs Management", callback_data="adm_api_list")],
            [InlineKeyboardButton("🎁 Create Redeem Code", callback_data="adm_gen_code")],
            [InlineKeyboardButton("➕ Whitelist User", callback_data="adm_wl_add"),
             InlineKeyboardButton("➖ Remove Whitelist", callback_data="adm_wl_rem")],
            [InlineKeyboardButton("📜 View Whitelisted", callback_data="adm_view_wl")],
            [InlineKeyboardButton("📢 Broadcast Message", callback_data="adm_broadcast")],
            [InlineKeyboardButton("📥 EXPORT DATABASE", callback_data="adm_export")],
            [InlineKeyboardButton(pause_label, callback_data=pause_data)],
        ]
        if user.id == MAIN_OWNER:
            kb.append([
                InlineKeyboardButton("👑➕ Add Admin", callback_data="adm_add_admin"),
                InlineKeyboardButton("👑➖ Remove Admin", callback_data="adm_rem_admin")
            ])
            kb.append([InlineKeyboardButton("📜 View All Admins", callback_data="adm_view_admins")])
        await reply_with_video(update.message,
            f"🔴 <b>AYUSH ADMIN CONSOLE</b>\n\n"
            f"👥 Total Users: {len(db.data['users'])}\n"
            f"🔒 Whitelisted: {len(db.data.get('private_whitelist', []))}\n"
            f"🔍 Total Lookups: {db.data.get('stats', {}).get('total_lookups', 0)}\n"
            f"{'🔴 PAUSED' if BOT_PAUSED else '🟢 ACTIVE'}\n\n"
            f"Select option:",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )

    else:
        waiting = context.user_data.get("waiting_for")

        if waiting and waiting.startswith("osint_input_"):
            cmd = waiting.replace("osint_input_", "")
            context.user_data["waiting_for"] = None
            await execute_osint_lookup(update, context, cmd, text.strip())

        elif waiting == "redeem_code":
            code = text.strip().upper()
            codes = db.data.get("redeem_codes", {})
            if code in codes and codes[code].get("uses", 0) > 0:
                if user.id in codes[code].get("claimed_by", []):
                    await reply_with_video(update.message, "❌ Aapne ye code pehle claim kar liya hai!", parse_mode="HTML")
                else:
                    amt = codes[code]["credits"]
                    if not db.is_free_tier(user.id):
                        u["credits"] = u.get("credits", 0) + amt
                    codes[code]["uses"] -= 1
                    codes[code].setdefault("claimed_by", []).append(user.id)
                    db.save()
                    context.user_data["waiting_for"] = None
                    await reply_with_video(update.message, f"🎉 <b>SUCCESS!</b> +{amt} AYUSH added!", parse_mode="HTML")
            else:
                await reply_with_video(update.message, "❌ Invalid ya expired code!", parse_mode="HTML")

        elif waiting == "broadcast_msg":
            if user.id == MAIN_OWNER or user.id in ADMIN_IDS:
                broadcast_text = text.strip()
                context.user_data["waiting_for"] = None
                success = 0
                fail = 0
                status_msg = await update.message.reply_text("📢 <b>Broadcasting...</b>", parse_mode="HTML")
                for uid_str in list(db.data["users"].keys()):
                    try:
                        await context.bot.send_message(
                            int(uid_str),
                            f"📢 <b>BROADCAST FROM ADMIN</b>\n\n{broadcast_text}\n\n<i>— @{OWNER_USERNAME}</i>",
                            parse_mode="HTML"
                        )
                        success += 1
                    except Exception:
                        fail += 1
                try:
                    await status_msg.edit_text(
                        f"📢 <b>BROADCAST COMPLETE!</b>\n\n✅ Sent: <b>{success}</b>\n❌ Failed: <b>{fail}</b>",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
            else:
                context.user_data["waiting_for"] = None

        elif waiting == "adm_gen_code_cr":
            try:
                amt = int(text.strip())
                context.user_data["temp_redeem_cr"] = amt
                context.user_data["waiting_for"] = "adm_gen_code_uses"
                await reply_with_video(update.message, f"AYUSH Amount: <b>{amt}</b>\n\nMax uses enter karo:", parse_mode="HTML")
            except Exception:
                await reply_with_video(update.message, "❌ Valid number of credits enter karo:")

        elif waiting == "adm_gen_code_uses":
            try:
                uses = int(text.strip())
                amt = context.user_data.get("temp_redeem_cr", 1000)
                code = "AYUSH-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
                db.data.setdefault("redeem_codes", {})[code] = {
                    "credits": amt, "uses": uses, "claimed_by": []
                }
                db.save()
                context.user_data["waiting_for"] = None
                await reply_with_video(update.message,
                    f"🎁 <b>REDEEM CODE GENERATED!</b>\n\n"
                    f"Code: <code>{code}</code>\n"
                    f"AYUSH: <b>{amt}</b>\n"
                    f"Max Uses: <b>{uses}</b>",
                    parse_mode="HTML"
                )
            except Exception:
                await reply_with_video(update.message, "❌ Valid number of uses enter karo:")

        elif waiting and waiting.startswith("adm_change_api_"):
            cmd = waiting.replace("adm_change_api_", "")
            new_url = text.strip()
            if "{arg}" not in new_url:
                await reply_with_video(update.message, "⚠️ URL me <code>{arg}</code> hona zaroori hai! Dubara bhejo:", parse_mode="HTML")
                return
            apis = {}
            if API_CONFIG_FILE.exists():
                try:
                    with open(API_CONFIG_FILE, "r", encoding="utf-8") as f:
                        apis = json.load(f)
                except Exception:
                    pass
            apis[cmd] = new_url
            try:
                with open(API_CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(apis, f, indent=2)
            except Exception as e:
                logger.error(f"Save API config error: {e}")
            context.user_data["waiting_for"] = None
            await reply_with_video(update.message,
                f"✅ <b>API UPDATED FOR /{cmd}!</b>\n\nNew Endpoint: <code>{html_escape(new_url)}</code>",
                parse_mode="HTML"
            )

        elif waiting == "adm_api_new_pair":
            parts = text.strip().split(maxsplit=1)
            if len(parts) < 2 or "{arg}" not in parts[1]:
                await reply_with_video(update.message, "❌ Format: <code>&lt;command&gt; &lt;url_with_{arg}&gt;</code>", parse_mode="HTML")
                return
            n_cmd = parts[0].lstrip("/").lower()
            n_url = parts[1].strip()
            apis = {}
            if API_CONFIG_FILE.exists():
                try:
                    with open(API_CONFIG_FILE, "r", encoding="utf-8") as f:
                        apis = json.load(f)
                except Exception:
                    pass
            apis[n_cmd] = n_url
            with open(API_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(apis, f, indent=2)
            context.user_data["waiting_for"] = None
            await reply_with_video(update.message, f"✅ New Module <code>/{n_cmd}</code> registered!", parse_mode="HTML")

        elif waiting == "adm_add_admin_uid":
            if user.id == MAIN_OWNER:
                try:
                    target_uid = int(text.strip())
                    admins = db.data.setdefault("admins", [MAIN_OWNER])
                    if target_uid not in admins:
                        admins.append(target_uid)
                        db.save()
                        db.get_user(target_uid)["credits"] = 999999999
                        db.save()
                        await reply_with_video(update.message, f"👑✅ User <code>{target_uid}</code> ko ADMIN bana diya!", parse_mode="HTML")
                    else:
                        await reply_with_video(update.message, "Ye user pehle se Admin hai!", parse_mode="HTML")
                except Exception:
                    await reply_with_video(update.message, "❌ Invalid numeric User ID!")
            context.user_data["waiting_for"] = None

        elif waiting == "adm_rem_admin_uid":
            if user.id == MAIN_OWNER:
                try:
                    target_uid = int(text.strip())
                    admins = db.data.get("admins", [])
                    if target_uid == MAIN_OWNER:
                        await reply_with_video(update.message, "❌ Owner ko admin se nahi hata sakte!", parse_mode="HTML")
                    elif target_uid in admins:
                        admins.remove(target_uid)
                        db.save()
                        await reply_with_video(update.message, f"👑❌ User <code>{target_uid}</code> ko Admin se hataya!", parse_mode="HTML")
                    else:
                        await reply_with_video(update.message, "User admin list me nahi mila!", parse_mode="HTML")
                except Exception:
                    await reply_with_video(update.message, "❌ Invalid numeric User ID!")
            context.user_data["waiting_for"] = None

        elif waiting == "adm_wl_uid":
            if user.id in ADMIN_IDS or user.id == MAIN_OWNER:
                try:
                    target_uid = int(text.strip())
                    if target_uid not in db.data["private_whitelist"]:
                        db.data["private_whitelist"].append(target_uid)
                        db.save()
                        db.get_user(target_uid)["credits"] = 999999999
                        db.save()
                        await reply_with_video(update.message, f"✅ User <code>{target_uid}</code> whitelisted!", parse_mode="HTML")
                    else:
                        await reply_with_video(update.message, "User pehle se whitelisted hai!", parse_mode="HTML")
                except Exception:
                    await reply_with_video(update.message, "❌ Invalid numeric User ID!")
            context.user_data["waiting_for"] = None

        elif waiting == "adm_rem_wl":
            if user.id in ADMIN_IDS or user.id == MAIN_OWNER:
                try:
                    target_uid = int(text.strip())
                    if target_uid in db.data["private_whitelist"]:
                        db.data["private_whitelist"].remove(target_uid)
                        db.save()
                        await reply_with_video(update.message, f"✅ User <code>{target_uid}</code> removed from whitelist!", parse_mode="HTML")
                    else:
                        await reply_with_video(update.message, "User whitelist me nahi mila!", parse_mode="HTML")
                except Exception:
                    await reply_with_video(update.message, "❌ Invalid numeric User ID!")
            context.user_data["waiting_for"] = None


# ==================== OSINT LOOKUP EXECUTION ====================

async def execute_osint_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE, cmd: str, arg_val: str):
    user = update.effective_user
    u = db.get_user(user.id, user.first_name, user.username)

    OSINT_COST = 50
    if not db.is_free_tier(user.id):
        user_cr = u.get("credits", 0)
        if user_cr < OSINT_COST:
            await reply_with_video(update.message,
                f"❌ <b>INSUFFICIENT AYUSH CREDITS!</b>\n\n"
                f"Required: <b>{OSINT_COST} AYUSH</b>\n"
                f"Your balance: <code>{user_cr}</code> AYUSH\n\n"
                f"👉 <i>Tap '💲 BUY CREDITS' or claim '🎁 DAILY BONUS'!</i>",
                parse_mode="HTML"
            )
            return
        u["credits"] -= OSINT_COST
        db.save()

    u["total_lookups"] = u.get("total_lookups", 0) + 1
    db.data.setdefault("stats", {})["total_lookups"] = db.data.get("stats", {}).get("total_lookups", 0) + 1
    db.save()

    info = PROVIDED_APIS.get(cmd, {})
    label = info.get("label", f"/{cmd.upper()}")
    icon = info.get("icon", "🔍")

    api_map = {}
    if API_CONFIG_FILE.exists():
        try:
            with open(API_CONFIG_FILE, "r", encoding="utf-8") as f:
                api_map = json.load(f)
        except Exception:
            pass

    api_url = api_map.get(cmd) or info.get("url")
    if not api_url:
        await reply_with_video(update.message, f"⚠️ API for /{cmd} is not configured.")
        return

    req_url = api_url.replace("{arg}", arg_val)

    frames = [
        f"{icon} <b>AYUSH INTELLIGENCE CORE</b>\n━━━━━━━━━━━━━━━━━━\n◉ SCANNING   ░░░░░░░░░░\nTARGET ▸ {label}\n\nOpening intelligence layer...",
        f"{icon} <b>AYUSH INTELLIGENCE CORE</b>\n━━━━━━━━━━━━━━━━━━\n◉ ANALYZING  ███░░░░░░░\nTARGET ▸ {label}\n\nProcessing query view...",
        f"{icon} <b>AYUSH INTELLIGENCE CORE</b>\n━━━━━━━━━━━━━━━━━━\n◉ RENDERING  ███████░░░\nTARGET ▸ {label}\n\nPreparing result interface..."
    ]
    status_msg = await update.message.reply_text(frames[0], parse_mode="HTML")
    for frame in frames[1:]:
        try:
            await asyncio.sleep(0.25)
            await status_msg.edit_text(frame, parse_mode="HTML")
        except Exception:
            pass

    try:
        s = await get_http_session()
        async with s.get(req_url, timeout=aiohttp.ClientTimeout(total=15)) as r:
            if r.status == 200:
                txt = await r.text()
                try:
                    res_json = json.loads(txt)
                    pretty = json.dumps(res_json, indent=2, ensure_ascii=False)
                except Exception:
                    pretty = txt

                if len(pretty) > 3500:
                    pretty = pretty[:3500] + "\n...[TRUNCATED]"

                resp = (
                    f"╭━━━━ ◈ <b>AYUSH INTELLIGENCE REPORT</b> ◈ ━━━━╮\n"
                    f"◈ <b>MODULE:</b> {icon} {label}\n"
                    f"◈ <b>TARGET:</b> <code>{html_escape(arg_val)}</code>\n"
                    f"◈ <b>STATUS:</b> ✅ PROCESSED\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"<pre>{html_escape(pretty)}</pre>\n"
                    f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                    f"👨‍💻 <b>Developer:</b> @{OWNER_USERNAME}"
                )

                result_msg = await status_msg.edit_text(resp, parse_mode="HTML")

                async def auto_delete():
                    await asyncio.sleep(90)
                    try:
                        await result_msg.delete()
                    except Exception:
                        pass
                asyncio.create_task(auto_delete())

            else:
                await status_msg.edit_text(
                    f"❌ API returned status code: {r.status}\n\n👨‍💻 @{OWNER_USERNAME}",
                    parse_mode="HTML"
                )
    except Exception as e:
        await status_msg.edit_text(f"❌ Error fetching intelligence: {e}\n\n👨‍💻 @{OWNER_USERNAME}", parse_mode="HTML")


# ==================== CALLBACK ROUTER ====================

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_PAUSED
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user

    if data == "check_joined":
        missing = []
        for ch in FORCE_JOIN_CHANNELS:
            try:
                member = await context.bot.get_chat_member(f"@{ch}", user.id)
                if member.status not in ["member", "administrator", "creator"]:
                    missing.append(ch)
            except Exception:
                missing.append(ch)
        if not missing:
            await query.edit_message_text(
                "✅ <b>All Channels Joined Successfully!</b>\n\nAb /start tap karke bot use karo! 🚀",
                parse_mode="HTML"
            )
            return
        kb = []
        for ch in missing:
            kb.append([InlineKeyboardButton(f"📢 Join @{ch}", url=f"https://t.me/{ch}")])
        kb.append([InlineKeyboardButton("✅ I've Joined — Verify", callback_data="check_joined")])
        await query.edit_message_text(
            f"❌ <b>Abhi tak join nahi kiya!</b>\n\nMissing: " + ", ".join([f"@{ch}" for ch in missing]),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )
        return

    elif data == "osint_cancel":
        context.user_data["waiting_for"] = None
        await query.edit_message_text("❌ Lookup cancelled.")

    elif data == "adm_export":
        await query.answer("Preparing export...")
        try:
            await query.edit_message_text("📦 <b>Exporting database files...</b>", parse_mode="HTML")
        except Exception:
            pass
        await export_database(query.message, user.id, silent=False)

    elif data.startswith("osint_cat_"):
        cat_key = data.replace("osint_cat_", "")
        cat_info = OSINT_CATEGORIES.get(cat_key)
        if cat_info:
            kb = []
            for m_cmd, m_label in cat_info["modules"]:
                kb.append([InlineKeyboardButton(m_label, callback_data=f"osint_mod_{m_cmd}")])
            kb.append([InlineKeyboardButton("🔙 Back", callback_data="osint_back")])
            await query.edit_message_text(
                f"🔍 <b>{cat_info['title']}</b>\n\nTap a module:",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )

    elif data.startswith("osint_mod_"):
        cmd = data.replace("osint_mod_", "")
        info = PROVIDED_APIS.get(cmd, {})
        context.user_data["waiting_for"] = f"osint_input_{cmd}"
        await query.edit_message_text(
            f"{info.get('icon', '🔍')} <b>{info.get('label', cmd.upper())}</b>\n\n"
            f"📝 Enter: <i>{info.get('input_hint', 'target value')}</i>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="osint_cancel")]]),
            parse_mode="HTML"
        )

    elif data == "osint_back":
        context.user_data["waiting_for"] = None
        await query.edit_message_text("🔎 <b>Select an OSINT Category:</b>", reply_markup=osint_matrix_keyboard(), parse_mode="HTML")

    elif data == "adm_api_list":
        if user.id not in ADMIN_IDS and user.id != MAIN_OWNER:
            return await query.answer("Access Denied!")
        kb, total, cur_page, total_p = admin_apis_keyboard(0)
        await query.edit_message_text(
            f"🌐 <b>API ENDPOINTS</b>\n\n"
            f"Total: <b>{total}</b> (Page {cur_page}/{total_p})\n"
            f"Tap any API to edit/delete:",
            reply_markup=kb,
            parse_mode="HTML"
        )

    elif data.startswith("adm_api_page_"):
        p = int(data.replace("adm_api_page_", ""))
        kb, total, cur_page, total_p = admin_apis_keyboard(p)
        await query.edit_message_text(
            f"🌐 <b>API ENDPOINTS</b>\n\nTotal: <b>{total}</b> (Page {cur_page}/{total_p})",
            reply_markup=kb,
            parse_mode="HTML"
        )

    elif data.startswith("adm_api_view_"):
        cmd = data.replace("adm_api_view_", "")
        apis = {}
        if API_CONFIG_FILE.exists():
            with open(API_CONFIG_FILE, "r", encoding="utf-8") as f:
                apis = json.load(f)
        url = apis.get(cmd) or PROVIDED_APIS.get(cmd, {}).get("url", "Not found")
        kb = [
            [InlineKeyboardButton("✏️ Change URL", callback_data=f"adm_api_edit_{cmd}")],
            [InlineKeyboardButton("🗑 Delete Module", callback_data=f"adm_api_del_{cmd}")],
            [InlineKeyboardButton("🔙 Back", callback_data="adm_api_list")]
        ]
        await query.edit_message_text(
            f"⚙️ <b>API MODULE: /{cmd}</b>\n\nURL:\n<code>{html_escape(url)}</code>",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )

    elif data.startswith("adm_api_edit_"):
        cmd = data.replace("adm_api_edit_", "")
        context.user_data["waiting_for"] = f"adm_change_api_{cmd}"
        await query.edit_message_text(
            f"✏️ <b>CHANGE URL FOR /{cmd}</b>\n\n"
            f"Send new API URL with <code>{{arg}}</code>:\n"
            f"<i>Example: https://myapi.com/lookup?key=xyz&q={{arg}}</i>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_api_list")]]),
            parse_mode="HTML"
        )

    elif data.startswith("adm_api_del_"):
        cmd = data.replace("adm_api_del_", "")
        apis = {}
        if API_CONFIG_FILE.exists():
            with open(API_CONFIG_FILE, "r", encoding="utf-8") as f:
                apis = json.load(f)
        apis.pop(cmd, None)
        with open(API_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(apis, f, indent=2)
        await query.edit_message_text(
            f"🗑 <b>Module /{cmd} deleted!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="adm_api_list")]]),
            parse_mode="HTML"
        )

    elif data == "adm_api_add_new":
        context.user_data["waiting_for"] = "adm_api_new_pair"
        await query.edit_message_text(
            f"➕ <b>ADD NEW API</b>\n\nFormat: <code>&lt;command&gt; &lt;url_with_{{arg}}&gt;</code>\n\n"
            f"<i>Example: <code>num2 https://api.site.com/search?num={{arg}}</code></i>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_api_list")]]),
            parse_mode="HTML"
        )

    elif data == "adm_gen_code":
        if user.id not in ADMIN_IDS and user.id != MAIN_OWNER:
            return await query.answer("Access Denied!")
        context.user_data["waiting_for"] = "adm_gen_code_cr"
        await query.edit_message_text(
            "🎁 <b>GENERATE REDEEM CODE</b>\n\nAYUSH credits enter karo (e.g. 5000):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_back_main")]]),
            parse_mode="HTML"
        )

    elif data == "adm_add_admin":
        if user.id != MAIN_OWNER:
            return await query.answer("Sirf Owner admin add kar sakta hai!")
        context.user_data["waiting_for"] = "adm_add_admin_uid"
        await query.edit_message_text(
            "👑➕ <b>ADD ADMIN</b>\n\nUser ID send karein:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_back_main")]]),
            parse_mode="HTML"
        )

    elif data == "adm_rem_admin":
        if user.id != MAIN_OWNER:
            return await query.answer("Sirf Owner admin remove kar sakta hai!")
        context.user_data["waiting_for"] = "adm_rem_admin_uid"
        await query.edit_message_text(
            "👑➖ <b>REMOVE ADMIN</b>\n\nUser ID send karein:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_back_main")]]),
            parse_mode="HTML"
        )

    elif data == "adm_view_admins":
        admins = db.data.get("admins", [MAIN_OWNER])
        adm_str = "\n".join([f"• <code>{x}</code> {'(👑 OWNER)' if x == MAIN_OWNER else '(🛡️ ADMIN)'}" for x in admins])
        await query.edit_message_text(
            f"👑 <b>Admins:</b>\n\n{adm_str}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="adm_back_main")]]),
            parse_mode="HTML"
        )

    elif data == "adm_wl_add":
        context.user_data["waiting_for"] = "adm_wl_uid"
        await query.edit_message_text("Send Telegram numeric User ID to whitelist:")

    elif data == "adm_wl_rem":
        context.user_data["waiting_for"] = "adm_rem_wl"
        await query.edit_message_text("Send Telegram numeric User ID to remove from whitelist:")

    elif data == "adm_view_wl":
        wl = db.data.get("private_whitelist", [])
        wl_str = "\n".join([f"• <code>{x}</code>" for x in wl]) if wl else "No users whitelisted"
        await query.edit_message_text(
            f"🔒 <b>Whitelisted User IDs:</b>\n\n{wl_str}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="adm_back_main")]]),
            parse_mode="HTML"
        )

    elif data == "adm_broadcast":
        if user.id not in ADMIN_IDS and user.id != MAIN_OWNER:
            return await query.answer("Access Denied!")
        context.user_data["waiting_for"] = "broadcast_msg"
        await query.edit_message_text(
            "📢 <b>BROADCAST</b>\n\nMessage type karo:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_back_main")]]),
            parse_mode="HTML"
        )

    elif data == "adm_pause_bot":
        if user.id not in ADMIN_IDS and user.id != MAIN_OWNER:
            return await query.answer("Access Denied!")
        BOT_PAUSED = True
        await query.edit_message_text(
            "⏸ <b>Bot PAUSED!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="adm_back_main")]]),
            parse_mode="HTML"
        )

    elif data == "adm_resume_bot":
        if user.id not in ADMIN_IDS and user.id != MAIN_OWNER:
            return await query.answer("Access Denied!")
        BOT_PAUSED = False
        await query.edit_message_text(
            "▶️ <b>Bot RESUMED!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="adm_back_main")]]),
            parse_mode="HTML"
        )

    elif data == "adm_back_main":
        pause_label = "▶️ Resume Bot" if BOT_PAUSED else "⏸ Pause Bot"
        pause_data = "adm_resume_bot" if BOT_PAUSED else "adm_pause_bot"
        kb = [
            [InlineKeyboardButton("🌐 OSINT APIs Management", callback_data="adm_api_list")],
            [InlineKeyboardButton("🎁 Create Redeem Code", callback_data="adm_gen_code")],
            [InlineKeyboardButton("➕ Whitelist User", callback_data="adm_wl_add"),
             InlineKeyboardButton("➖ Remove Whitelist", callback_data="adm_wl_rem")],
            [InlineKeyboardButton("📜 View Whitelisted", callback_data="adm_view_wl")],
            [InlineKeyboardButton("📢 Broadcast Message", callback_data="adm_broadcast")],
            [InlineKeyboardButton("📥 EXPORT DATABASE", callback_data="adm_export")],
            [InlineKeyboardButton(pause_label, callback_data=pause_data)],
        ]
        if user.id == MAIN_OWNER:
            kb.append([
                InlineKeyboardButton("👑➕ Add Admin", callback_data="adm_add_admin"),
                InlineKeyboardButton("👑➖ Remove Admin", callback_data="adm_rem_admin")
            ])
            kb.append([InlineKeyboardButton("📜 View All Admins", callback_data="adm_view_admins")])
        await query.edit_message_text(
            f"🔴 <b>AYUSH ADMIN CONSOLE</b>\n\nSelect action:",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )


# ==================== DIRECT COMMAND HANDLER ====================

async def handle_direct_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.split()[0].lstrip("/").lower()
    args = update.message.text.split()[1:]

    if cmd not in PROVIDED_APIS:
        await reply_with_video(update.message,
            f"❌ Unknown command /{cmd}.\nUse /help to see available commands.",
            parse_mode="HTML"
        )
        return

    if not args:
        await reply_with_video(update.message,
            f"❌ Usage: <code>/{cmd} &lt;input&gt;</code>\n\n📝 <i>{PROVIDED_APIS[cmd]['input_hint']}</i>",
            parse_mode="HTML"
        )
        return

    arg_val = " ".join(args).strip()
    await execute_osint_lookup(update, context, cmd, arg_val)


# ==================== ERROR HANDLER ====================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=context.error)
    if update and hasattr(update, 'effective_user') and update.effective_user:
        try:
            if hasattr(update, 'message') and update.message:
                await update.message.reply_text("⚠️ Internal error. Try again.")
            elif hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.answer("⚠️ Error occurred.")
        except Exception:
            pass


# ==================== MAIN ====================

def main():
    print("=" * 60)
    print("🚀 STARTING AYUSH OSINT BOT (PROFESSIONAL)")
    print(f"👑 Owner ID: {MAIN_OWNER}")
    print(f"📢 Force Join: {FORCE_JOIN_CHANNELS}")
    print(f"🔍 OSINT Modules: {len(PROVIDED_APIS)}")
    print(f"📥 Export Feature: ENABLED")
    print("=" * 60)

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(128)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(15)
        .pool_timeout(10)
        .build()
    )

    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("export", export_command))

    for c in PROVIDED_APIS.keys():
        app.add_handler(CommandHandler(c, handle_direct_command))

    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    print("✅ Bot online via polling!")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()