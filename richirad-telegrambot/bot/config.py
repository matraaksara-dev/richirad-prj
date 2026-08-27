"""
Config — load .env + DB settings.
Priority: DB settings > .env file > default.
"""
import os
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent / ".env"


def _load_env():
    if not ENV_PATH.exists():
        return
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip("\"'")
            if val:
                os.environ.setdefault(key, val)


def get_setting(key: str, default: str | None = None) -> str | None:
    # DB setting override
    try:
        from db import get_setting as db_get
        val = db_get(key, None)
        if val is not None:
            return val
    except Exception:
        pass
    # env fallback
    return os.environ.get(key, default)


def get_int(key: str, default: int | None = None) -> int | None:
    val = get_setting(key)
    if val is not None:
        try:
            return int(val)
        except ValueError:
            pass
    return default


def get_int_list(key: str) -> set[int]:
    val = get_setting(key, "")
    if not val:
        return set()
    return {int(x.strip()) for x in val.split(",") if x.strip().isdigit()}


# Bootstrap — panggil sekali
_load_env()