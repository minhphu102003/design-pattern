# messy_signup.py
import os
import re
import json
import hashlib
import sqlite3
import smtplib
import logging
import urllib.request
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path


def signup_and_welcome(payload: dict) -> dict:
    """
    A real-world-ish mess:
    - reads env config
    - validates input
    - normalizes data
    - password hashing
    - checks disposable email via HTTP
    - rate limits via local file counter
    - writes to sqlite
    - sends email via SMTP
    - logs + metrics
    - builds API response
    """

    # 0) Config / runtime concerns (changes by ops/env)
    db_path = os.getenv("DB_PATH", "app.db")
    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "25"))
    email_from = os.getenv("EMAIL_FROM", "noreply@example.com")
    salt = os.getenv("PASSWORD_SALT", "dev_salt")
    allow_disposable_check = os.getenv("DISPOSABLE_CHECK", "1") == "1"
    daily_limit = int(os.getenv("SIGNUP_DAILY_LIMIT", "50"))

    logger = logging.getLogger("signup")

    # 1) Parse + normalize (changes by API contract)
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    full_name = " ".join((payload.get("full_name") or "").split())
    marketing_opt_in = bool(payload.get("marketing_opt_in", False))

    # 2) Validation rules (changes by product/security)
    if not email:
        raise ValueError("Missing email")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Invalid email format")
    if len(password) < 10:
        raise ValueError("Password too short")
    if not full_name:
        raise ValueError("Missing full_name")

    # 3) Anti-abuse: daily signup limit using a local file (changes by risk policy)
    counter_file = Path(".signup_counter.json")
    today = datetime.now(timezone.utc).date().isoformat()
    data = {"date": today, "count": 0}
    if counter_file.exists():
        try:
            data = json.loads(counter_file.read_text("utf-8"))
        except Exception:
            data = {"date": today, "count": 0}

    if data.get("date") != today:
        data = {"date": today, "count": 0}

    if data["count"] >= daily_limit:
        raise RuntimeError("Daily signup limit reached")

    # 4) External check: disposable email domain check via HTTP (changes by provider/endpoint)
    if allow_disposable_check:
        domain = email.split("@")[-1]
        # fake-ish endpoint for exercise purpose
        url = f"https://example.com/disposable-check?domain={domain}"
        try:
            with urllib.request.urlopen(url, timeout=1.5) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
                if "disposable=true" in body:
                    raise ValueError("Disposable email is not allowed")
        except Exception:
            # swallow network errors to not block signup
            pass

    # 5) Security: password hashing policy (changes by security)
    password_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    # 6) Data access: sqlite schema + queries (changes by DB/schema)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "email TEXT UNIQUE, "
        "password_hash TEXT, "
        "full_name TEXT, "
        "marketing_opt_in INTEGER, "
        "created_at TEXT)"
    )

    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    if row:
        conn.close()
        raise ValueError("Email already registered")

    created_at = datetime.now(timezone.utc).isoformat()
    cur.execute(
        "INSERT INTO users(email, password_hash, full_name, marketing_opt_in, created_at) "
        "VALUES(?, ?, ?, ?, ?)",
        (email, password_hash, full_name, int(marketing_opt_in), created_at),
    )
    user_id = cur.lastrowid
    conn.commit()
    conn.close()

    # 7) Side effect: send welcome email (changes by template/provider)
    msg = EmailMessage()
    msg["From"] = email_from
    msg["To"] = email
    msg["Subject"] = "Welcome!"
    msg.set_content(f"Hi {full_name}, welcome! Your id is {user_id}")

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=2) as smtp:
            smtp.send_message(msg)
    except Exception as e:
        logger.warning("welcome_email_failed", extra={"user_id": user_id, "err": str(e)})

    # 8) Logging/metrics (changes by observability needs)
    logger.info("user_registered", extra={"user_id": user_id, "email": email})
    data["count"] += 1
    counter_file.write_text(json.dumps(data), encoding="utf-8")

    # 9) Response shaping (changes by API contract)
    return {"id": user_id, "email": email, "full_name": full_name, "created_at": created_at}
