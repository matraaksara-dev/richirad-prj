"""
Semua teks/copywriting bot — Bahasa Indonesia, compliance.
"""
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")


def _fmt(dt_str: str | None) -> str:
    """Format UTC string → WIB. Contoh: '27 Agu 2026, 14:30 WIB'"""
    if not dt_str:
        return "—"
    try:
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1]
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        dt_wib = dt.astimezone(WIB)
        bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
        return f"{dt_wib.strftime('%d')} {bulan[dt_wib.month-1]} {dt_wib.strftime('%Y, %H:%M')} WIB"
    except Exception:
        return dt_str or "—"


# ── /start ──────────────────────────────────────────────────────────────────

WELCOME = """\
Halo! 👋

Saya <b>Richirad VIP Bot</b> — asisten pendaftaran program <b>VIP Education</b>.

Program edukasi intensif futures & spot (hingga 3 bulan) dengan dukungan praktik dan komunitas.
Bukan signal. Bukan jaminan profit.

Pilih salah satu di bawah:"""

# ── Disclaimer ──────────────────────────────────────────────────────────────

DISCLAIMER = """\
⚠️ <b>Disclaimer penting</b> (wajib dibaca)

Richirad. adalah komunitas edukasi trading.
Program VIP Education adalah program edukasi dan praktik — <b>bukan produk investasi</b> dengan jaminan imbal hasil.

Trading futures & spot mengandung risiko tinggi, termasuk kehilangan seluruh modal.
Keputusan dan tanggung jawab sepenuhnya ada pada masing-masing individu.

Dengan melanjutkan, kamu menyatakan:
• Memahami risiko trading
• Tidak mengharapkan jaminan profit
• Siap mengikuti proses edukasi dengan disiplin"""

# ── Form questions ──────────────────────────────────────────────────────────

Q_NAME = "📝 <b>Nama lengkap</b>\n\nKetik nama lengkap kamu:"
Q_DOMISILI = "📍 <b>Domisili</b>\n\nKamu berdomisili di mana?"
Q_LEVEL = "📊 <b>Level pengalaman</b>\n\nPilih level kamu:"
Q_MOTIVASI = "💡 <b>Motivasi</b> (opsional)\n\nCeritakan sedikit motivasi kamu mengikuti program ini. Atau tekan tombol lewati."
Q_WA = "📞 <b>Nomor WhatsApp</b>\n\nKetik nomor WhatsApp yang bisa dihubungi (contoh: 08123456789):"

# ── Review ──────────────────────────────────────────────────────────────────

def review_text(data: dict) -> str:
    return f"""\
📋 <b>Ringkasan data pendaftaran</b>

<b>Nama</b>: {data['full_name']}
<b>Domisili</b>: {data['domisili']}
<b>Level</b>: {data['experience_level']}
<b>Motivasi</b>: {data.get('motivation') or '—'}
<b>WhatsApp</b>: {data['contact_wa']}
<b>Sumber</b>: {data.get('source', 'organic')}

Pastikan data sudah benar."""

# ── Konfirmasi submit ───────────────────────────────────────────────────────

SUBMIT_CONFIRM = """\
✅ <b>Pendaftaran diterima!</b>

Admin akan meninjau data kamu dan menghubungi via WhatsApp/Telegram dalam 1×24 jam kerja.

<b>Langkah berikutnya:</b>
1. Siapkan kontribusi member <b>USD 100</b>
2. Tunggu instruksi dari admin
3. Setelah konfirmasi pembayaran, kamu akan mendapat akses grup VIP + onboarding

Ada pertanyaan? Gunakan tombol di bawah."""

# ── QRIS ────────────────────────────────────────────────────────────────────

QRIS_MEMBER_MSG = """\
📤 <b>Instruksi Pembayaran</b>

Silakan lakukan pembayaran kontribusi member <b>USD 100</b> melalui QRIS di atas.

⏳ <b>QRIS ini hanya berlaku 5–10 menit</b> sejak kamu menerimanya.
Jika sudah kedaluwarsa, ketik /qris untuk mendapatkan QRIS baru.

Setelah transfer berhasil, <b>kirimkan bukti transfer (foto) ke chat ini</b>.
Admin akan memverifikasi dan memasukkan kamu ke grup VIP setelah konfirmasi.

💡 Jika QRIS tidak terbaca / ada kendala, ketik /qris untuk mengirim ulang."""


def admin_qris_sent_text(reg: dict) -> str:
    return f"""\
📤 <b>QRIS terkirim</b>

<b>ID</b>: <code>{reg['id']}</code>
<b>Nama</b>: {reg['full_name']}
<b>WhatsApp</b>: {reg['contact_wa']}

<b>Status</b>: ⏳ Menunggu pembayaran (waiting_payment)

#vip #qris"""


QRIS_MEMBER_RESEND = """\
🔄 <b>QRIS dikirim ulang.</b>

⏳ QRIS ini hanya berlaku <b>5–10 menit</b> sejak kamu menerimanya.
Silakan transfer dan kirimkan bukti transfer (foto) ke chat ini."""


# ── Approved (Mark Paid = approve) ──────────────────────────────────────────

def approved_text(admin_name: str) -> str:
    return f"""\
🎉 <b>Pembayaran dikonfirmasi!</b>

Kamu kini resmi terdaftar sebagai <b>member VIP Education</b>. Akses grup VIP & onboarding akan menyusul di chat ini.

📘 <b>Modul VIP Member</b>
Sebagai member, kamu juga mendapatkan akses modul pembelajaran khusus. Klik link di bawah untuk membukanya:

🔗 <a href="https://richirad-modul.vercel.app/">https://richirad-modul.vercel.app/</a>

🔑 <b>Password akses</b>: <code>richirad2026</code>

Simpan password ini baik-baik — hanya untuk member VIP.

Selamat belajar! 🚀
— <i>Dikonfirmasi oleh {admin_name}</i>"""


def admin_approved_text(reg: dict, admin_name: str) -> str:
    return f"""\
✅ <b>APPROVED — Member Masuk Grup VIP</b>

<b>ID</b>: <code>{reg['id']}</code>
<b>Telegram ID</b>: <code>{reg['telegram_id']}</code>
<b>Nama</b>: {reg['full_name']}
<b>Domisili</b>: {reg['domisili']}
<b>Level</b>: {reg['experience_level']}

<b>Status</b>: 💰 PAID + APPROVED
<b>Dikonfirmasi oleh</b>: {admin_name}
<b>Dibayar pada</b>: {_fmt(reg['paid_at'])}
<b>Ditambahkan ke grup VIP</b>: Ya

#vip #paid #approved"""


# ── Bukti transfer (note untuk forward) ─────────────────────────────────────

def proof_note(reg: dict, status_label: str = "dalam proses approval") -> str:
    return f"""\
💳 <b>Bukti transfer</b>

<b>ID</b>: <code>{reg['id']}</code>
<b>Nama</b>: {reg['full_name']}
<b>WhatsApp</b>: {reg['contact_wa']}
<b>Status</b>: {reg['status']}

<i>{status_label}</i>"""


# ── QRIS terkirim (notifikasi grup B) ───────────────────────────────────────

def qris_sent_notif(reg: dict) -> str:
    return f"""📤 QRIS telah dikirim ke {reg['full_name']} (#{reg['id']}). Status: menunggu pembayaran."""


# ── Rejected ────────────────────────────────────────────────────────────────

def rejected_text(reason: str | None) -> str:
    msg = "Maaf, pendaftaranmu belum dapat kami setujui saat ini."
    if reason and reason != "—":
        msg += f"\n\nAlasan: {reason}"
    msg += "\n\nKamu tetap bisa bergabung di komunitas reguler. Hubungi admin untuk info lebih lanjut."
    msg += "\n\n💬 <b>Hubungi admin</b> jika ada pertanyaan."
    return msg

# ── Paid + Invite ───────────────────────────────────────────────────────────

INVITE_SENT = """\
🎉 <b>Pembayaran dikonfirmasi!</b>

Silakan gabung grup VIP Education melalui link di bawah ini:

{link}

<b>Link ini bersifat privat dan hanya bisa dipakai 1 kali.</b>
Jangan dibagikan ke siapa pun.

📘 <b>Modul VIP Member</b>
Jangan lupa akses modul pembelajaran khusus member:
🔗 <a href="https://richirad-modul.vercel.app/">https://richirad-modul.vercel.app/</a>
🔑 <b>Password</b>: <code>richirad2026</code>

Setelah masuk, baca pesan "Mulai di sini" untuk memulai onboarding."""

# ── Welcome after join ──────────────────────────────────────────────────────

WELCOME_JOIN = """\
🎉 <b>Selamat datang di VIP Education!</b>

Saat ini kamu tercatat dalam program edukasi 3 bulan. Periode edukasi kamu:
{start} — {end}

Gunakan waktu ini sebaik-baiknya untuk belajar dan praktik.

Selamat belajar! 🔥"""

# ── Admin notification ──────────────────────────────────────────────────────

def admin_notification(reg: dict) -> str:
    return f"""\
🆕 <b>Pendaftaran VIP Baru</b>

<b>ID</b>: <code>{reg['id']}</code>
<b>Telegram ID</b>: <code>{reg['telegram_id']}</code>
<b>Username</b>: @{reg['username'] or '—'}
<b>Nama</b>: {reg['full_name']}
<b>Domisili</b>: {reg['domisili']}
<b>Level</b>: {reg['experience_level']}
<b>WhatsApp</b>: {reg['contact_wa']}
<b>Sumber</b>: {reg['source']}
<b>Motivasi</b>: {reg.get('motivation') or '—'}

<b>Status</b>: ⏳ Pending
<b>Waktu</b>: {_fmt(reg['created_at'])}

#vip #pending"""


def admin_joined_text(reg: dict) -> str:
    return f"""\
🆕 <b>Pendaftaran VIP</b>

<b>ID</b>: <code>{reg['id']}</code>
<b>Nama</b>: {reg['full_name']}

<b>Status</b>: ✅ ACTIVE (sudah join grup)
<b>Join pada</b>: {_fmt(reg['joined_at'])}
<b>Masa edukasi</b>: {_fmt(reg['joined_at'])} — {_fmt(reg['education_end'])}

#vip #active"""


def admin_rejected_text(reg: dict, reason: str) -> str:
    return f"""\
🆕 <b>Pendaftaran VIP</b>

<b>ID</b>: <code>{reg['id']}</code>
<b>Nama</b>: {reg['full_name']}

<b>Status</b>: ❌ REJECTED
<b>Alasan</b>: {reason}
<b>Waktu reject</b>: {_fmt(reg['rejected_at'])}

#vip #rejected"""

# ── FAQ ─────────────────────────────────────────────────────────────────────

FAQ = """\
<b>❓ Apa itu VIP Education?</b>
Program edukasi intensif futures & spot hingga 3 bulan. Cocok untuk pemula dan intermediate yang ingin belajar dengan struktur dan dukungan komunitas.

<b>❓ Berapa biayanya?</b>
Kontribusi member <b>USD 100</b> (sekali, untuk seluruh periode).

<b>❓ Apakah ini signal / jaminan profit?</b>
<b>Tidak.</b> Ini program edukasi. Trading mengandung risiko tinggi. Tidak ada jaminan profit.

<b>❓ Bagaimana cara daftar?</b>
Ketik /start lalu pilih "Daftar VIP".

<b>❓ Ada pertanyaan lain?</b>
Hubungi admin via tombol kontak."""

# ── Privacy ─────────────────────────────────────────────────────────────────

PRIVACY = """\
<b>Kebijakan Privasi Richirad VIP Bot</b>

1. Data yang dikumpulkan: nama, domisili, level pengalaman, motivasi, WhatsApp, ID Telegram.
2. Data digunakan hanya untuk proses pendaftaran dan administrasi program VIP Education.
3. Data tidak dibagikan ke pihak ketiga.
4. Data dapat dihapus dengan menghubungi admin.
5. Bot menggunakan enkripsi HTTPS untuk komunikasi.

Bot ini dioperasikan oleh Richirad. — Komunitas edukasi trading.

/start untuk kembali ke menu utama."""

# ── Status ──────────────────────────────────────────────────────────────────

def status_text(reg: dict) -> str:
    labels = {
        "pending": "⏳ Menunggu review admin",
        "approved": "✅ Disetujui — menunggu pembayaran",
        "waiting_payment": "💳 Menunggu konfirmasi pembayaran",
        "paid": "💰 Pembayaran dikonfirmasi — cek invite link",
        "invited": "🔗 Undangan dikirim — cek chat untuk link grup",
        "active": "🎓 Aktif — masa edukasi sedang berjalan",
        "completed": "✅ Selesai — masa edukasi 3 bulan telah berakhir",
        "rejected": "❌ Pendaftaran ditolak",
        "cancelled": "🚫 Dibatalkan",
        "expired": "⏰ Link undangan telah kadaluarsa",
    }
    s = reg.get("status", "unknown")
    label = labels.get(s, s)
    msg = f"<b>Status pendaftaran:</b> {label}\n"
    if reg.get("joined_at"):
        msg += f"<b>Bergabung</b>: {_fmt(reg['joined_at'])}\n"
    if reg.get("education_end"):
        msg += f"<b>Masa edukasi selesai</b>: {_fmt(reg['education_end'])}\n"
    if reg.get("approved_at"):
        msg += f"<b>Disetujui</b>: {_fmt(reg['approved_at'])}\n"
    if reg.get("rejected_reason"):
        msg += f"<b>Alasan</b>: {reg['rejected_reason']}\n"
    return msg

# ── Detail (admin) ──────────────────────────────────────────────────────────

def detail_text(reg: dict) -> str:
    return f"""\
📋 <b>Detail Registrasi #{reg['id']}</b>

<b>Telegram ID</b>: <code>{reg['telegram_id']}</code>
<b>Username</b>: @{reg['username'] or '—'}
<b>Nama</b>: {reg['full_name']}
<b>Domisili</b>: {reg['domisili']}
<b>Level</b>: {reg['experience_level']}
<b>Motivasi</b>: {reg.get('motivation') or '—'}
<b>WhatsApp</b>: {reg['contact_wa']}
<b>Sumber</b>: {reg['source']}

<b>Status</b>: {reg['status']}
<b>Daftar</b>: {_fmt(reg['created_at'])}
<b>Disclaimer</b>: {_fmt(reg['disclaimer_accepted_at'])}
<b>Disetujui oleh</b>: <code>{reg['approved_by'] or '—'}</code>
<b>Approve</b>: {_fmt(reg['approved_at'])}
<b>Alasan tolak</b>: {reg.get('rejected_reason') or '—'}
<b>Bayar</b>: {_fmt(reg['paid_at'])}
<b>Link invite</b>: {reg.get('invite_link') or '—'}
<b>Invite expire</b>: {_fmt(reg['invite_expire_at'])}
<b>Join</b>: {_fmt(reg['joined_at'])}
<b>Edukasi selesai</b>: {_fmt(reg['education_end'])}"""

# ── Stats ───────────────────────────────────────────────────────────────────

def stats_text(stats: dict) -> str:
    labels = {
        "pending": "⏳ Pending", "approved": "✅ Approved",
        "waiting_payment": "💳 Waiting Payment", "paid": "💰 Paid",
        "invited": "🔗 Invited", "active": "🎓 Active",
        "completed": "🏁 Completed", "rejected": "❌ Rejected",
        "cancelled": "🚫 Cancelled", "expired": "⏰ Expired",
    }
    lines = [f"<b>📊 Statistik Registrasi</b>\n\n<b>Total</b>: {stats.get('total', 0)}"]
    for k, label in labels.items():
        if k in stats:
            lines.append(f"{label}: {stats[k]}")
    return "\n".join(lines)