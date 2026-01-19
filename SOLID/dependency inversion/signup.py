# signup.py
import os, re, sqlite3, smtplib
from email.message import EmailMessage

def signup(payload: dict) -> dict:
    email = (payload.get("email") or "").strip().lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Invalid email")

    conn = sqlite3.connect(os.getenv("DB_PATH","app.db"))
    cur = conn.cursor()
    cur.execute("INSERT INTO users(email) VALUES(?)", (email,))
    user_id = cur.lastrowid
    conn.commit()
    conn.close()

    msg = EmailMessage()
    msg["From"] = os.getenv("EMAIL_FROM","noreply@example.com")
    msg["To"] = email
    msg["Subject"] = "Welcome"
    msg.set_content(f"Hi, your id is {user_id}")

    with smtplib.SMTP(os.getenv("SMTP_HOST","localhost"), int(os.getenv("SMTP_PORT","25"))) as s:
        s.send_message(msg)

    return {"id": user_id, "email": email}
