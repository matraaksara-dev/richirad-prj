"""
QRIS flow — alur pembayaran via QRIS.

- Tombol "Kirim QRIS" (hanya Admin 2) di grup B → bot siap menerima foto QRIS.
- Foto QRIS yang diupload admin di grup → bot kirim ke member + status waiting_payment.
- "Kirim Ulang QRIS" (admin) & /qris (member) → kirim ulang QRIS tersimpan.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError

import db
import messages as m

# chat_id -> reg_id : menunggu admin mengupload foto QRIS di grup tsb
_pending_qris: dict[int, int] = {}

CB_QRIS = "a:qris"           # a:qris:{reg_id}
CB_QRIS_RESEND = "a:qris2"   # a:qris2:{reg_id}


async def on_qris_button(update: Update, context):
    """Admin 2 klik 'Kirim QRIS' di grup B → siapkan capture foto QRIS.

    Menangani ChatMigrated: jika grup sudah migrasi ke supergroup, pakai id baru.
    """
    query = update.callback_query
    admin = query.from_user
    if not db.is_admin2(admin.id):
        await query.answer("Hanya Admin 2 yang bisa mengirim QRIS.", show_alert=True)
        return
    try:
        reg_id = int(query.data.split(":")[2])
    except (ValueError, IndexError):
        await query.answer("Callback tidak valid", show_alert=True)
        return
    reg = db.get_registration(reg_id)
    if not reg or reg["status"] != "pending":
        await query.answer("Status sudah berubah.", show_alert=True)
        return

    chat_id = query.message.chat_id
    _pending_qris[chat_id] = reg_id
    prompt = (
        f"📤 Silakan kirim <b>foto QRIS</b> untuk {reg['full_name']} (#{reg_id}) di grup ini.\n"
        "Foto QRIS pertama yang kamu kirim akan langsung diteruskan ke member.\n\n"
        "💡 Atau balas (reply) pesan notifikasi pendaftar ini dengan foto QRIS."
    )
    try:
        await query.message.reply_text(prompt, parse_mode=ParseMode.HTML)
    except TelegramError as e:
        migrate_to = getattr(e, "migrate_to_chat_id", None)
        if migrate_to:
            _pending_qris.pop(chat_id, None)
            _pending_qris[migrate_to] = reg_id
            try:
                await context.bot.send_message(migrate_to, prompt, parse_mode=ParseMode.HTML)
            except TelegramError as e2:
                print(f"[qris] Gagal kirim prompt ke {migrate_to}: {e2}")
        else:
            print(f"[qris] Gagal reply prompt: {e}")
    try:
        await query.answer("Silakan unggah foto QRIS.")
    except TelegramError as e:
        print(f"[qris] Gagal answer callback: {e}")


def _find_reg_by_admin_message(message_id: int) -> int | None:
    """Cari registrasi yang pesan notifikasinya (grup A atau B) = message_id."""
    for r in db.list_registrations():
        if r.get("adminb_message_id") == message_id or r.get("admin_message_id") == message_id:
            return r["id"]
    return None


async def on_qris_photo(update: Update, context):
    """Foto QRIS yang diupload admin di grup (chat yang punya pending QRIS).

    Dua jalur:
    1. Ada pending (tombol 'Kirim QRIS' sudah diklik di chat ini).
    2. Foto dikirim sebagai REPLY ke pesan notifikasi pendaftar → dicocokkan
       via adminb_message_id / admin_message_id (tahan terhadap migrasi grup).
    """
    chat = update.effective_chat
    if chat is None or chat.type not in ("group", "supergroup"):
        return
    msg = update.message

    reg_id = _pending_qris.get(chat.id)
    if reg_id is None and msg.reply_to_message:
        reg_id = _find_reg_by_admin_message(msg.reply_to_message.message_id)

    if reg_id is None:
        return
    _pending_qris.pop(chat.id, None)
    reg = db.get_registration(reg_id)
    if not reg:
        return

    # Ambil file_id dari foto atau dokumen
    msg = update.message
    if msg.photo:
        file_id = msg.photo[-1].file_id
        send_fn = context.bot.send_photo
    elif msg.document:
        file_id = msg.document.file_id
        send_fn = context.bot.send_document
    else:
        return

    db.update_registration(
        reg_id,
        status="waiting_payment",
        qris_file_id=file_id,
        qris_sent_at=db._now_utc(),
    )

    # Kirim QRIS + instruksi ke member
    try:
        await send_fn(
            chat_id=reg["telegram_id"],
            **({"photo": file_id} if msg.photo else {"document": file_id}),
            caption=m.QRIS_MEMBER_MSG,
            parse_mode=ParseMode.HTML,
        )
    except TelegramError as e:
        print(f"[qris] Gagal kirim QRIS ke {reg['telegram_id']}: {e}")

    # Notif grup B: QRIS terkirim
    from admin_panel import get_query_group_id
    qg = get_query_group_id()
    if qg:
        try:
            await context.bot.send_message(qg, m.qris_sent_notif(reg))
        except TelegramError as e:
            print(f"[qris] Gagal notif grup B: {e}")

    # Edit notifikasi di kedua grup → status waiting_payment
    reg = db.get_registration(reg_id)
    kb_a = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Hubungi", callback_data=f"a:contact:{reg['telegram_id']}"),
            InlineKeyboardButton("📋 Detail", callback_data=f"a:detail:{reg_id}"),
        ],
    ])
    kb_b = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Kirim Ulang QRIS", callback_data=f"{CB_QRIS_RESEND}:{reg_id}")],
        [
            InlineKeyboardButton("💬 Hubungi", callback_data=f"a:contact:{reg['telegram_id']}"),
            InlineKeyboardButton("📋 Detail", callback_data=f"a:detail:{reg_id}"),
        ],
    ])
    from admin_panel import _edit_both_messages
    await _edit_both_messages(context, reg, m.admin_qris_sent_text(reg), kb_a, kb_b)


async def on_qris_resend(update: Update, context):
    """Admin (1/2) klik 'Kirim Ulang QRIS' → kirim ulang QRIS tersimpan."""
    query = update.callback_query
    admin = query.from_user
    if not (db.is_admin1(admin.id) or db.is_admin2(admin.id)):
        await query.answer("Tidak diizinkan", show_alert=True)
        return
    try:
        reg_id = int(query.data.split(":")[2])
    except (ValueError, IndexError):
        await query.answer("Callback tidak valid", show_alert=True)
        return
    reg = db.get_registration(reg_id)
    if not reg or not reg.get("qris_file_id"):
        await query.answer("Belum ada QRIS tersimpan.", show_alert=True)
        return
    try:
        await context.bot.send_photo(
            chat_id=reg["telegram_id"],
            photo=reg["qris_file_id"],
            caption=m.QRIS_MEMBER_RESEND,
            parse_mode=ParseMode.HTML,
        )
        await query.answer("QRIS dikirim ulang ke member.")
    except TelegramError as e:
        print(f"[qris] Gagal kirim ulang: {e}")
        await query.answer("Gagal kirim ulang.", show_alert=True)


async def cmd_qris(update: Update, context):
    """Member minta QRIS ulang via chatbot."""
    user = update.effective_user
    reg = db.get_by_telegram_id(user.id)
    if not reg:
        await update.message.reply_text("Kamu belum terdaftar. Ketik /start.")
        return
    if reg["status"] != "waiting_payment":
        await update.message.reply_text(
            "QRIS hanya dikirim ulang saat menunggu pembayaran. "
            "Ketik /status untuk cek status."
        )
        return
    if not reg.get("qris_file_id"):
        await update.message.reply_text("QRIS belum diterima admin. Tunggu sebentar.")
        return
    try:
        await update.message.reply_photo(
            photo=reg["qris_file_id"],
            caption=m.QRIS_MEMBER_MSG,
            parse_mode=ParseMode.HTML,
        )
    except TelegramError as e:
        print(f"[qris] /qris gagal: {e}")
        await update.message.reply_text("Gagal mengirim QRIS. Hubungi admin.")