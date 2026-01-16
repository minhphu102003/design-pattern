from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
import smtplib
from typing import Optional

@dataclass(frozen=True)
class UserDraft:
    email: str
    full_name: str
    user_type: str
    password: str
    marketing_opt_in: bool = False


@dataclass(frozen=True)
class Config:
    db_path: str
    smtp_host: str
    smtp_port: int
    email_from: str
    password_salt: str
    disposable_check_enabled: bool
    daily_signup_limit: int
    signup_counter_file: str = ".signup_counter.json"

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            db_path=os.getenv("DB_PATH", "app.db"),
            smtp_host=os.getenv("SMTP_HOST", "localhost"),
            smtp_port=int(os.getenv("SMTP_PORT", "25")),
            email_from=os.getenv("EMAIL_FROM", "noreply@example.com"),
            password_salt=os.getenv("PASSWORD_SALT", "dev_salt"),
            disposable_check_enabled=(os.getenv("DISPOSABLE_CHECK", "1") == "1"),
            daily_signup_limit=int(os.getenv("SIGNUP_DAILY_LIMIT", "50")),
        )


class SignupValidator:
    _EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    @classmethod
    def normalize_and_validate(cls, payload: dict) -> UserDraft:
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password") or ""
        full_name = " ".join((payload.get("full_name") or "").split())
        user_type = (payload.get("user_type") or "NORMAL").strip().upper()
        marketing_opt_in = bool(payload.get("marketing_opt_in", False))

        if not email:
            raise ValueError("Missing email")
        if not cls._EMAIL_RE.match(email):
            raise ValueError("Invalid email format")
        if len(password) < 10:
            raise ValueError("Password too short")
        if not full_name:
            raise ValueError("Missing full_name")

        return UserDraft(
            email=email,
            full_name=full_name,
            user_type=user_type,
            password=password,
            marketing_opt_in=marketing_opt_in,
        )


class PasswordHasher:
    @staticmethod
    def hash(password: str, salt: str) -> str:
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


class DisposableEmailPolicy:
    _BLOCKED_DOMAINS = {"tempmail.com", "mailinator.com", "10minutemail.com"}

    @classmethod
    def is_disposable(cls, email: str) -> bool:
        parts = email.split("@")
        if len(parts) != 2:
            return False
        return parts[1].lower() in cls._BLOCKED_DOMAINS


class DailySignupLimiter:
    def __init__(self, counter_file: str, daily_limit: int):
        self._file = Path(counter_file)
        self._limit = daily_limit

    def check_and_increment(self) -> None:
        today = datetime.now(timezone.utc).date().isoformat()
        state = {"date": today, "count": 0}

        if self._file.exists():
            try:
                state = json.loads(self._file.read_text("utf-8"))
            except Exception:
                state = {"date": today, "count": 0}

        if state.get("date") != today:
            state = {"date": today, "count": 0}

        if int(state.get("count", 0)) >= self._limit:
            raise RuntimeError("Daily signup limit reached")

        state["count"] = int(state.get("count", 0)) + 1
        self._file.write_text(json.dumps(state), encoding="utf-8")

class UserRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def ensure_schema(self) -> None:
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    password_hash TEXT,
                    full_name TEXT,
                    user_type TEXT,
                    marketing_opt_in INTEGER,
                    created_at TEXT
                )
                """
            )
            conn.commit()

    def exists_by_email(self, email: str) -> bool:
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM users WHERE email = ?", (email,))
            return cur.fetchone() is not None

    def insert_user(self, *, draft: UserDraft, password_hash: str, created_at: str) -> int:
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO users(email, password_hash, full_name, user_type, marketing_opt_in, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    draft.email,
                    password_hash,
                    draft.full_name,
                    draft.user_type,
                    int(draft.marketing_opt_in),
                    created_at,
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

class EmailService:
    def __init__(self, smtp_host: str, smtp_port: int, email_from: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.email_from = email_from

    def build_welcome(self, *, to: str, full_name: str, user_id: int) -> EmailMessage:
        msg = EmailMessage()
        msg["From"] = self.email_from
        msg["To"] = to
        msg["Subject"] = "Welcome!"
        msg.set_content(f"Hi {full_name}, welcome! Your id is {user_id}.")
        return msg

    def send(self, msg: EmailMessage) -> None:
        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=2) as server:
            server.send_message(msg)

class Logger:
    def __init__(self, name: str = "signup"):
        self._logger = logging.getLogger(name)

    def info(self, message: str, extra: Optional[dict] = None) -> None:
        self._logger.info(message, extra=extra)

    def warning(self, message: str, extra: Optional[dict] = None) -> None:
        self._logger.warning(message, extra=extra)

    def error(self, message: str, extra: Optional[dict] = None) -> None:
        self._logger.error(message, extra=extra)

class SignupService:
    def __init__(
        self,
        *,
        config: Config,
        repo: UserRepository,
        email_service: EmailService,
        logger: Logger,
        limiter: DailySignupLimiter,
        disposable_policy: DisposableEmailPolicy,
        validator: SignupValidator,
        hasher: PasswordHasher,
    ):
        self.config = config
        self.repo = repo
        self.email_service = email_service
        self.logger = logger
        self.limiter = limiter
        self.disposable_policy = disposable_policy
        self.validator = validator
        self.hasher = hasher

    def signup(self, payload: dict) -> dict:
        draft = self.validator.normalize_and_validate(payload)
        self.limiter.check_and_increment()

        if self.config.disposable_check_enabled and self.disposable_policy.is_disposable(draft.email):
            raise ValueError("Disposable email is not allowed")

        password_hash = self.hasher.hash(draft.password, self.config.password_salt)

        self.repo.ensure_schema()
        if self.repo.exists_by_email(draft.email):
            raise ValueError("Email already registered")

        created_at = datetime.now(timezone.utc).isoformat()
        user_id = self.repo.insert_user(draft=draft, password_hash=password_hash, created_at=created_at)

        try:
            msg = self.email_service.build_welcome(to=draft.email, full_name=draft.full_name, user_id=user_id)
            self.email_service.send(msg)
        except Exception as e:
            self.logger.warning("welcome_email_failed", extra={"user_id": user_id, "err": str(e)})

        self.logger.info("user_registered", extra={"user_id": user_id, "email": draft.email})
        return {"id": user_id, "email": draft.email, "full_name": draft.full_name, "created_at": created_at}

def build_signup_service() -> SignupService:
    config = Config.from_env()
    repo = UserRepository(config.db_path)
    email_service = EmailService(config.smtp_host, config.smtp_port, config.email_from)
    logger = Logger("signup")
    limiter = DailySignupLimiter(config.signup_counter_file, config.daily_signup_limit)

    disposable_policy = DisposableEmailPolicy()
    validator = SignupValidator()
    hasher = PasswordHasher()

    return SignupService(
        config=config,
        repo=repo,
        email_service=email_service,
        logger=logger,
        limiter=limiter,
        disposable_policy=disposable_policy,
        validator=validator,
        hasher=hasher,
    )
