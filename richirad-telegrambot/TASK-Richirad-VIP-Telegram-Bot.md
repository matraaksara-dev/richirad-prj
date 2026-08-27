# TASK: Richirad VIP Education Telegram Bot v1.2

**Task breakdown & tracking** — status pengerjaan.

---

## Status Legend
- ✅ Selesai & teruji
- 🔄 Sedang dikerjakan
- ⬜ Belum dikerjakan

---

## Epic A — Fondasi

| Task | Status | Catatan |
|------|:------:|---------|
| A1. Buat bot di BotFather + token | ✅ | `@richiradvip_bot`, token di `.env` |
| A2. Scaffold bot (main/config/db/messages) | ✅ | |
| A3. SQLite schema + migrasi kolom QRIS | ✅ | WAL mode, backup 6 jam |
| A4. Set commands BotFather | ✅ | start/status/faq/privacy |
| A5. Long polling `python main.py` | ✅ | Berjalan single-process |

## Epic B — User Flow

| Task | Status | Catatan |
|------|:------:|---------|
| B1. `/start` + deep link source | ✅ | |
| B2. Welcome + menu | ✅ | |
| B3. Disclaimer wajib | ✅ | |
| B4. Form 5 pertanyaan (ConversationHandler) | ✅ | |
| B5. Review + submit → DB `pending` | ✅ | |
| B6. Konfirmasi submit ke user | ✅ | |
| B7. `/status /faq /privacy` | ✅ | |
| B8. `/qris` member (minta ulang QRIS) | 🔄 | File `qris.py` sudah ditulis, perlu tes |

## Epic C — Admin & Grup A/B

| Task | Status | Catatan |
|------|:------:|---------|
| C1. 2-slot admin (Admin1/Admin2, claim sekali) | ✅ | `/setadmin`, `/setadmin2`, `/deladmin2` |
| C2. Setup grup: `/setgroup`, `/setquerygroup`, `/setvip` | ✅ | Grup A approval, Grup B query |
| C3. Notifikasi pendaftar ke Grup A (tanpa QRIS) | 🔄 | Perlu finalisasi di `admin_panel.send_admin_notification` |
| C4. Notifikasi pendaftar ke Grup B (+ tombol Kirim QRIS) | 🔄 | |
| C5. Tombol Kirim QRIS (Admin 2) + capture foto + kirim ke member | 🔄 | `qris.py` ditulis, perlu finalisasi wiring |
| C6. Kirim Ulang QRIS (admin) | 🔄 | `a:qris2` |
| C7. Auto-forward bukti → Grup A (Mark Paid) & B (info) | 🔄 | `payment.py` perlu update tombol per grup |
| C8. Mark Paid = approve → addChatMember + fallback invite | 🔄 | `admin_panel._handle_mark_paid` perlu refactor |
| C9. Edit 2 pesan (A & B) saat status berubah | 🔄 | `_edit_both_messages` |
| C10. Notifikasi approve ke Grup A & B | 🔄 | |

## Epic D — Invite & Masa Edukasi

| Task | Status | Catatan |
|------|:------:|---------|
| D1. Invite link 1x pakai (limit 1, 48 jam) | ✅ | `invite.create_vip_invite` |
| D2. addChatMember raw API (fallback) | 🔄 | Pakai `bot._post("addChatMember")` |
| D3. Tracking join (chat_member) → active + 90 hari | ✅ | `invite.record_join` |
| D4. Auto completed setelah 90 hari | ✅ | sync 6 jam + `/sync` |

## Epic E — Query Admin

| Task | Status | Catatan |
|------|:------:|---------|
| E1. `/pending /active /completed /expired` | ✅ | |
| E2. `/detail /stats /export` | ✅ | |
| E3. `/reinvite /sync /backup` | ✅ | |

## Epic F — Pengujian & Go-Live

| Task | Status | Catatan |
|------|:------:|---------|
| F1. Syntax check semua modul | 🔄 | Setelah refactor |
| F2. Test DB (status machine QRIS) | ⬜ | |
| F3. Test end-to-end (member + admin A/B) | ⬜ | Perlu founder di Telegram |
| F4. Setup manual founder (claim admin, grup, VIP) | ⬜ | RUNBOOK §1 |
| F5. Cabut link lama `t.me/+b-UHMbB3oFFlODVl` | ⬜ | Setelah go-live |
| F6. Update RUNBOOK | 🔄 | |

---

## Urutan Penyelesaian Saat Ini

1. **C3–C9**: Finalisasi `admin_panel.py` (notifikasi 2 grup, Mark Paid → add member)
2. **C7**: Update `payment.py` (bukti ke A dengan tombol, B tanpa)
3. **C10/D2**: Wiring `qris.py` + `invite.py` (addChatMember)
4. **D3**: Update `invite.record_join` → edit 2 pesan
5. **F1–F2**: Syntax + DB test
6. **F3–F5**: Founder test manual di Telegram

---

## Lampiran — Tabel Risiko Penuh (dari PLAN v1.1 + tambahan)

| Risiko | Mitigasi |
|--------|----------|
| Bot belum admin grup VIP | Checklist setup + deteksi saat start |
| Invite link bocor | member_limit=1 + expire 48h + revoke |
| Double approve | Guard idempotent (cek status) |
| Callback >64 byte | id integer + prefix pendek |
| Token dipakai 2 proses (409) | 1 token = 1 proses; jangan di hermes `.env` |
| SQLite race | WAL + single process + backup |
| User blokir bot | Fallback manual + notif admin |
| Perhitungan 3 bulan zona waktu | UTC di DB, tampil WIB |
| QRIS salah upload / tidak terbaca | Capture foto pertama saja; kirim ulang |
| addChatMember gagal | Fallback invite link |

---

**Akhir TASK v1.2** — status di-update seiring pengerjaan.