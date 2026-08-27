"""
Richirad VIP Bot — entry point.
Jalankan: python main.py
Long polling, tanpa webhook, tanpa hermes.
"""
import threading
import time
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import db
import config
from telegram.error import TelegramError
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    MessageHandler,
    filters,
)

import flow_user
import admin_panel
import invite
import payment
import qris

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("richirad-vip-bot")


def _bg_loop():
    """Sinkronisasi status completed + backup DB tiap 6 jam."""
    while True:
        time.sleep(6 * 3600)
        try:
            db.sync_completed_statuses()
            db.backup_db()
            log.info("Background: sync + backup selesai.")
        except Exception as e:
            log.error(f"Background error: {e}")


def main():
    db.init_db()
    token = config.get_setting("BOT_TOKEN")
    if not token:
        print("ERROR: BOT_TOKEN tidak ditemukan. Cek file bot/.env")
        sys.exit(1)

    app = ApplicationBuilder().token(token).build()

    # Error handler global — log semua exception agar tidak diam-diam gagal
    async def error_handler(update, context):
        err = context.error
        if isinstance(err, TelegramError):
            migrate_to = getattr(err, "migrate_to_chat_id", None)
            if migrate_to:
                log.info(f"Chat migrated ke {migrate_to} — dilanjutkan")
        log.error(f"Error pada update {getattr(update, 'update_id', '?')}: {err}")

    app.add_error_handler(error_handler)

    # ── User flow ──
    app.add_handler(CommandHandler("start", flow_user.cmd_start))
    app.add_handler(CommandHandler("status", flow_user.cmd_status))
    app.add_handler(CommandHandler("faq", flow_user.cmd_faq))
    app.add_handler(CommandHandler("privacy", flow_user.cmd_privacy))
    app.add_handler(CommandHandler("qris", qris.cmd_qris))  # member minta ulang QRIS
    app.add_handler(flow_user.conv_handler())
    app.add_handler(
        CallbackQueryHandler(flow_user.on_menu_callback, pattern="^(u:apavip|u:faq)$")
    )

    # ── Admin ──
    admin_panel.register_handlers(app)
    # QRIS callbacks didaftarkan SEBELUM admin_panel.on_callback
    app.add_handler(CallbackQueryHandler(qris.on_qris_button, pattern="^a:qris:"))
    app.add_handler(CallbackQueryHandler(qris.on_qris_resend, pattern="^a:qris2:"))
    app.add_handler(CallbackQueryHandler(admin_panel.on_callback, pattern="^a:"))

    # ── Invite & tracking grup VIP ──
    app.add_handler(ChatMemberHandler(invite.on_chat_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(ChatMemberHandler(invite.on_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))

    # ── Auto-forward bukti transfer (chat pribadi member) ──
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE
            & (filters.PHOTO | filters.Document.ALL | (filters.TEXT & ~filters.COMMAND)),
            payment.on_proof_message,
        )
    )

    # ── Capture foto/dokumen QRIS yang diupload admin di grup (pending state) ──
    app.add_handler(
        MessageHandler(
            filters.ChatType.GROUPS & (filters.PHOTO | filters.Document.ALL),
            qris.on_qris_photo,
        )
    )

    threading.Thread(target=_bg_loop, daemon=True).start()

    log.info("Bot mulai polling... (Ctrl+C untuk stop)")
    try:
        app.run_polling(allowed_updates=["message", "callback_query", "chat_member", "my_chat_member"])
    except KeyboardInterrupt:
        log.info("Dihentikan oleh user.")
        db.backup_db()


if __name__ == "__main__":
    main()