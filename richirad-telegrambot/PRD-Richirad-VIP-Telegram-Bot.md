# PRD: Richirad VIP Education — Telegram Registration Bot

**Dokumen:** Product Requirements Document  
**Produk:** Telegram Bot Pendaftaran VIP Education  
**Versi:** 1.0  
**Tanggal:** 27 Agustus 2026  
**Status:** Draft untuk implementasi  
**Pemilik:** Richirad. (Founder / Product Owner)  
**Audience:** Developer, AI coding agent, Admin operasional  

---

## 1. Ringkasan Eksekutif

### 1.1 Latar Belakang
Richirad. adalah komunitas edukasi trading futures & spot berbasis Malang. Saat ini pendaftaran program **VIP Education** dilakukan manual melalui grup Telegram publik (`t.me/Taa_x_Richirad`). Proses ini tidak terstruktur, sulit dilacak, dan tidak memiliki audit trail yang jelas.

### 1.2 Tujuan Produk
Membangun **Telegram Bot** yang:
1. Menggantikan alur manual menjadi flow kualifikasi terstruktur.
2. Mengumpulkan data pendaftar secara konsisten.
3. Menyimpan data ke database (source of truth).
4. Mengirim notifikasi + tombol aksi ke **Grup Admin privat** sebagai panel operasional.
5. Menjalankan alur Approve → Payment → Onboarding secara semi-otomatis.
6. Mematuhi disclaimer compliance (edukasi, bukan investasi, risiko trading).

### 1.3 Non-Tujuan (Out of Scope v1)
- Bot signal / rekomendasi aset.
- Pembayaran otomatis penuh (Stripe/crypto auto-verify) — opsional di V2.
- Mini App kompleks.
- Multi-bahasa (selain Bahasa Indonesia).
- Integrasi CRM eksternal (HubSpot, dll.).

### 1.4 Metrik Keberhasilan (Success Metrics)
| Metrik | Target Awal (30 hari) |
|--------|------------------------|
| Completion rate flow pendaftaran | ≥ 60% |
| Waktu rata-rata admin merespons | ≤ 24 jam kerja |
| Data hilang / duplikat | 0 |
| User yang menerima invite setelah approve + bayar | 100% dari yang approved & confirmed payment |
| Complaint terkait klaim profit / mis-selling | 0 |

---

## 2. Personas & Stakeholders

| Peran | Kebutuhan Utama |
|-------|-----------------|
| **Pendaftar (User)** | Proses daftar yang jelas, transparan, cepat, dan merasa aman (disclaimer jelas). |
| **Admin Richirad** | Melihat pendaftar baru real-time, approve/reject dengan 1 klik, chat user, track status. |
| **Founder / Ops** | Audit trail, export data, kontrol akses grup VIP. |
| **Developer / AI Agent** | Spec yang jelas, state machine, callback contract, task breakdown. |

---

## 3. User Stories

### 3.1 Pendaftar
- Sebagai calon member, saya ingin memulai pendaftaran dari link website `/vip` agar data sumber tercatat.
- Sebagai calon member, saya ingin membaca disclaimer dan menyetujuinya sebelum mengisi data.
- Sebagai calon member, saya ingin mengisi data secara bertahap (satu pertanyaan per pesan) agar tidak overwhelm.
- Sebagai calon member, saya ingin melihat ringkasan data sebelum mengirim.
- Sebagai calon member, saya ingin mendapat konfirmasi bahwa data sudah diterima dan tahu langkah selanjutnya.
- Sebagai calon member, saya ingin mengecek status pendaftaran saya (`/status`).

### 3.2 Admin
- Sebagai admin, saya ingin menerima notifikasi di grup privat setiap ada pendaftar baru.
- Sebagai admin, saya ingin menekan tombol Approve / Reject / Hubungi langsung dari pesan notifikasi.
- Sebagai admin, saya ingin status di database dan pesan notifikasi ter-update setelah aksi.
- Sebagai admin, saya ingin user otomatis mendapat pesan status + instruksi pembayaran (jika approve).
- Sebagai admin, saya ingin menandai pembayaran sudah diterima dan memicu invite ke grup VIP.

---

## 4. Fitur & Scope

### 4.1 MVP (v1.0) — Wajib
| ID | Fitur | Prioritas |
|----|-------|-----------|
| F01 | `/start` + deep link tracking (`?start=vip_web`, dll.) | P0 |
| F02 | Welcome message + menu tombol (Daftar / Apa itu VIP / FAQ) | P0 |
| F03 | Disclaimer wajib (tidak bisa skip) | P0 |
| F04 | Flow kualifikasi 5 langkah (nama, domisili, level, motivasi opsional, WA) | P0 |
| F05 | Ringkasan + konfirmasi kirim | P0 |
| F06 | Simpan data ke database (status: `pending`) | P0 |
| F07 | Kirim notifikasi terstruktur + inline keyboard ke Grup Admin | P0 |
| F08 | Callback handler: Approve / Reject / Hubungi | P0 |
| F09 | Update status DB + edit pesan notifikasi + notifikasi ke user | P0 |
| F10 | Perintah `/status` untuk user | P0 |
| F11 | FAQ singkat via tombol | P1 |
| F12 | Privacy Policy (`/privacy`) + set di BotFather | P0 |
| F13 | Perintah admin: `/list_pending` (opsional ringan) | P2 |

### 4.2 Post-MVP (v1.5 – v2)
- Reminder follow-up otomatis (belum bayar).
- Tombol “Konfirmasi Pembayaran Diterima” → generate invite link 1x pakai.
- Export ke Google Sheet.
- Tracking sumber kampanye.
- Rate limiting & anti-spam dasar.

---

## 5. Alur Lengkap (User & Admin)

### 5.1 Alur User (Pendaftaran)

```
[Website / CTA] → t.me/Bot?start=SOURCE
        ↓
   /start (deep link param disimpan)
        ↓
┌──────────────────────────────┐
│ Welcome + 3 tombol           │
│ [Daftar VIP] [Apa itu VIP?] [FAQ]
└──────────────────────────────┘
        ↓ [Daftar VIP]
┌──────────────────────────────┐
│ Disclaimer (wajib)           │
│ [Saya paham & setuju] [Batal]│
└──────────────────────────────┘
        ↓
  Q1 Nama (text)
  Q2 Domisili [Malang] [Luar Malang]
  Q3 Level [Pemula] [Intermediate]
  Q4 Motivasi (text / "lewati")
  Q5 WhatsApp (text)
        ↓
┌──────────────────────────────┐
│ Ringkasan data               │
│ [Kirim] [Edit] [Batal]       │
└──────────────────────────────┘
        ↓ [Kirim]
  Simpan DB (status=pending)
  Kirim notifikasi ke Grup Admin
  Kirim konfirmasi ke User
```

### 5.2 Alur Admin: Klik Approve → Apa yang Terjadi Selanjutnya

```
Admin menekan [✅ Approve] pada pesan notifikasi di Grup Admin
        ↓
1. Bot menjawab callback (answerCallbackQuery) → toast "Disetujui"
2. Bot update database:
   - status = 'approved'
   - approved_by = admin_telegram_id
   - approved_at = now()
3. Bot edit pesan notifikasi di Grup Admin:
   - Status diganti menjadi "✅ APPROVED"
   - Tombol diganti menjadi [💳 Tandai Sudah Bayar] [💬 Hubungi] [📋 Detail]
4. Bot kirim pesan ke User (private chat):
   """
   ✅ Pendaftaranmu telah disetujui!

   Langkah selanjutnya:
   1. Siapkan kontribusi member USD 100
   2. Transfer sesuai instruksi admin (akan dikirim / sudah tertera)
   3. Kirim bukti transfer ke admin
   4. Setelah konfirmasi, kamu akan mendapat akses grup VIP

   [💬 Hubungi Admin]
   """
5. (Opsional) Bot kirim detail rekening / instruksi pembayaran
   (bisa hardcode di config atau dikirim manual admin dulu di v1)
        ↓
Admin menerima bukti bayar (manual / via chat)
        ↓
Admin menekan [💳 Tandai Sudah Bayar]
        ↓
6. Bot update DB: status = 'paid', paid_at = now()
7. Bot generate / ambil invite link grup VIP (1x pakai atau link terbatas)
8. Bot kirim ke User:
   """
   🎉 Pembayaran dikonfirmasi!

   Silakan gabung grup VIP Education:
   {INVITE_LINK}

   Link ini bersifat privat. Jangan dibagikan.
   Baca pesan “Mulai di sini” setelah masuk.
   """
9. Bot edit pesan di Grup Admin → status "PAID + INVITED"
10. (Opsional) Bot kirim welcome sequence di grup VIP saat user join
    (bisa ditangani bot terpisah atau event chat_member)
```

### 5.3 Alur Reject

```
Admin tekan [❌ Reject]
        ↓
Bot minta alasan (opsional) via force-reply atau tombol preset
        ↓
Update DB: status = 'rejected', rejected_reason, rejected_at
Edit pesan notifikasi → "❌ REJECTED"
Kirim pesan ke User:
"Maaf, pendaftaranmu belum dapat kami setujui saat ini.
Alasan: {reason}
Kamu tetap bisa bergabung di komunitas reguler: {link_grup_reguler}"
```

---

## 6. Format Pesan Notifikasi + Tombol Aksi (Optimal)

### 6.1 Pesan Notifikasi Awal (saat user submit)

**Parse mode:** HTML  
**Disable web page preview:** true  

```
🆕 <b>Pendaftaran VIP Baru</b>

<b>ID</b>: <code>{telegram_id}</code>
<b>Username</b>: @{username}
<b>Nama</b>: {full_name}
<b>Domisili</b>: {domisili}
<b>Level</b>: {experience_level}
<b>WhatsApp</b>: {contact_wa}
<b>Sumber</b>: {source}
<b>Motivasi</b>: {motivation atau "—"}

<b>Status</b>: ⏳ Pending
<b>Waktu</b>: {created_at Asia/Jakarta}

#vip #pending
```

**Inline Keyboard (row 1):**
| ✅ Approve | ❌ Reject |
|------------|----------|
**Row 2:**
| 💬 Hubungi User | 📋 Salin Data |

**Callback data convention (max 64 bytes):**
- `admin:approve:{registration_id}`
- `admin:reject:{registration_id}`
- `admin:contact:{telegram_id}`
- `admin:copy:{registration_id}`
- `admin:mark_paid:{registration_id}`
- `admin:detail:{registration_id}`

> Gunakan `registration_id` (UUID atau auto-increment) bukan hanya telegram_id, agar aman terhadap race condition.

### 6.2 Pesan Setelah Approve (hasil edit)

```
🆕 <b>Pendaftaran VIP</b>

... (data sama) ...

<b>Status</b>: ✅ APPROVED
<b>Disetujui oleh</b>: {admin_name} (@{admin_username})
<b>Waktu approve</b>: {approved_at}

#vip #approved
```

**Keyboard baru:**
| 💳 Tandai Sudah Bayar | 💬 Hubungi |
|-----------------------|------------|
| 📋 Detail             |            |

### 6.3 Pesan Setelah Mark Paid

```
... data ...

<b>Status</b>: 💰 PAID + INVITED
<b>Dibayar pada</b>: {paid_at}
<b>Invite dikirim</b>: Ya

#vip #paid
```

**Keyboard:**
| 💬 Hubungi | 📋 Detail |

### 6.4 Toast / Answer Callback
- Approve → `"Disetujui. User telah dinotifikasi."`
- Reject → `"Ditolak."`
- Mark Paid → `"Pembayaran dicatat. Invite telah dikirim."`
- Contact → `"Buka chat dengan user."` (atau kirim deep link `tg://user?id=...`)

---

## 7. Spesifikasi Teknis

### 7.1 Stack yang Direkomendasikan
| Layer | Teknologi |
|-------|-----------|
| Bot framework | **grammY** (TypeScript) atau Telegraf |
| Runtime | Node.js ≥ 20 |
| Database | Supabase (Postgres) **atau** Google Sheet + better-sqlite3 (MVP sangat sederhana) |
| Hosting | Railway / Render / Fly.io (webhook) |
| State management | Database-driven (jangan hanya in-memory) |

### 7.2 Model Data (Minimal)

```sql
-- registrations
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
telegram_id     BIGINT NOT NULL
username        TEXT
full_name       TEXT NOT NULL
domisili        TEXT NOT NULL          -- 'Malang' | 'Luar Malang'
experience_level TEXT NOT NULL         -- 'Pemula' | 'Intermediate'
motivation      TEXT
contact_wa      TEXT NOT NULL
source          TEXT DEFAULT 'organic'
status          TEXT NOT NULL DEFAULT 'pending'
  -- pending | approved | rejected | waiting_payment | paid | invited | cancelled
disclaimer_accepted_at TIMESTAMPTZ
approved_by     BIGINT
approved_at     TIMESTAMPTZ
rejected_reason TEXT
rejected_at     TIMESTAMPTZ
paid_at         TIMESTAMPTZ
invite_link     TEXT
admin_message_id BIGINT               -- message_id di grup admin (untuk edit)
admin_chat_id   BIGINT
created_at      TIMESTAMPTZ DEFAULT now()
updated_at      TIMESTAMPTZ DEFAULT now()
```

### 7.3 State Machine User (Conversation)

```
idle
  → start
  → disclaimer
  → ask_name
  → ask_domisili
  → ask_level
  → ask_motivation
  → ask_wa
  → review
  → submitted
  → (end)
```

Simpan state per `telegram_id` di tabel `user_sessions` atau kolom JSONB.

### 7.4 Bagaimana Bot Mengirim & Menangani Callback di Grup Admin

#### 7.4.1 Mengirim notifikasi
```ts
const msg = await bot.api.sendMessage(ADMIN_GROUP_ID, text, {
  parse_mode: "HTML",
  reply_markup: {
    inline_keyboard: [
      [
        { text: "✅ Approve", callback_data: `admin:approve:${regId}` },
        { text: "❌ Reject", callback_data: `admin:reject:${regId}` },
      ],
      [
        { text: "💬 Hubungi User", callback_data: `admin:contact:${telegramId}` },
        { text: "📋 Salin Data", callback_data: `admin:copy:${regId}` },
      ],
    ],
  },
});

// Simpan message_id untuk edit nanti
await db.from("registrations").update({
  admin_message_id: msg.message_id,
  admin_chat_id: ADMIN_GROUP_ID,
}).eq("id", regId);
```

#### 7.4.2 Menangani callback_query
```ts
bot.on("callback_query:data", async (ctx) => {
  const data = ctx.callbackQuery.data;
  if (!data.startsWith("admin:")) return;

  const [_, action, id] = data.split(":"); // admin:approve:uuid
  const adminId = ctx.from.id;

  // (Opsional) cek apakah user adalah admin yang diizinkan
  if (!ALLOWED_ADMIN_IDS.includes(adminId)) {
    await ctx.answerCallbackQuery({ text: "Tidak diizinkan", show_alert: true });
    return;
  }

  switch (action) {
    case "approve":
      await handleApprove(ctx, id, adminId);
      break;
    case "reject":
      await handleReject(ctx, id, adminId);
      break;
    case "mark_paid":
      await handleMarkPaid(ctx, id, adminId);
      break;
    case "contact":
      await ctx.answerCallbackQuery();
      await ctx.reply(`Chat user: tg://user?id=${id}`);
      break;
    // ...
  }
});
```

#### 7.4.3 Pattern handleApprove (inti)
```ts
async function handleApprove(ctx, regId, adminId) {
  const reg = await getRegistration(regId);
  if (!reg || reg.status !== "pending") {
    await ctx.answerCallbackQuery({ text: "Status sudah berubah", show_alert: true });
    return;
  }

  await updateRegistration(regId, {
    status: "approved",
    approved_by: adminId,
    approved_at: new Date().toISOString(),
  });

  await ctx.answerCallbackQuery({ text: "Disetujui. User dinotifikasi." });

  // Edit pesan di grup admin
  await ctx.api.editMessageText(reg.admin_chat_id, reg.admin_message_id, newText, {
    parse_mode: "HTML",
    reply_markup: newKeyboardAfterApprove(regId),
  });

  // Notifikasi user
  await ctx.api.sendMessage(reg.telegram_id, userApprovedMessage);
}
```

**Catatan penting:**
- Selalu `answerCallbackQuery` (wajib, max 1x per query).
- Gunakan `editMessageText` + `editMessageReplyMarkup` agar grup tidak penuh pesan baru.
- Validasi status sebelum update (idempotent).
- Log semua aksi admin ke tabel `admin_actions` (audit).

### 7.5 Environment Variables
```
BOT_TOKEN=
ADMIN_GROUP_ID=
ALLOWED_ADMIN_IDS=123456,789012
VIP_GROUP_ID=
DATABASE_URL=          # atau SUPABASE_URL + SUPABASE_KEY
WEBHOOK_URL=           # jika webhook
PAYMENT_INSTRUCTION=   # teks instruksi transfer (opsional)
```

### 7.6 Keamanan
- Token bot hanya di environment, tidak di repo.
- Callback data tidak mengandung data sensitif panjang.
- Hanya `ALLOWED_ADMIN_IDS` yang boleh menekan tombol aksi.
- Grup admin harus privat + bot sebagai admin.
- Rate limit perintah user (mis. max 5 submit / jam per user).
- Privacy Policy wajib (BotFather + `/privacy`).

---

## 8. Copywriting Utama (Siap Pakai)

### 8.1 /start
```
Halo! 👋

Saya **Richirad VIP Bot** — asisten pendaftaran program **VIP Education**.

Program edukasi intensif futures & spot (hingga 3 bulan) dengan dukungan praktik dan komunitas.
Bukan signal. Bukan jaminan profit.

Pilih salah satu di bawah:
```

### 8.2 Disclaimer
```
⚠️ **Disclaimer penting** (wajib dibaca)

Richirad. adalah komunitas edukasi trading.
Program VIP Education adalah program edukasi dan praktik — **bukan produk investasi** dengan jaminan imbal hasil.

Trading futures & spot mengandung risiko tinggi, termasuk kehilangan seluruh modal.
Keputusan dan tanggung jawab sepenuhnya ada pada masing-masing individu.

Dengan melanjutkan, kamu menyatakan:
• Memahami risiko trading
• Tidak mengharapkan jaminan profit
• Siap mengikuti proses edukasi dengan disiplin
```

### 8.3 Konfirmasi submit (ke user)
```
✅ Pendaftaran diterima!

Admin akan meninjau data kamu dan menghubungi via WhatsApp/Telegram dalam 1×24 jam kerja.

**Langkah berikutnya:**
1. Siapkan kontribusi member **USD 100**
2. Tunggu instruksi dari admin
3. Setelah konfirmasi pembayaran, kamu akan mendapat akses grup VIP + onboarding

Ada pertanyaan? Gunakan tombol di bawah.
```

---

## 9. Spec Steering (Keputusan Desain yang Mengikat)

Dokumen ini mengikat keputusan berikut. Perubahan harus melalui update PRD.

| ID | Keputusan | Alasan |
|----|-----------|--------|
| S01 | Bahasa UI: **Bahasa Indonesia** saja (v1) | Target market Malang + Indonesia |
| S02 | Source of truth = **Database**, bukan chat history | Audit, export, scale |
| S03 | Grup Admin = **panel aksi + notifikasi**, bukan database | Best practice hybrid |
| S04 | Disclaimer **wajib** diklik sebelum form | Compliance trading education |
| S05 | Satu pertanyaan per pesan + button-first | UX Telegram 2025–2026 |
| S06 | Callback data memakai `registration_id` | Hindari race condition |
| S07 | Setelah Approve → status `approved`, user dinotifikasi instruksi bayar | Pembayaran masih semi-manual di v1 |
| S08 | Invite link dikirim **hanya setelah** Mark Paid | Kontrol akses |
| S09 | Tidak ada klaim profit / signal di copy bot | Brand + legal |
| S10 | Privacy Policy wajib dipublikasikan | Persyaratan Telegram Bot |

---

## 10. Task Breakdown (Implementation)

### Epic A — Foundation
| Task | Estimasi | Keterangan |
|------|----------|------------|
| A1. Buat bot di BotFather + set description, commands, privacy, about | 0.5 jam | |
| A2. Setup repo + TypeScript + grammY/Telegraf | 1 jam | |
| A3. Setup database schema + migration | 1–2 jam | |
| A4. Environment & config module | 0.5 jam | |
| A5. Deploy webhook / long-polling dev | 1 jam | |

### Epic B — User Flow
| Task | Estimasi | Keterangan |
|------|----------|------------|
| B1. Handler `/start` + deep link source | 1 jam | |
| B2. Welcome + keyboard menu | 0.5 jam | |
| B3. Disclaimer step (wajib) | 1 jam | |
| B4. Conversation state machine (5 pertanyaan) | 3–4 jam | |
| B5. Review + submit | 1.5 jam | |
| B6. Simpan ke DB + validasi | 1 jam | |
| B7. Pesan sukses ke user | 0.5 jam | |
| B8. `/status` command | 1 jam | |
| B9. FAQ handlers | 1 jam | |
| B10. `/privacy` | 0.5 jam | |

### Epic C — Admin Group Integration
| Task | Estimasi | Keterangan |
|------|----------|------------|
| C1. Format pesan notifikasi + kirim ke ADMIN_GROUP_ID | 1.5 jam | |
| C2. Simpan `admin_message_id` | 0.5 jam | |
| C3. Callback router `admin:*` | 1 jam | |
| C4. handleApprove (update DB + edit message + notif user) | 2 jam | |
| C5. handleReject (+ alasan) | 1.5 jam | |
| C6. handleMarkPaid + kirim invite link | 2 jam | |
| C7. handleContact | 0.5 jam | |
| C8. Guard ALLOWED_ADMIN_IDS | 0.5 jam | |
| C9. Audit log aksi admin | 1 jam | |

### Epic D — Polish & Safety
| Task | Estimasi | Keterangan |
|------|----------|------------|
| D1. Idempotency & status guard | 1 jam | |
| D2. Error handling + logging | 1 jam | |
| D3. Rate limit dasar | 1 jam | |
| D4. Copywriting final + review compliance | 1 jam | |
| D5. Testing end-to-end (user + admin) | 2–3 jam | |
| D6. Dokumentasi runbook admin | 1 jam | |

**Total estimasi kasar MVP:** 25–35 jam kerja.

### Urutan Implementasi yang Disarankan
1. A1 → A5 (fondasi)
2. B1 → B7 (user bisa daftar sampai data masuk DB)
3. C1 → C4 (admin bisa Approve)
4. C5 → C6 (Reject + Mark Paid)
5. B8, B9, D* (polish)

---

## 11. Acceptance Criteria (MVP)

- [ ] User dari deep link `?start=vip_web` tercatat sourcenya.
- [ ] User tidak bisa melewati disclaimer.
- [ ] Semua field wajib terisi sebelum submit.
- [ ] Data muncul di database dengan status `pending`.
- [ ] Notifikasi muncul di Grup Admin dengan 4 tombol aksi.
- [ ] Klik Approve → DB update, pesan diedit, user dapat pesan.
- [ ] Klik Reject → DB update, user dapat pesan penolakan.
- [ ] Klik Mark Paid → user dapat invite link grup VIP.
- [ ] Hanya admin yang di-whitelist yang bisa menekan tombol aksi.
- [ ] `/status` mengembalikan status terkini user.
- [ ] Privacy Policy dapat diakses.
- [ ] Tidak ada klaim profit di seluruh copy bot.

---

## 12. Risiko & Mitigasi

| Risiko | Mitigasi |
|--------|----------|
| Admin menekan tombol dua kali | Idempotent update + cek status |
| User spam daftar | Rate limit + unique partial constraint |
| Invite link bocor | Gunakan join request / link 1x pakai / limited member |
| Bot token bocor | Env only + rotate via BotFather |
| Grup admin penuh | Selalu edit message, jangan kirim pesan baru untuk update status |
| Salah kirim invite sebelum bayar | Hanya kirim invite di handler Mark Paid |

---

## 13. Lampiran

### 13.1 Perintah Bot (setMyCommands)
```
start - Mulai / menu utama
status - Cek status pendaftaran
faq - Pertanyaan umum
privacy - Kebijakan privasi
help - Bantuan
```

### 13.2 Deep Link yang Didukung
| Param | Sumber |
|-------|--------|
| `vip_web` | Website halaman /vip |
| `vip_ig` | Instagram bio / story |
| `vip_group` | Dari grup reguler |
| `organic` | Default / tanpa param |

### 13.3 Glosarium
- **VIP Education**: Program edukasi intensif 3 bulan + dukungan praktik.
- **Grup Admin**: Grup privat berisi admin + bot untuk operasional.
- **Grup VIP**: Grup privat member yang sudah paid.
- **registration_id**: Identifier unik record di database.

---

**Akhir dokumen PRD v1.0**  
Dokumen ini siap digunakan sebagai steering document untuk implementasi oleh developer atau AI coding agent.
