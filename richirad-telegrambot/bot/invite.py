"""
Invite link management — buat link 1x pakai, revoke, tracking join grup VIP.
Event chat_member untuk mendeteksi user join dan mencatat masa edukasi 3 bulan.
"""
import time
from datetime import datetime, timezone, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import TelegramError

import db
import messages as m


def _fmt_db(dt: datetime) -> str:
    """Datetime → string UTC untuk DB."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


async def create_vip_invite(context, chat_id: int) -> tuple[str, datetime]:
    """Buat invite link 1x pakai, expire 48 jam."""
    expire_dt = datetime.now(timezone.utc) + timedelta(hours=48)
    expire_ts = int(expire_dt.timestamp())
    link = await context.bot.create_chat_invite_link(
        chat_id=chat_id, member_limit=1, expire_date=expire_ts,
    )
    return link.invite_link, expire_dt


async def add_member_directly(context, vip_group: int, user_id: int) -> bool:
    """Tambahkan member langsung ke grup VIP via raw API addChatMember.

    PTB v21 tidak punya method add_chat_member, jadi dipanggil via bot._post.
    Return True jika sukses. Fallback ke invite link jika gagal (limit/blokir).
    """
    try:
        await context.bot._post(
            "addChatMember", {"chat_id": vip_group, "user_id": user_id}
        )
        return True
    except TelegramError as e:
        print(f"[invite] addChatMember gagal untuk {user_id}: {e}")
        return False


async def on_chat_member(update: Update, context):
    """Deteksi user join grup VIP → catat joined_at + education_end.
    Idempotent: jika joined_at sudah terisi (mark_paid langsung set untuk
    addChatMember), skip untuk hindari duplikat welcome."""
    cm = update.chat_member
    chat = cm.chat
    new = cm.new_chat_member
    old = cm.old_chat_member

    if new.status not in ("member", "administrator", "creator"):
        return
    if old.status == new.status:
        return

    user = new.user
    reg = db.get_by_telegram_id(user.id)
    if not reg:
        return
    if reg["status"] not in ("paid", "invited"):
        return
    # Idempotency: sudah diproses mark_paid untuk direct-add, skip
    if reg.get("joined_at"):
        return

    await record_join(context, reg, chat.id)


async def record_join(context, reg: dict, chat_id: int):
    """Catat join user ke grup VIP → active + education_end + edit 2 pesan."""
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=90)

    db.update_registration(
        reg["id"],
        status="active",
        joined_at=_fmt_db(now),
        education_end=_fmt_db(end),
        invite_used_at=_fmt_db(now),
    )
    db.log_admin_action(reg["id"], 0, "joined", "User join grup VIP")

    reg = db.get_registration(reg["id"])

    # Welcome ke user
    try:
        await context.bot.send_message(
            reg["telegram_id"],
            m.WELCOME_JOIN.format(
                start=reg["joined_at"] or "—",
                end=reg["education_end"] or "—",
            ),
            parse_mode=ParseMode.HTML,
        )
    except TelegramError as e:
        print(f"[join] Gagal kirim welcome ke {reg['telegram_id']}: {e}")

    # Edit pesan notifikasi di Grup A & B
    from admin_panel import _edit_both_messages
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Hubungi", callback_data=f"a:contact:{reg['telegram_id']}"),
            InlineKeyboardButton("📋 Detail", callback_data=f"a:detail:{reg['id']}"),
        ],
    ])
    await _edit_both_messages(context, reg, m.admin_joined_text(reg), kb, kb)

    # Notif singkat ke grup admin
    from admin_panel import get_admin_group_id
    admin_group = get_admin_group_id()
    if admin_group:
        try:
            await context.bot.send_message(
                admin_group,
                f"✅ {reg['full_name']} telah join grup VIP. "
                f"Masa edukasi: 90 hari (s.d. {reg['education_end']}).",
            )
        except TelegramError:
            pass


async def on_my_chat_member(update: Update, context):
    """Bot ditambahkan/dihapus dari grup — log chat_id + info."""
    cm = update.my_chat_member
    chat = cm.chat
    new = cm.new_chat_member
    status = new.status

    if status in ("member", "administrator", "creator"):
        print(f"[my_chat_member] Bot ditambahkan ke grup: {chat.id} ({chat.title})")
        try:
            await context.bot.send_message(
                chat.id,
                f"🤖 Bot aktif di grup ini.\n\n"
                f"Chat ID: <code>{chat.id}</code>\n\n"
                f"Gunakan perintah:\n"
                f"• <b>/setvip</b> — jadikan grup ini sebagai grup VIP (invite member)\n"
                f"• <b>/setgroup</b> — jadikan grup ini sebagai grup admin (notifikasi)",
                parse_mode=ParseMode.HTML,
            )
        except TelegramError:
            pass
    elif status in ("left", "kicked"):
        print(f"[my_chat_member] Bot dihapus dari grup: {chat.id} ({chat.title})")