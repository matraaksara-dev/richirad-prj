"""
Payment proof — auto-forward bukti transfer dari calon member yang sudah
menerima QRIS (status waiting_payment) ke 2 grup admin:

- Grup A (approval, Admin 1): media + note + tombol [💳 Mark as Paid]
- Grup B (query, Admin 1 & 2): media + note "dalam proses approval" (tanpa tombol)
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError

import db
import messages as m

# Status yang mengizinkan user mengirim bukti transfer
PROOF_STATUSES = ("waiting_payment", "paid")


async def on_proof_message(update: Update, context):
    """Terima foto/dokumen/teks bukti transfer → forward ke Grup A & B."""
    user = update.effective_user
    if user is None:
        return
    reg = db.get_by_telegram_id(user.id)
    if not reg:
        return
    if reg["status"] not in PROOF_STATUSES:
        return

    from admin_panel import get_admin_group_id, get_query_group_id

    group_a = get_admin_group_id()
    group_b = get_query_group_id()
    if not group_a and not group_b:
        await update.message.reply_text(
            "Grup admin belum diset. Hubungi admin langsung."
        )
        return

    msg = update.effective_message

    # Forward media asli ke semua grup admin
    for gid in (g for g in (group_a, group_b) if g):
        try:
            await msg.forward(chat_id=gid)
        except TelegramError as e:
            print(f"[proof] Gagal forward ke grup {gid}: {e}")
            await update.message.reply_text(
                "⚠️ Gagal mengirim bukti. Coba kirim ulang atau hubungi admin."
            )
            return

    # Grup A (approval): note + tombol Mark as Paid (Admin 1)
    if group_a:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Mark as Paid", callback_data=f"a:pay:{reg['id']}")],
            [
                InlineKeyboardButton("💬 Hubungi", callback_data=f"a:contact:{reg['telegram_id']}"),
                InlineKeyboardButton("📋 Detail", callback_data=f"a:detail:{reg['id']}"),
            ],
        ])
        try:
            await context.bot.send_message(
                group_a,
                m.proof_note(reg, status_label="Verifikasi & klik Mark as Paid"),
                parse_mode=ParseMode.HTML,
                reply_markup=kb,
            )
        except TelegramError as e:
            print(f"[proof] Gagal kirim note ke Grup A: {e}")

    # Grup B (query): note info, tanpa tombol approval
    if group_b:
        try:
            await context.bot.send_message(
                group_b,
                m.proof_note(reg, status_label="Dalam proses approval"),
                parse_mode=ParseMode.HTML,
            )
        except TelegramError as e:
            print(f"[proof] Gagal kirim note ke Grup B: {e}")

    await update.message.reply_text(
        "✅ <b>Bukti transfer diterima.</b>\n\n"
        "Bukti kamu sudah diteruskan ke admin untuk verifikasi. "
        "Admin akan memproses dan memasukkan kamu ke grup VIP setelah konfirmasi.",
        parse_mode=ParseMode.HTML,
    )