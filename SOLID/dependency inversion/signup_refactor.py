from contextlib import closing
import re, sqlite3, smtplib
from email.message import EmailMessage

class Database:
  def __init__(self, path):
    self.path = path

  def execute(self, query, params):
    with closing(sqlite3.connect(self.path)) as conn:
      cur = conn.execute(query, params)
      conn.commit()
      return cur.lastrowid

class EmailService:
    def __init__(self, host: str, port: int, from_: str):
        self.host = host
        self.port = port
        self.from_ = from_

    def validate_email(self, email: str) -> bool:
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

    def send_email(self, to: str, subject: str, body: str) -> None:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = self.from_
        msg["To"] = to

        with smtplib.SMTP(self.host, self.port) as smtp:
            smtp.send_message(msg)

def signup(payload: dict, email_service: EmailService, db: Database) -> dict:
    email = (payload.get("email") or "").strip().lower()
    if not email_service.validate_email(email):
        raise ValueError("Invalid email")

    user_id = db.execute("INSERT INTO users(email) VALUES(?)", (email,))

    return { "id": user_id, "email": email }
