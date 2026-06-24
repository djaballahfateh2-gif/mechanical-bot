import os
import json
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", category=UserWarning)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters, ConversationHandler
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ADMIN_ID = int(os.environ["TELEGRAM_ADMIN_ID"])

# DATA_DIR: set to /data on Railway (persistent volume), defaults to script dir in dev
DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
os.makedirs(DATA_DIR, exist_ok=True)

STRUCTURE = {
    "📗 السنة 1 - جذع مشترك": {
        "key": "S1_tronc",
        "matieres": [
            "Analyse 1", "Analyse 2", "Algèbre 1", "Algèbre 2",
            "Physique 1", "Physique 2", "Chimie 1", "Chimie 2",
            "Probabilités et statistiques", "Informatique"
        ]
    },
    "📘 السنة 2 - Engineer Génie Mécanique": {
        "key": "S2_engineer",
        "matieres": [
            "Mechanical fabrication", "Electronics", "Applied mathematics",
            "Computer science 3", "Rational mechanics", "Electrical engineering",
            "Fluid mechanics", "Technical English", "Wave and vibrations",
            "Thermodynamique appliquée", "Production et transport d'énergie",
            "Résistance des matériaux", "Conversion d'énergie",
            "Transfert de chaleur", "Hydraulique et pneumatique",
            "Mesure et Instrumentation"
        ]
    },
    "📘 السنة 2 - Bachelor Génie Mécanique": {
        "key": "S2_bachelor_gm",
        "matieres": [
            "Méthodes Numériques", "Mathématiques 4", "Electricité industrielle",
            "Thermodynamique 2", "Sciences des matériaux", "Fabrication Mécanique",
            "Résistance des matériaux"
        ]
    },
    "📘 السنة 2 - Bachelor Électromécanique": {
        "key": "S2_bachelor_em",
        "matieres": [
            "Méthodes Numériques", "Logique combinatoire et séquentielle",
            "Notions de mesures électriques", "Résistance des matériaux",
            "Systèmes de conversion de l'énergie", "Hydraulique et pneumatique"
        ]
    },
    "📙 السنة 3 - Bachelor Construction Mécanique": {
        "key": "S3_bachelor_cm",
        "matieres": [
            "Mécanique analytique", "Élasticité", "Résistance des matériaux 2",
            "Asservissement et régulation", "Maintenance",
            "Environnement et développement durable",
            "Construction Mécanique 2", "Théorie des mécanismes",
            "Transfert thermique", "Systèmes hydrauliques et pneumatiques",
            "Moteur à combustion interne", "Matériaux non métalliques",
            "Dynamique des structures"
        ]
    },
    "📙 السنة 3 - Bachelor Énergétique": {
        "key": "S3_bachelor_en",
        "matieres": [
            "Mécanique des fluides 2", "Turbomachines 1", "Conversion d'énergie",
            "Transfert de chaleur 1", "Asservissement et régulation",
            "Notion d'éléments de machines", "Mesure et instrumentation",
            "Environnement et développement durable",
            "Transfert de chaleur 2", "Cryogénie", "Turbomachines 2",
            "Moteurs à combustion interne", "Energies renouvelables",
            "Machines Frigorifiques et PAC"
        ]
    },
    "📙 السنة 3 - Bachelor Maintenance Industrielle": {
        "key": "S3_bachelor_mi",
        "matieres": [
            "Électronique appliquée", "Éléments de machines",
            "Organisation et méthode de la maintenance",
            "Électrotechnique appliquée", "Éléments de transfert de chaleur",
            "G.M.A.O", "Capteurs et métrologie",
            "Technologie des machines thermiques et hydrauliques",
            "Robotique industrielle", "Moteur à combustion interne",
            "Traitement de signal", "Dynamique des structures",
            "Fiabilité", "Outils de maintenance préventive",
            "Systèmes asservis et Régulation"
        ]
    },
    "📒 السنة 3 - Engineer Génie Mécanique": {
        "key": "S3_engineer_gm",
        "matieres": [
            "Théorie des mécanismes", "Construction mécanique 2",
            "Traitement thermique", "Dynamique des structures",
            "Moteur à combustion interne", "Diagnostic et gestion des pannes",
            "Rhéologie des matériaux", "Introduction à la propriété industrielle",
            "Logistique et gestion des stocks", "Entreprenariat et start-up"
        ]
    },
    "📕 السنة 4/5 - Master Construction Mécanique": {
        "key": "S4_master_cm",
        "matieres": [
            "Résistance des matériaux avancée", "Automatisation des systèmes industriels",
            "Mécanique des fluides appliquée", "Technique de soudage",
            "Moteurs à combustion interne", "Techniques de fabrication avancées",
            "Mécanique des milieux continus", "Programmation avancée python",
            "Systèmes mécaniques articulés et robotique", "Optimisation",
            "Conception des systèmes mécaniques", "CFAO",
            "Méthode des éléments finis", "Dynamique des structures avancées"
        ]
    },
    "📕 السنة 4/5 - Master Énergétique": {
        "key": "S4_master_en",
        "matieres": [
            "Transfert de chaleur et de masse approfondi",
            "Transport et stockage de l'énergie", "Machines thermiques",
            "Méthodes numériques approfondies", "Instrumentation et mesures",
            "Mécanique des fluides approfondie", "Programmation avancée python",
            "Méthodes des volumes finis", "Combustion",
            "Chauffage et climatisation", "Asservissement et régulation",
            "Dynamique des gaz", "Le séchage thermique",
            "Turbomachines approfondies"
        ]
    },
    "📕 السنة 4/5 - Master Maintenance Industrielle": {
        "key": "S4_master_mi",
        "matieres": [
            "Dynamique des structures", "Méthodes statistiques et échantillonnage",
            "Mécanique des milieux continus", "Introduction aux matériaux",
            "Stratégie de maintenance", "Traitement de signal",
            "Thermodynamique Appliquée", "Programmation avancée python",
            "Contrôle non destructif", "Méthode des éléments finis",
            "Capteurs intelligents", "Fiabilité des systèmes",
            "Vibration des machines tournantes",
            "Gestion de maintenance assistée par ordinateur"
        ]
    },
}

KEY_MAP = {data["key"]: (label, data) for label, data in STRUCTURE.items()}

FILE_IDS_PATH = os.path.join(DATA_DIR, "file_ids.json")
STATS_PATH    = os.path.join(DATA_DIR, "stats.json")
USERS_PATH    = os.path.join(DATA_DIR, "users.json")
RATINGS_PATH  = os.path.join(DATA_DIR, "ratings.json")

_voted: set = set()

SELECT_NIVEAU, SELECT_SUBJECT, RECEIVE_FILE, RECEIVE_RESTORE = range(4)


# ── file_ids helpers ───────────────────────────────────────────────────────────
# Structure: { "niveau_key|matiere": [{"name": "cours.pdf", "file_id": "BQA..."}, ...] }

def load_file_ids() -> dict:
    if os.path.exists(FILE_IDS_PATH):
        with open(FILE_IDS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_file_ids(data: dict):
    with open(FILE_IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_files_for(niveau_key: str, matiere: str) -> list:
    return load_file_ids().get(f"{niveau_key}|{matiere}", [])


def add_file_entry(niveau_key: str, matiere: str, name: str, file_id: str):
    data = load_file_ids()
    key = f"{niveau_key}|{matiere}"
    entries = data.get(key, [])
    entries = [e for e in entries if e["name"] != name]
    entries.append({"name": name, "file_id": file_id})
    data[key] = entries
    save_file_ids(data)


def remove_file_entry(niveau_key: str, matiere: str, name: str) -> bool:
    data = load_file_ids()
    key = f"{niveau_key}|{matiere}"
    entries = data.get(key, [])
    new_entries = [e for e in entries if e["name"] != name]
    if len(new_entries) == len(entries):
        return False
    if new_entries:
        data[key] = new_entries
    else:
        data.pop(key, None)
    save_file_ids(data)
    return True


# ── users helpers ──────────────────────────────────────────────────────────────

def load_users() -> dict:
    if os.path.exists(USERS_PATH):
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_users(users: dict):
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def register_user(user):
    users = load_users()
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "first_name": user.first_name or "",
            "username": user.username or "",
            "joined": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        save_users(users)


# ── stats helpers ──────────────────────────────────────────────────────────────

def load_stats() -> dict:
    if os.path.exists(STATS_PATH):
        with open(STATS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_stats(stats: dict):
    with open(STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def record_download(niveau_key: str, matiere: str):
    stats = load_stats()
    key = f"{niveau_key}|{matiere}"
    entry = stats.get(key, {"count": 0, "last": None})
    entry["count"] += 1
    entry["last"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    stats[key] = entry
    save_stats(stats)


# ── ratings helpers ────────────────────────────────────────────────────────────

def load_ratings() -> dict:
    if os.path.exists(RATINGS_PATH):
        with open(RATINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_ratings(ratings: dict):
    with open(RATINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(ratings, f, ensure_ascii=False, indent=2)


def record_rating(niveau_key: str, matiere: str, vote: str):
    ratings = load_ratings()
    key = f"{niveau_key}|{matiere}"
    entry = ratings.get(key, {"up": 0, "down": 0})
    entry[vote] += 1
    ratings[key] = entry
    save_ratings(ratings)


def rating_keyboard(niveau_key: str, idx: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("👍 مفيد", callback_data=f"rate_up_{niveau_key}_{idx}"),
        InlineKeyboardButton("👎 يحتاج تحسين", callback_data=f"rate_dn_{niveau_key}_{idx}"),
    ]])


# ── keyboard helpers ───────────────────────────────────────────────────────────

def niveau_keyboard(prefix: str = "niveau") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data=f"{prefix}_{data['key']}")]
        for label, data in STRUCTURE.items()
    ])


def subject_keyboard(niveau_key: str, prefix: str = "mat") -> InlineKeyboardMarkup:
    label, data = KEY_MAP[niveau_key]
    rows = [
        [InlineKeyboardButton(f"📖 {m}", callback_data=f"{prefix}_{niveau_key}_{i}")]
        for i, m in enumerate(data["matieres"])
    ]
    rows.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_start")])
    return InlineKeyboardMarkup(rows)


# ── /start ─────────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update.effective_user)
    await update.message.reply_text(
        "🎓 *بوت هندسة ميكانيكية - جامعة ابن خلدون تيارت*\n\nاختر المستوى:",
        reply_markup=niveau_keyboard(),
        parse_mode="Markdown"
    )


# ── browse flow ────────────────────────────────────────────────────────────────

async def show_matieres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    niveau_key = query.data[len("niveau_"):]
    if niveau_key not in KEY_MAP:
        await query.answer("خطأ!")
        return
    label, _ = KEY_MAP[niveau_key]
    await query.edit_message_text(
        f"{label}\n\nاختر المادة:",
        reply_markup=subject_keyboard(niveau_key),
        parse_mode="Markdown"
    )


async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    idx = int(parts[-1])
    niveau_key = "_".join(parts[1:-1])

    if niveau_key not in KEY_MAP:
        await query.message.reply_text("⚠️ خطأ في البيانات.")
        return

    _, data = KEY_MAP[niveau_key]
    matiere = data["matieres"][idx]
    entries = get_files_for(niveau_key, matiere)

    if not entries:
        await query.message.reply_text(
            f"⚠️ لا توجد ملفات لـ *{matiere}* بعد.", parse_mode="Markdown"
        )
        return

    await query.message.reply_text(
        f"📤 جاري إرسال ملفات *{matiere}*...", parse_mode="Markdown"
    )
    for entry in entries:
        await query.message.reply_document(
            document=entry["file_id"],
            filename=entry["name"]
        )

    record_download(niveau_key, matiere)

    await query.message.reply_text(
        f"⭐ كيف تقيّم ملفات *{matiere}*؟",
        reply_markup=rating_keyboard(niveau_key, idx),
        parse_mode="Markdown"
    )


async def back_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎓 *بوت هندسة ميكانيكية - جامعة ابن خلدون تيارت*\n\nاختر المستوى:",
        reply_markup=niveau_keyboard(),
        parse_mode="Markdown"
    )


async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    parts = query.data.split("_")
    vote = parts[1]
    idx = int(parts[-1])
    niveau_key = "_".join(parts[2:-1])

    if niveau_key not in KEY_MAP:
        await query.answer("خطأ!")
        return

    _, data = KEY_MAP[niveau_key]
    matiere = data["matieres"][idx]
    vote_key = (user_id, f"{niveau_key}|{matiere}")

    if vote_key in _voted:
        await query.answer("✅ لقد صوّتت مسبقاً على هذه المادة.")
        return

    _voted.add(vote_key)
    record_rating(niveau_key, matiere, vote)

    ratings = load_ratings()
    entry = ratings.get(f"{niveau_key}|{matiere}", {"up": 0, "down": 0})
    up, dn = entry["up"], entry["down"]
    total = up + dn
    bar = "🟩" * up + "🟥" * dn if total <= 10 else ""

    emoji = "👍" if vote == "up" else "👎"
    await query.edit_message_text(
        f"{emoji} شكراً على تقييمك!\n\n"
        f"📊 *{matiere}*\n"
        f"👍 {up}   👎 {dn}   ({total} تقييم)\n{bar}",
        parse_mode="Markdown"
    )


# ── /upload conversation (admin only) ─────────────────────────────────────────

async def upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 هذا الأمر للمشرف فقط.")
        return ConversationHandler.END

    await update.message.reply_text(
        "📤 *رفع ملف جديد*\n\nاختر المستوى:",
        reply_markup=niveau_keyboard(prefix="upniv"),
        parse_mode="Markdown"
    )
    return SELECT_NIVEAU


async def upload_select_niveau(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    niveau_key = query.data[len("upniv_"):]
    context.user_data["upload_niveau"] = niveau_key

    label, data = KEY_MAP[niveau_key]
    rows = [
        [InlineKeyboardButton(f"📖 {m}", callback_data=f"upsub_{niveau_key}_{i}")]
        for i, m in enumerate(data["matieres"])
    ]
    await query.edit_message_text(
        f"{label}\n\nاختر المادة:",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode="Markdown"
    )
    return SELECT_SUBJECT


async def upload_select_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    idx = int(parts[-1])
    niveau_key = "_".join(parts[1:-1])
    _, data = KEY_MAP[niveau_key]
    matiere = data["matieres"][idx]

    context.user_data["upload_niveau"] = niveau_key
    context.user_data["upload_matiere"] = matiere

    label, _ = KEY_MAP[niveau_key]
    await query.edit_message_text(
        f"✅ *{label}*\n📖 *{matiere}*\n\nأرسل الآن ملف PDF:",
        parse_mode="Markdown"
    )
    return RECEIVE_FILE


async def upload_receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("⚠️ أرسل ملف PDF من فضلك.")
        return RECEIVE_FILE

    doc = update.message.document
    if not doc.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("⚠️ الملف يجب أن يكون بصيغة PDF.")
        return RECEIVE_FILE

    niveau_key = context.user_data["upload_niveau"]
    matiere = context.user_data["upload_matiere"]

    # Store the Telegram file_id — no download needed, Telegram hosts the file
    add_file_entry(niveau_key, matiere, doc.file_name, doc.file_id)

    label, _ = KEY_MAP[niveau_key]
    await update.message.reply_text(
        f"✅ تم حفظ *{doc.file_name}* على خوادم تيليغرام ☁️\n📘 {label}\n📖 {matiere}",
        parse_mode="Markdown"
    )
    context.user_data.clear()
    return ConversationHandler.END


async def upload_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ تم إلغاء الرفع.")
    return ConversationHandler.END


# ── /list (admin only) ────────────────────────────────────────────────────────

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 هذا الأمر للمشرف فقط.")
        return

    file_ids = load_file_ids()
    lines = []

    for label, data in STRUCTURE.items():
        niveau_key = data["key"]
        section_lines = []
        for matiere in data["matieres"]:
            key = f"{niveau_key}|{matiere}"
            entries = file_ids.get(key, [])
            if entries:
                section_lines.append(f"  📖 *{matiere}* ({len(entries)} ملف)")
                for e in entries:
                    section_lines.append(f"    • {e['name']}")
        if section_lines:
            lines.append(f"\n{label}")
            lines.extend(section_lines)

    if not lines:
        await update.message.reply_text("📭 لا توجد ملفات مرفوعة بعد.")
    else:
        text = "\n".join(lines)
        if len(text) > 4000:
            for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, parse_mode="Markdown")


# ── /delete (admin only) ──────────────────────────────────────────────────────

async def delete_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 هذا الأمر للمشرف فقط.")
        return

    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "استخدم: `/delete <niveau_key> <المادة> <اسم_الملف.pdf>`\n"
            "مثال: `/delete S1_tronc Analyse 1 cours.pdf`\n\n"
            "المفاتيح المتاحة:\n" +
            "\n".join(f"  `{k}`" for k in KEY_MAP),
            parse_mode="Markdown"
        )
        return

    niveau_key = context.args[0]
    if niveau_key not in KEY_MAP:
        await update.message.reply_text(f"⚠️ المفتاح غير معروف: `{niveau_key}`", parse_mode="Markdown")
        return

    _, data = KEY_MAP[niveau_key]
    matiere = context.args[1]
    filename = " ".join(context.args[2:])

    if matiere not in data["matieres"]:
        await update.message.reply_text("⚠️ المادة غير موجودة في هذا المستوى.")
        return

    if remove_file_entry(niveau_key, matiere, filename):
        label, _ = KEY_MAP[niveau_key]
        await update.message.reply_text(
            f"🗑️ تم حذف *{filename}*\n📘 {label}\n📖 {matiere}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(f"⚠️ الملف غير موجود: {filename}")


# ── /stats (admin only) ───────────────────────────────────────────────────────

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 هذا الأمر للمشرف فقط.")
        return

    stats = load_stats()
    if not stats:
        await update.message.reply_text("📊 لا توجد إحصائيات بعد.")
        return

    total_downloads = sum(v["count"] for v in stats.values())
    sorted_entries = sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)

    lines = [f"📊 *إحصائيات التحميل*\n🔢 المجموع الكلي: *{total_downloads}* تحميل\n"]
    medals = ["🥇", "🥈", "🥉"]

    ratings = load_ratings()
    for i, (key, data) in enumerate(sorted_entries):
        niveau_key, matiere = key.split("|", 1)
        label = KEY_MAP[niveau_key][0] if niveau_key in KEY_MAP else niveau_key
        medal = medals[i] if i < 3 else "▫️"
        r = ratings.get(key, {"up": 0, "down": 0})
        rating_str = f"👍 {r['up']}  👎 {r['down']}" if (r["up"] + r["down"]) > 0 else "—"
        lines.append(
            f"{medal} *{matiere}*\n"
            f"   ↳ {label}\n"
            f"   ↳ 📥 {data['count']} تحميل  |  ⭐ {rating_str}  |  🕐 {data.get('last', '—')}"
        )

    lines.append("\n━━━━━━━━━━━━━━━━━━")
    lines.append("📈 *المواد التي لم تُحمَّل بعد:*")

    file_ids = load_file_ids()
    downloaded_keys = set(stats.keys())
    no_downloads = []
    for label, data in STRUCTURE.items():
        for matiere in data["matieres"]:
            key = f"{data['key']}|{matiere}"
            if key not in downloaded_keys and key in file_ids:
                no_downloads.append(f"  • {matiere}")

    if no_downloads:
        lines.extend(no_downloads)
    else:
        lines.append("  جميع المواد التي تحتوي ملفات تم تحميلها ✅")

    text = "\n".join(lines)
    if len(text) > 4000:
        for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            await update.message.reply_text(chunk, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


# ── /help ──────────────────────────────────────────────────────────────────────

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = update.effective_user.id == ADMIN_ID
    text = (
        "🎓 *بوت هندسة ميكانيكية - جامعة ابن خلدون تيارت*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "📚 *كيف تستخدم البوت؟*\n\n"
        "1️⃣ اضغط /start لعرض جميع المستويات\n"
        "2️⃣ اختر مستواك الدراسي\n"
        "3️⃣ اختر المادة التي تريدها\n"
        "4️⃣ سيُرسَل إليك الملف مباشرة 📥\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔍 *البحث السريع*\n\n"
        "`/search <كلمة>` — ابحث عن أي مادة بالاسم\n"
        "مثال: `/search mecanique`\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📂 *المستويات المتاحة*\n\n"
        "📗 السنة 1 — جذع مشترك\n"
        "📘 السنة 2 — Engineer / Bachelor GM / Bachelor EM\n"
        "📙 السنة 3 — Bachelor CM / Énergétique / Maintenance / Engineer GM\n"
        "📕 السنة 4/5 — Master CM / Énergétique / Maintenance\n"
    )
    if is_admin:
        text += (
            "\n━━━━━━━━━━━━━━━━━━\n"
            "⚙️ *أوامر المشرف*\n\n"
            "/upload — رفع ملف PDF جديد\n"
            "/list — عرض جميع الملفات المرفوعة\n"
            "/delete `<key> <مادة> <ملف.pdf>` — حذف ملف\n"
            "/stats — إحصائيات التحميل\n"
            "/backup — نسخة احتياطية كاملة لجميع البيانات\n"
            "/restore — استعادة البيانات من ملف JSON\n"
            "/broadcast `<رسالة>` — إرسال إشعار للجميع\n"
            "/cancel — إلغاء أي عملية جارية\n"
        )
    await update.message.reply_text(text, parse_mode="Markdown")


# ── /search ────────────────────────────────────────────────────────────────────

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🔍 استخدم: `/search <كلمة البحث>`\n"
            "مثال: `/search thermodynamique`",
            parse_mode="Markdown"
        )
        return

    query_text = " ".join(context.args).lower()
    file_ids = load_file_ids()
    results = []

    for label, data in STRUCTURE.items():
        niveau_key = data["key"]
        for matiere in data["matieres"]:
            if query_text in matiere.lower():
                key = f"{niveau_key}|{matiere}"
                entries = file_ids.get(key, [])
                status = f"📂 {len(entries)} ملف" if entries else "📭 لا توجد ملفات بعد"
                results.append(f"📖 *{matiere}*\n   ↳ {label}\n   ↳ {status}")

    if not results:
        await update.message.reply_text(
            f"🔍 لا توجد نتائج لـ «{' '.join(context.args)}»\n\n"
            "تأكد من الكتابة الصحيحة أو جرب كلمة أخرى."
        )
        return

    header = f"🔍 نتائج البحث عن «*{' '.join(context.args)}*» — {len(results)} نتيجة\n"
    text = header + "\n\n" + "\n\n".join(results)

    if len(text) > 4000:
        for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            await update.message.reply_text(chunk, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")


# ── /backup (admin only) ──────────────────────────────────────────────────────

async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 هذا الأمر للمشرف فقط.")
        return

    files_sent = 0
    for path, label in [
        (FILE_IDS_PATH, "📁 file_ids.json — فهرس الملفات"),
        (STATS_PATH,    "📊 stats.json — إحصائيات التحميل"),
        (USERS_PATH,    "👥 users.json — قائمة المستخدمين"),
        (RATINGS_PATH,  "⭐ ratings.json — التقييمات"),
    ]:
        if os.path.exists(path):
            with open(path, "rb") as f:
                await update.message.reply_document(
                    document=f,
                    filename=os.path.basename(path),
                    caption=label
                )
            files_sent += 1

    if files_sent == 0:
        await update.message.reply_text("📭 لا توجد بيانات للنسخ الاحتياطي بعد.")
    else:
        await update.message.reply_text(
            f"✅ *نسخة احتياطية كاملة*\n\n"
            f"تم إرسال *{files_sent}* ملف.\n\n"
            "💡 لاستعادة البيانات: ضع هذه الملفات في مجلد `DATA_DIR` على السيرفر.",
            parse_mode="Markdown"
        )


# ── /restore conversation (admin only) ───────────────────────────────────────

ALLOWED_RESTORE_FILES = {
    "file_ids.json": FILE_IDS_PATH,
    "stats.json":    STATS_PATH,
    "users.json":    USERS_PATH,
    "ratings.json":  RATINGS_PATH,
}

async def restore_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 هذا الأمر للمشرف فقط.")
        return ConversationHandler.END

    await update.message.reply_text(
        "♻️ *استعادة البيانات*\n\n"
        "أرسل ملف JSON الذي تريد استعادته:\n\n"
        "• `file_ids.json` — فهرس الملفات\n"
        "• `stats.json` — الإحصائيات\n"
        "• `users.json` — المستخدمون\n"
        "• `ratings.json` — التقييمات\n\n"
        "⚠️ سيتم استبدال البيانات الحالية. أرسل /cancel للإلغاء.",
        parse_mode="Markdown"
    )
    return RECEIVE_RESTORE


async def restore_receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("⚠️ أرسل ملف JSON من فضلك، أو /cancel للإلغاء.")
        return RECEIVE_RESTORE

    doc = update.message.document
    filename = doc.file_name

    if filename not in ALLOWED_RESTORE_FILES:
        await update.message.reply_text(
            f"⚠️ اسم الملف غير معروف: `{filename}`\n\n"
            "الأسماء المقبولة:\n" +
            "\n".join(f"  • `{n}`" for n in ALLOWED_RESTORE_FILES),
            parse_mode="Markdown"
        )
        return RECEIVE_RESTORE

    tg_file = await doc.get_file()
    raw = await tg_file.download_as_bytearray()

    try:
        data = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        await update.message.reply_text("⚠️ الملف تالف أو ليس JSON صحيحاً. حاول مرة أخرى.")
        return RECEIVE_RESTORE

    dest = ALLOWED_RESTORE_FILES[filename]
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    count = len(data) if isinstance(data, dict) else "—"
    await update.message.reply_text(
        f"✅ *تمت الاستعادة بنجاح*\n\n"
        f"📄 الملف: `{filename}`\n"
        f"📦 عدد الإدخالات: *{count}*",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def restore_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم إلغاء الاستعادة.")
    return ConversationHandler.END


# ── /broadcast (admin only) ───────────────────────────────────────────────────

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 هذا الأمر للمشرف فقط.")
        return

    if not context.args:
        await update.message.reply_text(
            "استخدم: `/broadcast <رسالتك هنا>`",
            parse_mode="Markdown"
        )
        return

    message_text = " ".join(context.args)
    users = load_users()

    if not users:
        await update.message.reply_text("📭 لا يوجد مستخدمون مسجلون بعد.")
        return

    total = len(users)
    sent = 0
    failed = 0

    status_msg = await update.message.reply_text(
        f"📡 جاري الإرسال إلى *{total}* مستخدم...", parse_mode="Markdown"
    )

    broadcast_text = f"📢 *إشعار من الإدارة*\n\n{message_text}"

    for uid in users:
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text=broadcast_text,
                parse_mode="Markdown"
            )
            sent += 1
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"✅ *اكتمل الإرسال*\n\n"
        f"📨 أُرسل إلى: *{sent}* مستخدم\n"
        f"❌ فشل: *{failed}* مستخدم",
        parse_mode="Markdown"
    )


# ── app setup ──────────────────────────────────────────────────────────────────

upload_conv = ConversationHandler(
    entry_points=[CommandHandler("upload", upload_start)],
    states={
        SELECT_NIVEAU: [CallbackQueryHandler(upload_select_niveau, pattern="^upniv_")],
        SELECT_SUBJECT: [CallbackQueryHandler(upload_select_subject, pattern="^upsub_")],
        RECEIVE_FILE: [MessageHandler(filters.Document.ALL, upload_receive_file)],
    },
    fallbacks=[CommandHandler("cancel", upload_cancel)],
    per_user=True,
    per_message=False,
)

restore_conv = ConversationHandler(
    entry_points=[CommandHandler("restore", restore_start)],
    states={
        RECEIVE_RESTORE: [MessageHandler(filters.Document.ALL, restore_receive_file)],
    },
    fallbacks=[CommandHandler("cancel", restore_cancel)],
    per_user=True,
    per_message=False,
)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list", list_files))
app.add_handler(CommandHandler("delete", delete_file))
app.add_handler(CommandHandler("stats", show_stats))
app.add_handler(CommandHandler("backup", backup))
app.add_handler(restore_conv)
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("search", search))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(upload_conv)
app.add_handler(CallbackQueryHandler(show_matieres, pattern="^niveau_"))
app.add_handler(CallbackQueryHandler(send_file, pattern="^mat_"))
app.add_handler(CallbackQueryHandler(back_start, pattern="^back_start"))
app.add_handler(CallbackQueryHandler(handle_rating, pattern="^rate_"))

print(f"✅ البوت شغّال! — DATA_DIR: {DATA_DIR}")
app.run_polling()
