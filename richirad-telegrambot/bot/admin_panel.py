"""
Admin panel — Grup A (approval) & Grup B (query), Mark Paid = approve,
query admin, dan setup grup.
"""
from datetime import datetime, timezone, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError

import db
import messages as m
from invite import create_vip_invite, add_member_directly

# ── Const ───────────────────────────────────────────────────────────────────

ACTIVE_STATUSES = (
    "pending", "waiting_payment", "paid", "invited", "active",
)


def get_admin_group_id() -> int | None:
    """Grup A (approval) — Admin 1 saja."""
    val = db.get_setting("ADMIN_GROUP_ID")
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        return None


def get_query_group_id() -> int | None:
    """Grup B (query) — Admin 1 & 2."""
    val = db.get_setting("QUERY_GROUP_ID")
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        return None


def get_vip_group_id() -> int | None:
    val = db.get_setting("VIP_GROUP_ID")
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        return None


# ── Guard ───────────────────────────────────────────────────────────────────

def _guard_full(update: Update) -> int | None:
    """Admin 1 (query + approval)."""
    user = update.effective_user
    if user is None:
        return None
    if db.can_approve(user.id):
        return user.id
    return None


def _guard_query(update: Update) -> int | None:
    """Admin 1 atau Admin 2 (bisa lihat data)."""
    user = update.effective_user
    if user is None:
        return None
    if db.can_query(user.id):
        return user.id
    return None


async def _denied(update: Update, context):
    if update.callback_query:
        await update.callback_query.answer("Tidak diizinkan", show_alert=True)
    elif update.message:
        await update.message.reply_text("⛔ Perintah ini hanya untuk admin.")


def _admin_name(update: Update) -> str:
    u = update.effective_user
    name = u.full_name or ""
    return f"{name} (@{u.username})" if u.username else (name or str(u.id))


# ── Notifikasi pendaftar baru ke Grup A & B ────────────────────────────────

async def send_admin_notification(context, reg: dict) -> bool:
    group_a = get_admin_group_id()
    group_b = get_query_group_id()
    if not group_a and not group_b:
        print(f"[admin-panel] Belum ada grup admin di-set — registrasi #{reg['id']} "
              f"tidak dinotifikasi. Jalankan /setgroup & /setquerygroup.")
        return False

    text = m.admin_notification(reg)
    tid = reg["telegram_id"]
    rid = reg["id"]

    # Grup A (approval): tanpa tombol QRIS
    kb_a = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Hubungi", callback_data=f"a:contact:{tid}"),
            InlineKeyboardButton("📋 Detail", callback_data=f"a:detail:{rid}"),
        ],
    ])
    # Grup B (query): dengan tombol Kirim QRIS (Admin 2)
    kb_b = InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Kirim QRIS", callback_data=f"a:qris:{rid}")],
        [
            InlineKeyboardButton("💬 Hubungi", callback_data=f"a:contact:{tid}"),
            InlineKeyboardButton("📋 Detail", callback_data=f"a:detail:{rid}"),
        ],
    ])

    msg_a = msg_b = None
    if group_a:
        try:
            msg_a = await context.bot.send_message(group_a, text, parse_mode=ParseMode.HTML, reply_markup=kb_a)
        except TelegramError as e:
            print(f"[admin-panel] Gagal kirim ke Grup A ({group_a}): {e}")
    if group_b:
        try:
            msg_b = await context.bot.send_message(group_b, text, parse_mode=ParseMode.HTML, reply_markup=kb_b)
        except TelegramError as e:
            print(f"[admin-panel] Gagal kirim ke Grup B ({group_b}): {e}")

    db.update_registration(
        reg["id"],
        admin_chat_id=group_a,
        admin_message_id=msg_a.message_id if msg_a else None,
        adminb_chat_id=group_b,
        adminb_message_id=msg_b.message_id if msg_b else None,
    )
    return bool(msg_a or msg_b)


# ── Edit pesan notifikasi di Grup A & B ────────────────────────────────────

async def _edit_both_messages(context, reg: dict, text: str, kb_a=None, kb_b=None):
    if reg.get("admin_chat_id") and reg.get("admin_message_id"):
        try:
            await context.bot.edit_message_text(
                text, chat_id=reg["admin_chat_id"], message_id=reg["admin_message_id"],
                parse_mode=ParseMode.HTML, reply_markup=kb_a,
            )
        except TelegramError as e:
            print(f"[admin-panel] Gagal edit Grup A: {e}")
    if reg.get("adminb_chat_id") and reg.get("adminb_message_id"):
        try:
            await context.bot.edit_message_text(
                text, chat_id=reg["adminb_chat_id"], message_id=reg["adminb_message_id"],
                parse_mode=ParseMode.HTML, reply_markup=kb_b,
            )
        except TelegramError as e:
            print(f"[admin-panel] Gagal edit Grup B: {e}")


# ── Callback router (a:pay, a:contact, a:detail) ────────────────────────────
# (a:qris & a:qris2 ditangani di qris.py — terdaftar lebih dulu di main.py)

async def on_callback(update: Update, context):
    query = update.callback_query
    data = query.data or ""
    if not data.startswith("a:"):
        return

    parts = data.split(":")
    action = parts[1]

    try:
        if action == "pay":
            await _handle_mark_paid(update, context, int(parts[2]))
        elif action == "contact":
            await query.answer("Buka chat dengan user.")
            tid = parts[2]
            await query.message.reply_text(
                f"Chat user: <a href=\"tg://user?id={tid}\">buka chat</a>",
                parse_mode=ParseMode.HTML,
            )
        elif action == "detail":
            await query.answer()
            reg = db.get_registration(int(parts[2]))
            if not reg:
                await query.message.reply_text("Data tidak ditemukan.")
                return
            await query.message.reply_text(m.detail_text(reg), parse_mode=ParseMode.HTML)
    except (ValueError, IndexError):
        await query.answer("Callback tidak valid", show_alert=True)


# ── Mark Paid = Approve ────────────────────────────────────────────────────

async def _handle_mark_paid(update: Update, context, reg_id: int):
    """Admin 1 klik 'Mark as Paid' → approve + masukkan member ke grup VIP."""
    query = update.callback_query
    admin_id = _guard_full(update)
    if admin_id is None:
        await _denied(update, context)
        return

    reg = db.get_registration(reg_id)
    if not reg:
        await query.answer("Data tidak ditemukan.", show_alert=True)
        return
    if reg["status"] != "waiting_payment":
        await query.answer("Status belum 'menunggu pembayaran'.", show_alert=True)
        return

    vip_group = get_vip_group_id()
    if not vip_group:
        await query.answer("VIP_GROUP_ID belum diset — jalankan /setvip di grup VIP.", show_alert=True)
        return

    db.update_registration(
        reg_id,
        status="paid",
        paid_at=db._now_utc(),
        approved_by=admin_id,
        approved_at=db._now_utc(),
    )
    db.log_admin_action(reg_id, admin_id, "mark_paid")

    # Masukkan member langsung ke grup VIP (raw addChatMember)
    added = await add_member_directly(context, vip_group, reg["telegram_id"])

    if added:
        now = datetime.now(timezone.utc)
        db.update_registration(
            reg_id,
            status="active",
            joined_at=db.fmt_db(now),
            education_end=db.fmt_db(now + timedelta(days=90)),
        )
    else:
        # Fallback: invite link 1x pakai
        try:
            link, expire = await create_vip_invite(context, vip_group)
            db.update_registration(reg_id, status="invited", invite_link=link,
                                   invite_expire_at=db.fmt_db(expire))
        except TelegramError as e:
            print(f"[mark_paid] Gagal buat invite link: {e}")
            await query.answer("Gagal membuat undangan. Coba lagi.", show_alert=True)
            return

    reg = db.get_registration(reg_id)
    admin_label = _admin_name(update)

    # Notifikasi ke member
    try:
        await context.bot.send_message(
            reg["telegram_id"], m.approved_text(admin_label), parse_mode=ParseMode.HTML,
        )
    except TelegramError as e:
        print(f"[mark_paid] Gagal kirim ke user {reg['telegram_id']}: {e}")

    if added:
        try:
            await context.bot.send_message(
                reg["telegram_id"],
                m.WELCOME_JOIN.format(start=reg["joined_at"], end=reg["education_end"]),
                parse_mode=ParseMode.HTML,
            )
        except TelegramError as e:
            print(f"[mark_paid] Gagal kirim welcome ke {reg['telegram_id']}: {e}")
    else:
        try:
            await context.bot.send_message(
                reg["telegram_id"], m.INVITE_SENT.format(link=reg["invite_link"]),
                parse_mode=ParseMode.HTML,
            )
        except TelegramError as e:
            print(f"[mark_paid] Gagal kirim invite link ke {reg['telegram_id']}: {e}")

    await query.answer("✅ Approved — member diproses.")

    # Edit pesan di Grup A & B
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Hubungi", callback_data=f"a:contact:{reg['telegram_id']}"),
            InlineKeyboardButton("📋 Detail", callback_data=f"a:detail:{reg_id}"),
        ],
    ])
    await _edit_both_messages(context, reg, m.admin_approved_text(reg, admin_label), kb, kb)

    # Notifikasi approve ke Grup B
    group_b = get_query_group_id()
    if group_b:
        try:
            await context.bot.send_message(
                group_b,
                f"✅ <b>Admin 1 telah approve</b> — {reg['full_name']} (#{reg_id}) "
                f"({'masuk grup VIP' if added else 'dikirim link undangan'}).",
                parse_mode=ParseMode.HTML,
            )
        except TelegramError as e:
            print(f"[mark_paid] Gagal notif Grup B: {e}")


# ── Command admin ───────────────────────────────────────────────────────────

def _list_short(rows: list[dict]) -> str:
    if not rows:
        return "— kosong —"
    lines = []
    for r in rows:
        lines.append(f"<code>{r['id']}</code> · {r['full_name']} · {r['contact_wa']} · {r['status']}")
    return "\n".join(lines)


async def cmd_pending(update: Update, context):
    if not _guard_query(update):
        return await _denied(update, context)
    rows = db.list_registrations("pending")
    await update.message.reply_text(
        f"<b>⏳ Pending ({len(rows)})</b>\n\n{_list_short(rows)}", parse_mode=ParseMode.HTML
    )


async def cmd_active(update: Update, context):
    if not _guard_query(update):
        return await _denied(update, context)
    rows = db.list_active()
    await update.message.reply_text(
        f"<b>🎓 Active — dalam masa edukasi ({len(rows)})</b>\n\n{_list_short(rows)}",
        parse_mode=ParseMode.HTML,
    )


async def cmd_completed(update: Update, context):
    if not _guard_query(update):
        return await _denied(update, context)
    rows = db.list_completed()
    await update.message.reply_text(
        f"<b>🏁 Completed — selesai masa edukasi 3 bulan ({len(rows)})</b>\n\n{_list_short(rows)}",
        parse_mode=ParseMode.HTML,
    )


async def cmd_expired(update: Update, context):
    if not _guard_query(update):
        return await _denied(update, context)
    rows = db.list_expired_invites()
    await update.message.reply_text(
        f"<b>⏰ Invite hangus / belum join ({len(rows)})</b>\n\n{_list_short(rows)}",
        parse_mode=ParseMode.HTML,
    )


async def cmd_detail(update: Update, context):
    if not _guard_query(update):
        return await _denied(update, context)
    if not context.args:
        await update.message.reply_text("Gunakan: /detail <id atau telegram_id>")
        return
    raw = context.args[0]
    reg = db.get_registration(int(raw)) if raw.isdigit() else db.get_by_telegram_id(int(raw))
    if not reg:
        await update.message.reply_text("Data tidak ditemukan.")
        return
    await update.message.reply_text(m.detail_text(reg), parse_mode=ParseMode.HTML)


async def cmd_reinvite(update: Update, context):
    if not _guard_full(update):
        return await _denied(update, context)
    if not context.args:
        await update.message.reply_text("Gunakan: /reinvite <id>")
        return
    reg_id = int(context.args[0])
    reg = db.get_registration(reg_id)
    if not reg:
        await update.message.reply_text("Data tidak ditemukan.")
        return
    vip_group = get_vip_group_id()
    if not vip_group:
        await update.message.reply_text("VIP_GROUP_ID belum diset — jalankan /setvip di grup VIP.")
        return
    if reg.get("invite_link"):
        try:
            await context.bot.revoke_chat_invite_link(vip_group, reg["invite_link"])
        except TelegramError:
            pass
    link, expire = await create_vip_invite(context, vip_group)
    db.update_registration(reg_id, status="invited", invite_link=link, invite_expire_at=db.fmt_db(expire))
    db.log_admin_action(reg_id, update.effective_user.id, "reinvite")
    try:
        await context.bot.send_message(
            reg["telegram_id"], m.INVITE_SENT.format(link=link), parse_mode=ParseMode.HTML,
        )
        await update.message.reply_text(f"✅ Link baru dikirim ke #{reg_id}.")
    except TelegramError as e:
        await update.message.reply_text(f"⚠️ Gagal kirim ke user: {e}")


async def cmd_stats(update: Update, context):
    if not _guard_query(update):
        return await _denied(update, context)
    await update.message.reply_text(m.stats_text(db.get_stats()), parse_mode=ParseMode.HTML)


async def cmd_export(update: Update, context):
    if not _guard_query(update):
        return await _denied(update, context)
    path = db.export_csv()
    if not path:
        await update.message.reply_text("Belum ada data.")
        return
    with open(path, "rb") as f:
        await update.message.reply_document(f, filename=path.split("\\")[-1].split("/")[-1])


async def cmd_sync(update: Update, context):
    if not _guard_full(update):
        return await _denied(update, context)
    db.sync_completed_statuses()
    vip_group = get_vip_group_id()
    checked = 0
    updated = 0
    if vip_group:
        for reg in db.list_by_statuses(["invited", "active"]):
            try:
                member = await context.bot.get_chat_member(vip_group, reg["telegram_id"])
            except TelegramError:
                continue
            checked += 1
            if member.status in ("member", "administrator", "creator") and reg["status"] == "invited":
                from invite import record_join
                await record_join(context, reg, vip_group)
                updated += 1
    await update.message.reply_text(
        f"✅ Sinkronisasi selesai. {updated} member terdeteksi sudah join (dari {checked} dicek)."
    )


async def cmd_id(update: Update, context):
    """Informasi ID & peran — dipakai untuk setup."""
    user = update.effective_user
    chat = update.effective_chat
    role = db.admin_role(user.id)
    if role == "admin1":
        role_label = "✅ Admin 1 (query + approval)"
    elif role == "admin2":
        role_label = "👁️ Admin 2 (query saja)"
    else:
        role_label = "❌ Belum"
    txt = (
        f"<b>ID kamu</b>: <code>{user.id}</code>\n"
        f"<b>Chat ini</b>: <code>{chat.id}</code>\n"
        f"<b>Peran</b>: {role_label}"
    )
    a1 = db.get_admin1_id()
    a2 = db.get_admin2_id()
    txt += f"\n\n<b>Slot Admin 1</b>: {'<code>' + str(a1) + '</code>' if a1 else '🔓 Kosong'}"
    txt += f"\n<b>Slot Admin 2</b>: {'<code>' + str(a2) + '</code>' if a2 else '🔓 Kosong'}"
    if db.can_query(user.id):
        txt += (
            f"\n\n<b>Grup A (approval)</b>: <code>{get_admin_group_id() or '—'}</code>"
            f"\n<b>Grup B (query)</b>: <code>{get_query_group_id() or '—'}</code>"
            f"\n<b>Grup VIP</b>: <code>{get_vip_group_id() or '—'}</code>"
        )
    await update.message.reply_text(txt, parse_mode=ParseMode.HTML)


async def cmd_setadmin(update: Update, context):
    """Claim slot Admin 1 (query + approval). Hanya bisa di-claim SEKALI."""
    user = update.effective_user
    if db.get_admin1_id() is not None:
        await update.message.reply_text(
            "⛔ Slot Admin 1 sudah terisi. Tidak bisa di-claim lagi.\n\n"
            "Gunakan /setadmin2 untuk claim slot Admin 2 (query saja)."
        )
        return
    db.claim_admin1(user.id)
    await update.message.reply_text(
        f"✅ <b>Selamat!</b> Kamu terdaftar sebagai <b>Admin 1</b> "
        f"(query + approval).\n\n"
        f"Langkah selanjutnya:\n"
        f"1. Buat grup approval (Grup A) → tambah bot → /setgroup\n"
        f"2. Buat grup query (Grup B) → /setquerygroup\n"
        f"3. Di grup VIP → /setvip\n"
        f"4. Admin 2 bisa claim via /setadmin2",
        parse_mode=ParseMode.HTML,
    )


async def cmd_setadmin2(update: Update, context):
    """Claim slot Admin 2 (query saja). Hanya bisa di-claim SEKALI."""
    user = update.effective_user
    if db.get_admin2_id() is not None:
        await update.message.reply_text(
            "⛔ Slot Admin 2 sudah terisi. Hubungi Admin 1 untuk reset."
        )
        return
    db.claim_admin2(user.id)
    await update.message.reply_text(
        f"✅ Kamu terdaftar sebagai <b>Admin 2</b> (query saja — "
        f"bisa melihat data, tidak bisa approve).",
        parse_mode=ParseMode.HTML,
    )


async def cmd_deladmin2(update: Update, context):
    """Hapus Admin 2 (hanya oleh Admin 1)."""
    user = update.effective_user
    if not db.can_approve(user.id):
        return await _denied(update, context)
    db.set_setting("ADMIN2_ID", "")
    await update.message.reply_text(
        "✅ Slot Admin 2 dikosongkan. Orang lain bisa claim via /setadmin2."
    )


async def cmd_setvip(update: Update, context):
    """Set VIP_GROUP_ID — dari argumen, atau dari chat grup tempat command dijalankan."""
    if not _guard_full(update):
        return await _denied(update, context)
    chat = update.effective_chat
    if context.args and context.args[0].lstrip("-").isdigit():
        gid = int(context.args[0])
    elif chat and chat.type in ("group", "supergroup"):
        gid = chat.id
    else:
        await update.message.reply_text(
            "Jalankan /setvip di dalam grup VIP, atau /setvip <chat_id>."
        )
        return
    db.set_setting("VIP_GROUP_ID", str(gid))
    await update.message.reply_text(f"✅ VIP_GROUP_ID = <code>{gid}</code>", parse_mode=ParseMode.HTML)


async def cmd_setgroup(update: Update, context):
    """Set Grup A (approval — hanya Admin 1). Bisa dari argumen atau dari chat grup."""
    if not _guard_full(update):
        return await _denied(update, context)
    chat = update.effective_chat
    if context.args and context.args[0].lstrip("-").isdigit():
        gid = int(context.args[0])
    elif chat and chat.type in ("group", "supergroup"):
        gid = chat.id
    else:
        await update.message.reply_text(
            "Jalankan /setgroup di dalam grup approval, atau /setgroup <chat_id>."
        )
        return
    db.set_setting("ADMIN_GROUP_ID", str(gid))
    await update.message.reply_text(
        f"✅ Grup A (approval) = <code>{gid}</code>\n\n"
        f"Notifikasi pendaftar, bukti transfer + tombol Mark as Paid dikirim ke sini. "
        f"<b>Hanya masukkan Admin 1.</b>",
        parse_mode=ParseMode.HTML,
    )


async def cmd_setquerygroup(update: Update, context):
    """Set Grup B (query — Admin 1 & 2). Bisa dari argumen atau dari chat grup."""
    if not _guard_full(update):
        return await _denied(update, context)
    chat = update.effective_chat
    if context.args and context.args[0].lstrip("-").isdigit():
        gid = int(context.args[0])
    elif chat and chat.type in ("group", "supergroup"):
        gid = chat.id
    else:
        await update.message.reply_text(
            "Jalankan /setquerygroup di dalam grup query, atau /setquerygroup <chat_id>."
        )
        return
    db.set_setting("QUERY_GROUP_ID", str(gid))
    await update.message.reply_text(
        f"✅ Grup B (query) = <code>{gid}</code>\n\n"
        f"Laporan pendaftar + tombol Kirim QRIS (Admin 2) + bukti transfer diterima di sini. "
        f"<b>Masukkan Admin 1 & Admin 2.</b>",
        parse_mode=ParseMode.HTML,
    )


async def cmd_backup(update: Update, context):
    if not _guard_full(update):
        return await _denied(update, context)
    dest = db.backup_db()
    await update.message.reply_text(f"✅ Backup dibuat: {dest}")


async def cmd_checkadmin(update: Update, context):
    """Diagnostik: cek status bot di semua grup + privacy mode."""
    if not _guard_full(update):
        return await _denied(update, context)
    me = await context.bot.get_me()
    lines = [
        f"🤖 <b>Diagnostik bot</b>",
        f"Bot: @{me.username}",
        f"Privacy mode: {'❌ AKTIF — bot tidak lihat pesan grup' if not me.can_read_all_group_messages else '✅ Off (semua pesan diterima)'}",
        "",
    ]
    for label, gid in [
        ("Grup A (approval)", get_admin_group_id()),
        ("Grup B (query)", get_query_group_id()),
        ("Grup VIP", get_vip_group_id()),
    ]:
        if not gid:
            lines.append(f"{label}: ❌ belum diset")
            continue
        try:
            m = await context.bot.get_chat_member(gid, me.id)
            ok = m.status in ("administrator", "creator")
            lines.append(f"{label} ({gid}): {'✅ admin' if ok else '❌ member biasa — wajib admin + /setprivacy Disable'}")
        except Exception as e:
            lines.append(f"{label}: error {e}")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


def register_handlers(app):
    from telegram.ext import CommandHandler
    for cmd, handler in [
        ("pending", cmd_pending),
        ("active", cmd_active),
        ("completed", cmd_completed),
        ("expired", cmd_expired),
        ("detail", cmd_detail),
        ("reinvite", cmd_reinvite),
        ("stats", cmd_stats),
        ("export", cmd_export),
        ("sync", cmd_sync),
        ("id", cmd_id),
        ("setadmin", cmd_setadmin),
        ("setadmin2", cmd_setadmin2),
        ("deladmin2", cmd_deladmin2),
        ("setvip", cmd_setvip),
        ("setgroup", cmd_setgroup),
        ("setapproval", cmd_setgroup),  # alias
        ("setquerygroup", cmd_setquerygroup),
        ("backup", cmd_backup),
        ("checkadmin", cmd_checkadmin),
    ]:
        app.add_handler(CommandHandler(cmd, handler))