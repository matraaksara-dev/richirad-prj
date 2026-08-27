# PLAN: Richirad VIP Education Telegram Bot v1.2

**Dokumen:** Steering Plan — keputusan desain final & arsitektur
**Versi:** 1.2 (27 Agu 2026)
**Status:** LIVE — implementasi alur QRIS berjalan
**Referensi:** PRD v1.0, SPEC v1.2, TASK v1.2

---

## 0. Ringkasan Status

- **Bot:** [@richiradvip_bot](https://t.me/richiradvip_bot) — berjalan (long polling, `python main.py`)
- **Stack:** Python 3.13 + python-telegram-bot v21.11 + SQLite (WAL)
- **Database:** `richirad_vip.db` (SQLite, WAL mode, backup otomatis 6 jam)
- **Token:** di `bot/.env` (gitignored)
- **Grup VIP:** "VIP Richirad By TAA [insider]" — link `t.me/+b-UHMbB3oFFlODVl` (terverifikasi, aktif)

---

## 1. Steering Decisions (Mengikat)

| ID | Keputusan | Alasan |
|----|-----------|--------|
| S01 | Bahasa Indonesia (v1) | Target market |
| S02 | Source of truth = SQLite DB | Audit, export, portabel, tanpa server |
| S03 | Stack: Python + PTB (deterministik) + long polling | Tanpa hermes, tanpa LLM, 1 dependency pip, tanpa webhook/SSL |
| S04 | Disclaimer wajib sebelum form | Compliance trading education |
| S05 | Satu pertanyaan per pesan + button-first | UX Telegram 2025–2026 |
| S06 | **Admin = 2 slot tetap:** Admin 1 (query+approval) & Admin 2 (query only). Claim sekali. | Sesuai permintaan founder |
| S07 | **Grup A (Approval):** Admin 1 saja. Menerima laporan pendaftar (tanpa tombol QRIS), bukti transfer + tombol Mark Paid, notifikasi approve. | Approval terpusat & aman |
| S08 | **Grup B (Query):** Admin 1 & 2. Menerima laporan pendaftar + tombol Kirim QRIS (hanya Admin 2), bukti transfer (tanpa Mark Paid), notifikasi QRIS terkirim & approve. | Transparansi transaksi |
| S09 | **Alur:** daftar → Admin 2 kirim QRIS → member bayar → kirim bukti → Admin 1 Mark Paid = approve → bot masukkan ke grup VIP | Flow yang diinginkan founder |
| S10 | **QRIS diupload manual per member** oleh Admin 2 di grup B; file_id disimpan di DB utk kirim ulang. | Admin 2 pilih QRIS (dinamis/nominal) |
| S11 | **Mark Paid = approve:** status `paid`, `approved_by`, `approved_at`. Bot langsung `addChatMember` (raw API) + fallback `createChatInviteLink`. | "Langsung memasukkan" member |
| S12 | **Kirim ulang QRIS:** admin (tombol) & member (/qris saat `waiting_payment`). | Fault tolerance |
| S13 | **Bukti transfer** di-forward ke 2 grup: A (media + Mark Paid) & B (media + info "dalam proses approval"). | Transparansi + efisiensi |
| S14 | Tidak ada klaim profit / signal di copy bot | Brand + legal |
| S15 | Privacy Policy wajib di BotFather | Persyaratan Telegram |

---

## 2. Alur Final

### FASE 1 — Pendaftaran
```
User → /start → Welcome → [Daftar VIP] → Disclaimer (wajib)
→ Q1 Nama → Q2 Domisili → Q3 Level → Q4 Motivasi (opsional) → Q5 WA
→ Review → [Kirim] → DB: status=pending
→ Notifikasi ke Grup A (laporan, tanpa tombol QRIS)
→ Notifikasi ke Grup B (laporan, tombol [📤 Kirim QRIS] — hanya Admin 2)
```

### FASE 2 — Kirim QRIS (Admin 2)
```
[Grup B] Admin 2 klik [📤 Kirim QRIS]
→ Bot: "Kirim foto QRIS untuk {nama} di grup ini"
→ Admin 2 upload foto QRIS di grup B
→ Bot kirim QRIS + instruksi bayar ke member
→ DB: status=waiting_payment, qris_file_id, qris_sent_at
→ Notifikasi grup B: "QRIS telah dikirim ke {nama}"
→ Edit pesan di Grup A & B → status waiting_payment
   Grup A: [💬 Hubungi] [📋 Detail]
   Grup B: [🔁 Kirim Ulang QRIS] [💬 Hubungi] [📋 Detail]
```

### FASE 3 — Pembayaran & Bukti Transfer
```
Member bayar via QRIS → kirim foto bukti ke bot
→ Bot forward bukti (media asli) + catatan ke:
   Grup A (Approval): media + [💳 Mark as Paid]
   Grup B (Query): media + catatan "dalam proses approval" (tanpa tombol)
→ Member dapat konfirmasi: "Bukti transfer diterima"
```

### FASE 4 — Approval (Admin 1) + Masuk Grup VIP
```
[Grup A] Admin 1 klik [💳 Mark as Paid]
→ DB: status=paid, paid_at, approved_by, approved_at
→ Bot langsung addChatMember (raw API) ke grup VIP
→ Jika sukses: status=active, joined_at, education_end=+90d
→ Jika gagal: createChatInviteLink (1x, 48h), status=invited, link dikirim ke member
→ Notifikasi ke user: "Pembayaran dikonfirmasi! Kamu sudah ditambahkan..."
→ Edit pesan Grup A & B → status APPROVED
→ Notifikasi Grup B: "Admin 1 telah approve — member masuk grup VIP"
```

### FASE 5 — Masa Edukasi (90 hari)
```
chat_member event (member join) → record_join:
→ joined_at, education_end = +90 hari, status=active
→ Welcome message ke member
→ Notifikasi grup A & B
→ 90 hari kemudian: sync otomatis → status=completed
```

---

## 3. Skema Database (SQLite)

```sql
-- Registrations (tabel utama)
id              INTEGER PRIMARY KEY AUTOINCREMENT
telegram_id     INTEGER NOT NULL UNIQUE
username        TEXT
full_name       TEXT NOT NULL
domisili        TEXT NOT NULL
experience_level TEXT NOT NULL
motivation      TEXT
contact_wa      TEXT NOT NULL
source          TEXT DEFAULT 'organic'
status          TEXT NOT NULL DEFAULT 'pending'
  -- pending | waiting_payment | paid | invited | active | completed | rejected | cancelled | expired
disclaimer_accepted_at TEXT
approved_by     INTEGER
approved_at     TEXT
rejected_reason TEXT
rejected_at     TEXT
paid_at         TEXT
invite_link     TEXT
invite_expire_at TEXT
invite_used_at  TEXT
joined_at       TEXT
education_end   TEXT
qris_file_id    TEXT              -- file_id foto QRIS (untuk kirim ulang)
qris_sent_at    TEXT              -- waktu QRIS dikirim ke member
admin_message_id INTEGER           -- pesan notifikasi di Grup A
admin_chat_id   INTEGER
adminb_message_id INTEGER          -- pesan notifikasi di Grup B
adminb_chat_id  INTEGER
created_at      TEXT DEFAULT (datetime('now'))
updated_at      TEXT DEFAULT (datetime('now'))

-- admin_actions (audit trail)
id              INTEGER PRIMARY KEY
registration_id INTEGER NOT NULL
admin_id        INTEGER NOT NULL
action          TEXT NOT NULL
note            TEXT
created_at      TEXT DEFAULT (datetime('now'))

-- settings (konfigurasi runtime)
key   TEXT PRIMARY KEY
value TEXT
```

---

## 4. State Machine

```
pending ──(Admin 2 kirim QRIS)──→ waiting_payment
waiting_payment ──(Admin 1 Mark Paid)──→ paid ──(addChatMember)──→ active
                                                          └─(gagal)──→ invited ──(user join)──→ active
active ──(90 hari lewat)──→ completed
pending ──(Admin 1 reject)──→ rejected
invited ──(link expire)──→ expired
```

---

## 5. Callback Contract

| Callback data | Handler | Trigger | Guard |
|--------------|---------|---------|-------|
| `a:qris:{reg_id}` | `qris.on_qris_button` | Tombol "Kirim QRIS" di Grup B | Admin 2 only |
| `a:qris2:{reg_id}` | `qris.on_qris_resend` | Tombol "Kirim Ulang QRIS" | Admin 1 or 2 |
| `a:pay:{reg_id}` | `admin_panel.on_callback` | Tombol "Mark as Paid" di Grup A | Admin 1 only |
| `a:contact:{tid}` | `admin_panel.on_callback` | Tombol "Hubungi" | Admin 1 or 2 |
| `a:detail:{reg_id}` | `admin_panel.on_callback` | Tombol "Detail" | Admin 1 or 2 |

---

## 6. Command Admin

| Command | Admin 1 | Admin 2 | Fungsi |
|---------|:-------:|:-------:|--------|
| `/setadmin` | — | — | Claim Admin 1 (sekali) |
| `/setadmin2` | — | — | Claim Admin 2 (sekali, setelah Admin 1) |
| `/deladmin2` | ✅ | ❌ | Hapus Admin 2 |
| `/setgroup` / `/setapproval` | ✅ | ❌ | Set Grup A (approval) |
| `/setquerygroup` | ✅ | ❌ | Set Grup B (query) |
| `/setvip` | ✅ | ❌ | Set Grup VIP |
| `/pending` | ✅ | ✅ | Daftar pending |
| `/active` | ✅ | ✅ | Member aktif (masa edukasi) |
| `/completed` | ✅ | ✅ | Selesai 3 bulan |
| `/expired` | ✅ | ✅ | Invite hangus |
| `/detail` | ✅ | ✅ | Detail member |
| `/stats` | ✅ | ✅ | Statistik |
| `/export` | ✅ | ✅ | Ekspor CSV |
| `/reinvite` | ✅ | ❌ | Kirim ulang link undangan |
| `/sync` | ✅ | ❌ | Sinkronisasi status |
| `/id` | ✅ | ✅ | Info ID & peran |
| `/backup` | ✅ | ❌ | Backup manual |
| `/qris` (member) | — | — | Minta ulang QRIS |

---

## 7. Risiko & Mitigasi (tambahan khusus QRIS)

| Risiko Baru | Mitigasi |
|------------|----------|
| Admin 2 upload foto bukan QRIS (salah kirim) | Hanya foto pertama setelah klik tombol yang diproses; pending di-clear saat foto diterima |
| Member tidak bisa scan QRIS / QRIS error | `/qris` kirim ulang; admin tombol "Kirim Ulang QRIS" |
| addChatMember gagal (limit Telegram, member blok bot) | Fallback ke invite link + notifikasi ke admin |
| addChatMember sukses tapi chat_member event tidak sampai | Status langsung di-set active oleh mark_paid; `/sync` untuk verify |
| QRIS global (sama untuk semua) vs per member | QRIS diupload per member, file_id disimpan per registrasi (fleksibel) |
| Admin 2 klik "Kirim QRIS" untuk 2 member berturut-turut | Satu pending per grup; klik baru menggantikan pending sebelumnya |

Risiko dasar (token bocor, double-click, callback >64 byte, SQLite, 409 conflict, dll.) — lihat tabel lengkap di TASK v1.2 lampiran atau RUNBOOK.

---

## 8. Acceptance Criteria

- [x] User daftar → data masuk DB `pending`; notifikasi ke Grup A & B
- [ ] Admin 2 klik "Kirim QRIS" → upload foto → QRIS terkirim ke member + status `waiting_payment`
- [ ] Member kirim bukti → forward ke Grup A (dengan Mark Paid) & Grup B (info)
- [ ] Admin 1 klik "Mark as Paid" → addChatMember + aktif + welcome
- [ ] Jika addChatMember gagal → invite link fallback + member join → active
- [ ] Kirim ulang QRIS via tombol admin & `/qris` member
- [ ] Query admin: `/pending /active /completed /expired /detail /stats /export`
- [ ] Masa edukasi 3 bulan: `active` → `completed` otomatis setelah 90 hari
- [ ] Hanya Admin 1 bisa approve; Admin 2 hanya query
- [ ] Tidak ada klaim profit di copy bot

---

## 9. File Layout

```
richirad-telegrambot/
├── PRD-Richirad-VIP-Telegram-Bot.md          (v1.0, referensi)
├── PLAN-Richirad-VIP-Telegram-Bot-v1.2.md     (dokumen ini)
├── SPEC-Richirad-VIP-Telegram-Bot.md          (spesifikasi implementasi)
├── TASK-Richirad-VIP-Telegram-Bot.md          (task breakdown)
├── RUNBOOK-SETUP.md                           (panduan operasional)
├── .gitignore
├── richirad_vip.db                            (SQLite)
├── backups/
└── bot/
    ├── main.py          (entry point)
    ├── config.py        (.env loader)
    ├── db.py            (SQLite layer)
    ├── messages.py      (copywriting)
    ├── flow_user.py     (form 5 langkah)
    ├── admin_panel.py   (panel admin, mark paid, query)
    ├── qris.py          (kirim QRIS, capture foto, resend)
    ├── payment.py       (auto-forward bukti)
    ├── invite.py        (invite link, tracking join)
    ├── .env             (token — gitignored)
    └── .env.example
```

---

**Akhir PLAN v1.2** — keputusan steering final. Berlaku untuk seluruh implementasi selanjutnya.