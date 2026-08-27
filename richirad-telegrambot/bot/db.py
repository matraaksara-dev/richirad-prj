"""
Database layer — SQLite dengan WAL mode.
Semua helper untuk registrasi, query masa edukasi, admin actions, settings.
"""
import sqlite3
import os
import csv
import io
import time
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent
DB_PATH = DB_DIR / "richirad_vip.db"
BACKUP_DIR = DB_DIR / "backups"

# ── Koneksi ────────────────────────────────────────────────────────────────

_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(str(DB_PATH))
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode = WAL")
        _conn.execute("PRAGMA busy_timeout = 5000")
        _conn.execute("PRAGMA foreign_keys = ON")
    return _conn


# ── Inisialisasi ───────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS registrations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id         INTEGER NOT NULL UNIQUE,
    username            TEXT,
    full_name           TEXT NOT NULL,
    domisili            TEXT NOT NULL,
    experience_level    TEXT NOT NULL,
    motivation          TEXT,
    contact_wa          TEXT NOT NULL,
    source              TEXT DEFAULT 'organic',
    status              TEXT NOT NULL DEFAULT 'pending',
    disclaimer_accepted_at TEXT,
    approved_by         INTEGER,
    approved_at         TEXT,
    rejected_reason     TEXT,
    rejected_at         TEXT,
    paid_at             TEXT,
    invite_link         TEXT,
    invite_expire_at    TEXT,
    invite_used_at      TEXT,
    joined_at           TEXT,
    education_end       TEXT,
    admin_message_id    INTEGER,
    admin_chat_id       INTEGER,
    created_at          TEXT DEFAULT (datetime('now')),
    updated_at          TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS admin_actions (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_id    INTEGER NOT NULL,
    admin_id           INTEGER NOT NULL,
    action             TEXT NOT NULL,
    note               TEXT,
    created_at         TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT
);

INSERT OR IGNORE INTO settings (key, value) VALUES ('schema_version', '1');
"""


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA_SQL)
    # Migrasi: tambah kolom baru bila belum ada
    cols = [r[1] for r in conn.execute("PRAGMA table_info(registrations)").fetchall()]
    new_cols = {
        "qris_file_id": "TEXT",        # file_id foto QRIS yang diupload admin
        "qris_sent_at": "TEXT",        # waktu QRIS dikirim ke member
        "adminb_message_id": "INTEGER",  # pesan notifikasi di grup B (query)
        "adminb_chat_id": "INTEGER",
    }
    for name, typ in new_cols.items():
        if name not in cols:
            conn.execute(f"ALTER TABLE registrations ADD COLUMN {name} {typ}")
    conn.commit()
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


# ── Helper ─────────────────────────────────────────────────────────────────

def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def fmt_db(dt: datetime) -> str:
    """Datetime → string UTC untuk kolom waktu di DB."""
    if isinstance(dt, (int, float)):
        dt = datetime.fromtimestamp(dt, tz=timezone.utc)
    if isinstance(dt, str):
        return dt
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _row_to_dict(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    return dict(row)


# ── Settings ────────────────────────────────────────────────────────────────

def get_setting(key: str, default: str | None = None) -> str | None:
    cur = get_conn().execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    if row:
        return row["value"]
    # fallback ke env:
    import os as _os
    return _os.environ.get(key, default)


def set_setting(key: str, value: str):
    get_conn().execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    get_conn().commit()


# ── Admin (2 slot tetap) ────────────────────────────────────────────────────
# Admin 1: query + approval (claim sekali)
# Admin 2: query saja (claim sekali, setelah admin 1 terisi)

def get_admin1_id() -> int | None:
    raw = get_setting("ADMIN1_ID")
    if not raw or not raw.strip().isdigit():
        return None
    return int(raw)


def get_admin2_id() -> int | None:
    raw = get_setting("ADMIN2_ID")
    if not raw or not raw.strip().isdigit():
        return None
    return int(raw)


def claim_admin1(tid: int) -> bool:
    """Claim slot Admin 1. Return True jika berhasil, False jika sudah terisi."""
    if get_admin1_id() is not None:
        return False
    set_setting("ADMIN1_ID", str(tid))
    return True


def claim_admin2(tid: int) -> bool:
    """Claim slot Admin 2. Return True jika berhasil, False jika sudah terisi."""
    if get_admin2_id() is not None:
        return False
    set_setting("ADMIN2_ID", str(tid))
    return True


def is_admin1(tid: int) -> bool:
    a = get_admin1_id()
    return a is not None and a == tid


def is_admin2(tid: int) -> bool:
    a = get_admin2_id()
    return a is not None and a == tid


def can_approve(tid: int) -> bool:
    """Hanya Admin 1 yang boleh approve/reject/mark paid/reinvite."""
    return is_admin1(tid)


def can_query(tid: int) -> bool:
    """Admin 1 dan Admin 2 boleh melihat data."""
    return is_admin1(tid) or is_admin2(tid)


def admin_role(tid: int) -> str | None:
    """Role user: 'admin1' | 'admin2' | None."""
    if is_admin1(tid):
        return "admin1"
    if is_admin2(tid):
        return "admin2"
    return None


# ── Registrasi ──────────────────────────────────────────────────────────────

def create_registration(data: dict) -> int:
    conn = get_conn()
    cur = conn.execute(
        """INSERT INTO registrations
           (telegram_id, username, full_name, domisili, experience_level,
            motivation, contact_wa, source, disclaimer_accepted_at, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
        (
            data["telegram_id"],
            data.get("username", ""),
            data["full_name"],
            data["domisili"],
            data["experience_level"],
            data.get("motivation", ""),
            data["contact_wa"],
            data.get("source", "organic"),
            _now_utc(),
        ),
    )
    conn.commit()
    return cur.lastrowid


def get_registration(id: int) -> dict | None:
    return _row_to_dict(
        get_conn().execute("SELECT * FROM registrations WHERE id = ?", (id,)).fetchone()
    )


def get_by_telegram_id(tid: int) -> dict | None:
    return _row_to_dict(
        get_conn()
        .execute("SELECT * FROM registrations WHERE telegram_id = ?", (tid,))
        .fetchone()
    )


def update_registration(id: int, **fields):
    if not fields:
        return
    fields["updated_at"] = _now_utc()
    cols = ", ".join(f"{k} = ?" for k in fields)
    vals = list(fields.values()) + [id]
    get_conn().execute(f"UPDATE registrations SET {cols} WHERE id = ?", vals)
    get_conn().commit()


def list_registrations(status: str | None = None) -> list[dict]:
    if status:
        rows = get_conn().execute(
            "SELECT * FROM registrations WHERE status = ? ORDER BY created_at DESC",
            (status,),
        ).fetchall()
    else:
        rows = get_conn().execute(
            "SELECT * FROM registrations ORDER BY created_at DESC"
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def list_by_statuses(statuses: list[str]) -> list[dict]:
    placeholders = ",".join("?" for _ in statuses)
    rows = get_conn().execute(
        f"SELECT * FROM registrations WHERE status IN ({placeholders}) ORDER BY created_at DESC",
        statuses,
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_stats() -> dict:
    conn = get_conn()
    cur = conn.execute(
        """SELECT status, COUNT(*) as cnt FROM registrations GROUP BY status"""
    )
    stats = {row["status"]: row["cnt"] for row in cur.fetchall()}
    total = sum(stats.values())
    return {"total": total, **stats}


# ── Masa edukasi ────────────────────────────────────────────────────────────

def sync_completed_statuses():
    """Tandai status='active' yang sudah lewat education_end → 'completed'."""
    conn = get_conn()
    conn.execute(
        """UPDATE registrations SET status = 'completed', updated_at = ?
           WHERE status = 'active' AND education_end IS NOT NULL
           AND education_end < datetime('now')""",
        (_now_utc(),),
    )
    conn.commit()


def list_active() -> list[dict]:
    """Member dalam masa edukasi (active + belum lewat education_end)."""
    sync_completed_statuses()
    return list_by_statuses(["active"])


def list_completed() -> list[dict]:
    sync_completed_statuses()
    return list_by_statuses(["completed"])


def list_expired_invites() -> list[dict]:
    """Invite link yang sudah expire dan user belum join."""
    conn = get_conn()
    rows = conn.execute(
        """SELECT * FROM registrations
           WHERE status = 'invited' AND invite_expire_at IS NOT NULL
           AND invite_expire_at < datetime('now')
           ORDER BY created_at DESC"""
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


# ── Admin actions ───────────────────────────────────────────────────────────

def log_admin_action(reg_id: int, admin_id: int, action: str, note: str | None = None):
    get_conn().execute(
        "INSERT INTO admin_actions (registration_id, admin_id, action, note) VALUES (?, ?, ?, ?)",
        (reg_id, admin_id, action, note),
    )
    get_conn().commit()


# ── Backup & Export ─────────────────────────────────────────────────────────

def backup_db():
    """Backup database ke folder backups/ dengan timestamp."""
    ts = time.strftime("%Y%m%d-%H%M%S")
    dest = BACKUP_DIR / f"richirad_vip-{ts}.db"
    conn = get_conn()
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    shutil.copy2(str(DB_PATH), dest)
    # Hapus backup > 30 hari
    cutoff = time.time() - 30 * 86400
    for f in BACKUP_DIR.glob("richirad_vip-*.db"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
    return dest


def export_csv() -> str:
    """Ekspor semua registrasi ke CSV, return path file."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM registrations ORDER BY id"
    ).fetchall()
    if not rows:
        return ""
    cols = [desc[0] for desc in conn.execute("SELECT * FROM registrations LIMIT 0").description]
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = BACKUP_DIR / f"export-{ts}.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([r[c] for c in cols])
    return str(path)