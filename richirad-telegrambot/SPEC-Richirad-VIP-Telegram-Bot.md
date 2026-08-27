# SPEC: Richirad VIP Education Telegram Bot v1.2

**Spesifikasi implementasi** — kontrak teknis antara desain (PLAN) dan kode.

---

## 1. Modul & Tanggung Jawab

| File | Tanggung jawab |
|------|----------------|
| `main.py` | Entry point, daftar handler, polling loop, background thread (sync+backup) |
| `config.py` | Load `.env` (BOT_TOKEN), priority: DB settings > env > default |
| `db.py` | SQLite (WAL), skema, query helper, admin 2-slot, settings, backup/export |
| `messages.py` | Semua copywriting (disclaimer, QRIS, bukti, approved, dll.) |
| `flow_user.py` | ConversationHandler form 5 langkah + `/start /status /faq /privacy` |
| `admin_panel.py` | Notifikasi ke 2 grup, Mark Paid = approve, query admin, setup grup |
| `qris.py` | Tombol Kirim QRIS (Admin 2), capture foto QRIS, resend, `/qris` member |
| `payment.py` | Auto-forward bukti transfer ke Grup A (Mark Paid) & B (info) |
| `invite.py` | createChatInviteLink, addChatMember (raw), chat_member tracking join |

---

## 2. Konfigurasi (settings / env)

| Key | Via | Fungsi |
|-----|-----|--------|
| `BOT_TOKEN` | `.env` | Token bot (wajib) |
| `ADMIN_GROUP_ID` | `/setgroup` / `/setapproval` | Grup A — approval, Admin 1 saja |
| `QUERY_GROUP_ID` | `/setquerygroup` | Grup B — query, Admin 1 & 2 |
| `VIP_GROUP_ID` | `/setvip` | Grup VIP member |
| `ADMIN1_ID` | `/setadmin` (claim) | Admin 1 (query + approval) |
| `ADMIN2_ID` | `/setadmin2` (claim) | Admin 2 (query only) |

---

## 3. Guard / Hak Akses

| Fungsi | db | Siapa |
|--------|----|-------|
| `can_approve(tid)` | `is_admin1(tid)` | Admin 1 saja |
| `can_query(tid)` | `is_admin1 or is_admin2` | Admin 1 & 2 |
| `_guard_full(update)` | `can_approve` | untuk Mark Paid, setgroup, reinvite, sync, backup |
| `_guard_query(update)` | `can_query` | untuk pending/active/completed/expired/detail/stats/export |
| Tombol `a:qris` | `is_admin2` | **khusus Admin 2** |
| Tombol `a:qris2`, `a:contact`, `a:detail` | `can_query` | Admin 1 & 2 |
| Tombol `a:pay` | `can_approve` | **khusus Admin 1** |

---

## 4. Rute Handler (urutan pendaftaran di main.py)

Urutan penting — PTB pakai handler pertama yang match:

1. `CommandHandler` `/start /status /faq /privacy` (flow_user)
2. `ConversationHandler` (daftar → 5 pertanyaan)
3. `CallbackQueryHandler` menu (`u:apavip`, `u:faq`) (flow_user)
4. `register_handlers` admin commands (admin_panel)
5. `CallbackQueryHandler` `^a:qris` & `^a:qris2` (qris) — **SEBELUM** admin_panel callback
6. `CallbackQueryHandler` `^a:` (admin_panel: pay/contact/detail)
7. `ChatMemberHandler` CHAT_MEMBER & MY_CHAT_MEMBER (invite)
8. `MessageHandler` `PRIVATE & (PHOTO|Document|TEXT non-command)` (payment: bukti)
9. `MessageHandler` `GROUP & PHOTO` → dipakai qris untuk capture QRIS (via pending state)

> Catatan: handler capture foto QRIS (qris) hanya aktif pada chat yang punya `_pending_qris` — tidak mengganggu pesan lain.

---

## 5. State Machine & Transisi (implementasi)

| Dari | Aksi | Ke |
|------|------|----|
| — | submit form | `pending` |
| `pending` | Admin 2 upload QRIS (on_qris_photo) | `waiting_payment` |
| `waiting_payment` | Admin 1 Mark Paid + addChatMember sukses | `active` |
| `waiting_payment` | Admin 1 Mark Paid + addChatMember gagal | `invited` (link) |
| `invited` | user join (chat_member) | `active` |
| `active` | 90 hari lewat (sync) | `completed` |
| `pending` | (opsional) reject | `rejected` |
| `invited` | link expire | `expired` |

---

## 6. Callback Data (max 64 byte)

Prefix pendek `a:` + aksi + `registration_id` (integer):

| Data | Aksi |
|------|------|
| `a:qris:{id}` | Admin 2 → mulai capture QRIS |
| `a:qris2:{id}` | Kirim ulang QRIS tersimpan |
| `a:pay:{id}` | Admin 1 → Mark Paid + masukkan ke grup |
| `a:contact:{tid}` | Buka chat user |
| `a:detail:{id}` | Tampilkan detail |

---

## 7. Format Pesan ke Grup

**Grup A (approval):**
- Laporan pendaftar: tanpa tombol QRIS, ada `[💬 Hubungi] [📋 Detail]`
- Bukti transfer: media + note + `[💳 Mark as Paid]`
- Edit status: `admin_qris_sent_text` / `admin_approved_text`

**Grup B (query):**
- Laporan pendaftar: dengan `[📤 Kirim QRIS]` (Admin 2) + `[💬 Hubungi] [📋 Detail]`
- Bukti transfer: media + note "dalam proses approval" (tanpa tombol)
- Notif: "QRIS terkirim", "Admin 1 approve"

---

## 8. Perekaman Pesan untuk Edit

`registrations` menyimpan 2 pasang lokasi pesan:
- `admin_chat_id` / `admin_message_id` → pesan di Grup A
- `adminb_chat_id` / `adminb_message_id` → pesan di Grup B

Helper: `_edit_both_messages(context, reg, text, kb_a, kb_b)` — edit keduanya, toleran jika salah satu tidak ada.

---

## 9. Kegagalan & Fallback

| Skenario | Perilaku |
|----------|----------|
| addChatMember gagal | `createChatInviteLink(member_limit=1, expire 48h)` → status `invited`, link ke member |
| kirim pesan ke user gagal (blocked) | log + notif ke admin (hubungi manual) |
| QRIS belum ada saat `/qris` | pesan "QRIS belum diterima admin" |
| status sudah berubah saat klik tombol | `answerCallbackQuery("Status sudah berubah")` — idempotent |
| callback tidak valid | `answerCallbackQuery("Callback tidak valid")` |

---

**Akhir SPEC v1.2**