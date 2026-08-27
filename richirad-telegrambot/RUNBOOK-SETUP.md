# RUNBOOK — Setup & Operasional Richirad VIP Bot

**Bot:** [@richiradvip_bot](https://t.me/richiradvip_bot)
**Status:** Bot sudah berjalan (long polling), database SQLite aktif.
**Folder:** `richirad-telegrambot/bot/`

---

### Langkah 0 — Matikan Privacy Mode (WAJIB SEBELUM SEMUA)
1. Buka [@BotFather](https://t.me/BotFather)
2. `/setprivacy` → pilih `@richiradvip_bot` → pilih **`Disable`**

> ⚠️ **Tanpa ini bot TIDAK menerima foto/message dari member di grup** (mis. foto QRIS yang diupload Admin 2 di Grup B tidak akan pernah sampai ke bot). Privacy mode hanya membiarkan bot melihat command/mention/reply, bukan pesan biasa.

### Verifikasi cepat
Setelah selesai semua langkah, ketik **`/checkadmin`** di chat bot (sebagai Admin 1) — bot menampilkan status privacy mode + keanggotaan di 3 grup (✅ admin / ❌ member biasa).

> **Sistem admin: 2 slot tetap.**
> - **Admin 1** — query + approval (claim sekali via `/setadmin`)
> - **Admin 2** — query saja (claim sekali via `/setadmin2`)
> - Setelah Admin 1 terisi, slot Admin 1 **tidak bisa di-claim orang lain**.
> - Admin 2 hanya bisa dihapus oleh Admin 1 (`/deladmin2`).

### Langkah 1 — Claim Admin 1 (query + approval)
1. Buka [t.me/richiradvip_bot](https://t.me/richiradvip_bot) → tekan **Start**
2. Ketik `/setadmin` di chat pribadi dengan bot
3. Bot membalas *"Kamu terdaftar sebagai Admin 1"* → selesai

> ⚠️ Ini claim pertama: setelah slot Admin 1 terisi, `/setadmin` dari akun lain **ditolak**.

### Langkah 2 — Claim Admin 2 (query saja, opsional)
- Admin 2 (mis. partner/founder kedua) buka bot → ketik `/setadmin2`
- Admin 2 hanya bisa **melihat data** (`/pending`, `/active`, `/completed`, `/expired`, `/detail`, `/stats`, `/export`) — **tidak bisa** approve/reject/bayar
- Untuk menghapus Admin 2: Admin 1 ketik `/deladmin2`

### Langkah 3 — Siapkan 2 grup admin
Bot memakai **dua grup admin**:

| Grup | Isi | Fungsi | Set via |
|------|-----|--------|---------|
| **Approval + Query** | **Admin 1 saja** | Notifikasi pendaftar + tombol Approve/Reject/Bayar + bukti transfer. Admin 1 cek semua tanpa pindah grup. | `/setgroup` (alias `/setapproval`) |
| **Query** | **Admin 1 & 2** | Transparansi transaksi — menerima salinan bukti transfer. Tidak ada tombol approval di sini. | `/setquerygroup` |

**Cara setup:**
1. Buat grup privat "VIP Admin Panel" → tambahkan bot sebagai admin → di grup itu ketik `/setgroup` → bot balas `ADMIN_GROUP_ID (approval)`
2. Buat grup privat "VIP Query" (atau pakai grup lama) → tambahkan bot sebagai admin → tambahkan Admin 1 & Admin 2 sebagai member → di grup itu ketik `/setquerygroup` → bot balas `QUERY_GROUP_ID`

> ⚠️ **Grup Approval hanya Admin 1.** Notifikasi + tombol approval hanya muncul di sana. Grup Query hanya salinan bukti (transparansi) — Admin 2 tidak perlu masuk grup approval.

### Langkah 4 — Sambungkan ke grup VIP
1. Buka grup VIP **"VIP Richirad By TAA [insider]"**
2. Tambahkan bot `@richiradvip_bot` sebagai **admin** dengan izin:
   - ✅ **Undang pengguna** (invite users) — WAJIB
3. Di dalam grup VIP, ketik `/setvip`
4. Bot balas: `VIP_GROUP_ID = ...` → berarti sukses

> Tanpa izin "Undang pengguna", bot tidak bisa membuat link undangan otomatis.

### Langkah 5 — Uji alur lengkap (wajib sebelum dipakai)
1. Dari akun Telegram lain (atau mode incognito), buka bot → `/start` → **Daftar VIP** → isi form
2. Cek grup approval: harus muncul notifikasi pendaftar baru
3. Tekan **✅ Approve** → user harus dapat pesan "disetujui" + instruksi bayar
4. Dari akun user, **kirim foto bukti transfer** ke bot → harus otomatis ter-forward ke grup approval (dengan catatan nama/WA user) dan user dapat konfirmasi
5. Tekan **💳 Tandai Sudah Bayar** di grup approval → user harus dapat link undangan (1x pakai)
6. Klik link dari akun user → masuk grup VIP → bot harus kirim welcome + catat masa edukasi

### Langkah 6 — Go-live
- **Cabut link lama** `t.me/+b-UHMbB3oFFlODVl` (grup VIP → Pengaturan → Undang → Cabut link) agar tidak ada "pintu belakang". Semua member baru masuk lewat link otomatis dari bot.

---

## 2. Perintah Admin

| Perintah | Fungsi | Admin 1 | Admin 2 |
|----------|--------|:-------:|:-------:|
| `/setadmin` | Claim slot Admin 1 (sekali) | — | — |
| `/setadmin2` | Claim slot Admin 2 (sekali) | — | — |
| `/deladmin2` | Hapus Admin 2 | ✅ | ❌ |
| `/pending` | Daftar pendaftar menunggu approval | ✅ | ✅ |
| `/active` | Member aktif (masih dalam masa edukasi 3 bulan) | ✅ | ✅ |
| `/completed` | **Member yang sudah selesai masa edukasi (lewat 3 bulan)** | ✅ | ✅ |
| `/expired` | Invite link yang hangus / user belum join | ✅ | ✅ |
| `/detail <id>` | Detail lengkap 1 member | ✅ | ✅ |
| `/stats` | Ringkasan semua status | ✅ | ✅ |
| `/export` | Unduh semua data ke file CSV | ✅ | ✅ |
| `/reinvite <id>` | Kirim ulang link undangan baru | ✅ | ❌ |
| `/sync` | Sinkronisasi status & deteksi join yang terlewat | ✅ | ❌ |
| `/id` | Info ID & status slot | ✅ | ✅ |
| `/backup` | Backup database manual | ✅ | ❌ |
| `/setvip` | Set grup VIP (jalankan di dalam grup) | ✅ | ❌ |
| `/setgroup` / `/setapproval` | Set grup admin approval — hanya Admin 1 (jalankan di dalam grup) | ✅ | ❌ |
| `/setquerygroup` | Set grup query — Admin 1 & 2, salinan bukti transfer (jalankan di dalam grup) | ✅ | ❌ |
| `/checkadmin` | Diagnostik: status privacy + bot admin di 3 grup | ✅ | ❌ |
| `/qris` (member) | Minta ulang QRIS — ketik di chat bot | — | — |

> Tombol **Approve / Reject / Tandai Bayar** di grup admin: hanya Admin 1 yang berfungsi. Admin 2 yang menekan akan ditolak.

## 3. Alur Pembayaran QRIS & Bukti Transfer

**QRIS (dikirim Admin 2):**
1. Member daftar → laporan muncul di Grup A (tanpa tombol QRIS) & Grup B (**dengan tombol `📤 Kirim QRIS`**)
2. **Admin 2** klik `Kirim QRIS` di Grup B → bot minta upload foto QRIS di grup
3. Admin 2 upload foto QRIS → **bot kirim QRIS + instruksi bayar ke member** (status `waiting_payment`)
4. Grup B dapat notif "QRIS terkirim". Admin bisa `Kirim Ulang QRIS`; member bisa `/qris`

**Bukti transfer (dikirim member):**
1. Member bayar via QRIS → kirim foto bukti ke bot
2. **Media asli di-forward ke 2 grup:**
   - **Grup A** (Approval, Admin 1): media + tombol **`💳 Mark as Paid`**
   - **Grup B** (Query, Admin 1 & 2): media + keterangan "dalam proses approval" (tanpa tombol)
3. Member dapat konfirmasi "Bukti transfer diterima"

**Approval (Admin 1) → masuk grup VIP:**
1. Admin 1 klik `💳 Mark as Paid` di Grup A = **approve**
2. Bot **langsung memasukkan member ke grup VIP** (addChatMember). Jika gagal → fallback kirim link undangan 1x pakai
3. Member dapat pesan "Pembayaran dikonfirmasi" + welcome; Grup A & B dapat notifikasi approve
4. Masa edukasi 90 hari mulai tercatat

> Catatan: forward bukti hanya untuk member berstatus `waiting_payment` / `paid`. Tombol `Mark as Paid` hanya berfungsi untuk Admin 1; tombol `Kirim QRIS` hanya untuk Admin 2.

## 4. Perintah User (calon member)

`/start` (mulai daftar) · `/status` (cek status) · `/faq` · `/privacy`

---

## 5. Operasional

### Menjalankan / menghentikan bot
```bash
# Dari folder bot/
python main.py                    # jalankan (foreground)
```
Bot saat ini berjalan di background (file `bot.log`). Untuk restart:
```bash
# stop proses lama lalu jalankan lagi
```

### Database & backup
- File DB: `richirad-telegrambot/richirad_vip.db`
- Backup otomatis tiap 6 jam → folder `backups/`
- Backup manual: `/backup` (admin)

### Masa edukasi 3 bulan — cara kerjanya
- Terhitung otomatis sejak member **benar-benar join** grup VIP (`joined_at` + 90 hari).
- Status `active` → `completed` otomatis setelah lewat 90 hari (disinkronkan tiap 6 jam + tiap `/sync`).
- Query: `/active` (masih berjalan), `/completed` (sudah selesai).

---

## 6. Troubleshooting Cepat

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| Notifikasi tidak muncul di grup admin | `/setgroup` belum dijalankan | Jalankan `/setgroup` di dalam grup admin |
| Tombol "Tandai Sudah Bayar" alert "VIP_GROUP_ID belum diset" | `/setvip` belum dijalankan | Jalankan `/setvip` di dalam grup VIP |
| Bot tidak bisa buat link undangan | Bot bukan admin / tanpa izin undang di grup VIP | Cek izin bot di grup VIP (Langkah 3) |
| Link undangan tidak bekerja | Link sudah terpakai/expire (1x pakai, 48 jam) | Admin klik "Kirim Ulang Link" / `/reinvite <id>` |
| User tidak dapat pesan dari bot | User pernah blokir bot | Admin hubungi manual |
| Tidak bisa kirim bukti transfer | Bot tidak dalam status approval | User harus menunggu QRIS dari Admin 2 dulu |
| Tombol "Kirim QRIS" tidak muncul | Grup B belum di-set / bukan Admin 2 | Set `/setquerygroup`; tombol hanya Admin 2 |
| Tombol "Mark as Paid" tidak muncul | Grup A belum di-set / bukan Admin 1 | Set `/setgroup`; tombol hanya Admin 1 |
| Member tidak bisa /qris | Status bukan `waiting_payment` | /status untuk cek; QRIS harus dikirim Admin 2 dulu |

---

**Dibuat:** 27 Agustus 2026 · Versi bot v1.1
