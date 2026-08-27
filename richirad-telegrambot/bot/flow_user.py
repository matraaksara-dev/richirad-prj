"""
User flow — form pendaftaran 5 langkah dengan ConversationHandler.
State machine: DISCLAIMER → NAME → DOMISILI → LEVEL → MOTIVASI → WA → REVIEW
"""
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

import db
import messages as m

# State
DISCLAIMER, NAME, DOMISILI, LEVEL, MOTIVASI, WA, REVIEW = range(7)

# Callback data (user flow)
CB_DAFTAR = "u:daftar"
CB_SETUJU = "u:setuju"
CB_BATAL = "u:batal"
CB_MALANG = "u:malang"
CB_LUAR = "u:luar"
CB_PEMULA = "u:pemula"
CB_INTER = "u:inter"
CB_LEWATI = "u:lewati"
CB_KIRIM = "u:kirim"
CB_EDIT = "u:edit"
CB_APA_VIP = "u:apavip"
CB_FAQ = "u:faq"


# ── Handler umum /start /status /faq /privacy ───────────────────────────────

async def cmd_start(update: Update, context):
    user = update.effective_user
    existing = db.get_by_telegram_id(user.id)

    # Deep link source: /start SOURCE
    args = context.args
    source = args[0] if args else None

    text = m.WELCOME
    keyboard = [
        [InlineKeyboardButton("📝 Daftar VIP", callback_data=CB_DAFTAR)],
        [
            InlineKeyboardButton("ℹ️ Apa itu VIP?", callback_data=CB_APA_VIP),
            InlineKeyboardButton("❓ FAQ", callback_data=CB_FAQ),
        ],
    ]
    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard)
    )

    if existing and existing["status"] in ("pending", "approved", "waiting_payment", "paid", "invited", "active"):
        await update.message.reply_text(
            f"ℹ️ Kamu sudah terdaftar (ID #{existing['id']}).\n\n{m.status_text(existing)}",
            parse_mode="HTML",
        )
    elif source:
        context.user_data["source"] = source


async def cmd_status(update: Update, context):
    reg = db.get_by_telegram_id(update.effective_user.id)
    if not reg:
        await update.message.reply_text(
            "Kamu belum terdaftar. Ketik /start untuk memulai pendaftaran."
        )
        return
    await update.message.reply_text(m.status_text(reg), parse_mode="HTML")


async def cmd_faq(update: Update, context):
    await update.message.reply_text(m.FAQ, parse_mode="HTML")


async def cmd_privacy(update: Update, context):
    await update.message.reply_text(m.PRIVACY, parse_mode="HTML")


# ── Menu callbacks (luar conversation) ──────────────────────────────────────

async def on_menu_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == CB_APA_VIP:
        await query.message.reply_text(
            "VIP Education adalah program edukasi intensif trading futures & spot "
            "hingga 3 bulan, dengan struktur belajar, praktik, dan komunitas.\n\n"
            "Bukan signal. Bukan jaminan profit. Trading berisiko tinggi.\n\n"
            "Ketik /start lalu pilih 'Daftar VIP' untuk mendaftar."
        )
    elif data == CB_FAQ:
        await query.message.reply_text(m.FAQ, parse_mode="HTML")


# ── Conversation: daftar ────────────────────────────────────────────────────

async def start_registration(update: Update, context):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    existing = db.get_by_telegram_id(user.id)
    if existing and existing["status"] in (
        "pending", "approved", "waiting_payment", "paid", "invited", "active",
    ):
        await query.message.reply_text(
            f"ℹ️ Kamu sudah terdaftar (ID #{existing['id']}).\n\n{m.status_text(existing)}",
            parse_mode="HTML",
        )
        return ConversationHandler.END

    context.user_data["form"] = {}
    keyboard = [[InlineKeyboardButton("✅ Saya paham & setuju", callback_data=CB_SETUJU)]]
    await query.message.reply_text(
        m.DISCLAIMER,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return DISCLAIMER


async def disclaimer_setuju(update: Update, context):
    query = update.callback_query
    await query.answer()
    form = context.user_data.setdefault("form", {})
    form["disclaimer_accepted"] = True
    await query.message.reply_text(m.Q_NAME, parse_mode="HTML")
    return NAME


async def ask_name(update: Update, context):
    text = update.message.text.strip()
    if len(text) < 2:
        await update.message.reply_text("Nama terlalu pendek. Ketik nama lengkap kamu:")
        return NAME
    context.user_data["form"]["full_name"] = text
    keyboard = [
        [
            InlineKeyboardButton("📍 Malang", callback_data=CB_MALANG),
            InlineKeyboardButton("🏙️ Luar Malang", callback_data=CB_LUAR),
        ]
    ]
    await update.message.reply_text(
        m.Q_DOMISILI, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return DOMISILI


async def ask_domisili(update: Update, context):
    query = update.callback_query
    await query.answer()
    context.user_data["form"]["domisili"] = "Malang" if query.data == CB_MALANG else "Luar Malang"
    keyboard = [
        [
            InlineKeyboardButton("🌱 Pemula", callback_data=CB_PEMULA),
            InlineKeyboardButton("📈 Intermediate", callback_data=CB_INTER),
        ]
    ]
    await query.message.reply_text(
        m.Q_LEVEL, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return LEVEL


async def ask_level(update: Update, context):
    query = update.callback_query
    await query.answer()
    context.user_data["form"]["experience_level"] = (
        "Pemula" if query.data == CB_PEMULA else "Intermediate"
    )
    keyboard = [[InlineKeyboardButton("⏭️ Lewati", callback_data=CB_LEWATI)]]
    await query.message.reply_text(
        m.Q_MOTIVASI, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MOTIVASI


async def ask_motivasi(update: Update, context):
    text = update.message.text.strip()
    if len(text) > 500:
        text = text[:500]
    context.user_data["form"]["motivation"] = text
    await update.message.reply_text(m.Q_WA, parse_mode="HTML")
    return WA


async def skip_motivasi(update: Update, context):
    query = update.callback_query
    await query.answer()
    context.user_data["form"]["motivation"] = ""
    await query.message.reply_text(m.Q_WA, parse_mode="HTML")
    return WA


async def ask_wa(update: Update, context):
    text = update.message.text.strip()
    digits = re.sub(r"\D", "", text)
    if len(digits) < 9:
        await update.message.reply_text(
            "Nomor WhatsApp tidak valid. Ketik dengan format 08xxxxxxxxxx:"
        )
        return WA
    context.user_data["form"]["contact_wa"] = text
    form = context.user_data["form"]
    keyboard = [
        [
            InlineKeyboardButton("✅ Kirim", callback_data=CB_KIRIM),
            InlineKeyboardButton("✏️ Edit", callback_data=CB_EDIT),
        ],
        [InlineKeyboardButton("🚫 Batal", callback_data=CB_BATAL)],
    ]
    await update.message.reply_text(
        m.review_text(form), parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return REVIEW


async def submit(update: Update, context):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    form = context.user_data.get("form", {})

    # Guard: sudah terdaftar (race condition / double submit)
    existing = db.get_by_telegram_id(user.id)
    if existing and existing["status"] in (
        "pending", "approved", "waiting_payment", "paid", "invited", "active",
    ):
        await query.message.reply_text(
            f"ℹ️ Kamu sudah terdaftar (ID #{existing['id']}).\n\n{m.status_text(existing)}",
            parse_mode="HTML",
        )
        context.user_data.pop("form", None)
        return ConversationHandler.END

    reg_id = db.create_registration({
        "telegram_id": user.id,
        "username": user.username or "",
        "full_name": form.get("full_name", ""),
        "domisili": form.get("domisili", ""),
        "experience_level": form.get("experience_level", ""),
        "motivation": form.get("motivation", ""),
        "contact_wa": form.get("contact_wa", ""),
        "source": context.user_data.get("source") or "organic",
    })
    reg = db.get_registration(reg_id)
    context.user_data.pop("form", None)

    # Notifikasi ke grup admin
    from admin_panel import send_admin_notification
    await send_admin_notification(context, reg)

    keyboard = [[InlineKeyboardButton("💬 Hubungi Admin", url="t.me/richiradvip_bot")]]
    await query.message.reply_text(
        m.SUBMIT_CONFIRM, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END


async def edit_form(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(m.Q_NAME, parse_mode="HTML")
    return NAME


async def cancel(update: Update, context):
    context.user_data.pop("form", None)
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("Pendaftaran dibatalkan.")
    else:
        await update.message.reply_text("Pendaftaran dibatalkan.")
    return ConversationHandler.END


def conv_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(start_registration, pattern=f"^{CB_DAFTAR}$")],
        states={
            DISCLAIMER: [
                CallbackQueryHandler(disclaimer_setuju, pattern=f"^{CB_SETUJU}$"),
                CallbackQueryHandler(cancel, pattern=f"^{CB_BATAL}$"),
            ],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            DOMISILI: [
                CallbackQueryHandler(ask_domisili, pattern=f"^({CB_MALANG}|{CB_LUAR})$")
            ],
            LEVEL: [
                CallbackQueryHandler(ask_level, pattern=f"^({CB_PEMULA}|{CB_INTER})$")
            ],
            MOTIVASI: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_motivasi),
                CallbackQueryHandler(skip_motivasi, pattern=f"^{CB_LEWATI}$"),
            ],
            WA: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_wa)],
            REVIEW: [
                CallbackQueryHandler(submit, pattern=f"^{CB_KIRIM}$"),
                CallbackQueryHandler(edit_form, pattern=f"^{CB_EDIT}$"),
                CallbackQueryHandler(cancel, pattern=f"^{CB_BATAL}$"),
            ],
        },
        fallbacks=[CommandHandler("batal", cancel)],
        allow_reentry=True,
    )