"""
Legion Communication Skills
Email (SMTP) and Messaging (Discord/Telegram/WhatsApp stubs pending credentials).
"""
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any


async def handle_email(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message", "")
    msg_l = msg.lower()

    smtp_user = os.getenv("SMTP_USERNAME", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not smtp_user or not smtp_pass:
        return {
            "success": False,
            "result": (
                "Email not configured. Add to .env:\n"
                "  SMTP_USERNAME=your@email.com\n"
                "  SMTP_PASSWORD=your_app_password\n"
                "  SMTP_HOST=smtp.gmail.com  (optional)\n"
                "  SMTP_PORT=587  (optional)"
            ),
        }

    # READ / CHECK
    if any(w in msg_l for w in ["read", "check", "inbox", "show email", "get email"]):
        return {
            "success": False,
            "result": "Email reading (IMAP) is not yet configured. Legion currently supports sending only.",
        }

    # SEND
    to_m = re.search(r"to[:\s]+([^\s,]+@[^\s,]+)", msg, re.IGNORECASE)
    subj_m = re.search(r'subject[:\s]+"?([^"\n]+)"?', msg, re.IGNORECASE)
    body_m = re.search(r'(?:body|message|content)[:\s]+"?([^"]+)"?', msg, re.IGNORECASE)

    if not to_m:
        return {
            "success": False,
            "result": "Specify recipient: 'send email to user@example.com subject: [subject] body: [body]'",
        }

    to_addr = to_m.group(1).strip()
    subject = subj_m.group(1).strip() if subj_m else "Message from Legion"
    body = body_m.group(1).strip() if body_m else msg

    try:
        email_msg = MIMEMultipart()
        email_msg["From"] = smtp_user
        email_msg["To"] = to_addr
        email_msg["Subject"] = subject
        email_msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_addr, email_msg.as_string())

        return {"success": True, "result": f"Email sent to {to_addr} — Subject: {subject}"}

    except smtplib.SMTPAuthenticationError:
        return {"success": False, "result": "SMTP authentication failed. Check SMTP_USERNAME and SMTP_PASSWORD in .env."}
    except smtplib.SMTPException as e:
        return {"success": False, "result": f"SMTP error: {e}"}
    except Exception as e:
        return {"success": False, "result": f"Email error: {e}"}


async def handle_messaging(params: dict[str, Any]) -> dict[str, Any]:
    msg_l = params.get("message", "").lower()

    # Check which platform is being targeted
    if "discord" in msg_l:
        token = os.getenv("DISCORD_BOT_TOKEN", "")
        if not token:
            return {"success": False, "result": "Discord not connected. Set DISCORD_BOT_TOKEN in .env."}
    elif "telegram" in msg_l:
        token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        if not token:
            return {"success": False, "result": "Telegram not connected. Set TELEGRAM_BOT_TOKEN in .env."}
    elif "whatsapp" in msg_l:
        return {"success": False, "result": "WhatsApp requires WhatsApp Business API credentials (not yet configured)."}

    return {
        "success": False,
        "result": (
            "Messaging platforms pending configuration. Add to .env to activate:\n"
            "  DISCORD_BOT_TOKEN  — Discord\n"
            "  TELEGRAM_BOT_TOKEN — Telegram\n\n"
            "WhatsApp requires WhatsApp Business API setup."
        ),
    }
