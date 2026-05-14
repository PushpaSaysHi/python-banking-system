"""
email_service.py — Email notification service
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_ENABLED, EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_HOST, EMAIL_PORT


def send_email(to_email: str, subject: str, body: str):
    """Send an email notification. Silently skips if email is disabled or no address given."""
    if not EMAIL_ENABLED:
        return
    if not to_email:
        return

    try:
        msg = MIMEMultipart()
        msg["From"]    = EMAIL_ADDRESS
        msg["To"]      = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

        print(f"📧 Notification sent to {to_email}")

    except Exception as e:
        print(f"⚠️  Email could not be sent: {e}")


# ── Notification templates ───────────────────────────────────

def notify_deposit(email, owner_name, amount, balance):
    send_email(
        email,
        subject="PyBank — Deposit Received",
        body=(
            f"Hi {owner_name},\n\n"
            f"A deposit of ${amount:.2f} was made to your account.\n"
            f"New balance: ${balance:.2f}\n\n"
            f"If this wasn't you, contact us immediately.\n\n"
            f"— PyBank"
        )
    )


def notify_withdrawal(email, owner_name, amount, balance):
    send_email(
        email,
        subject="PyBank — Withdrawal Alert",
        body=(
            f"Hi {owner_name},\n\n"
            f"A withdrawal of ${amount:.2f} was made from your account.\n"
            f"New balance: ${balance:.2f}\n\n"
            f"If this wasn't you, contact us immediately.\n\n"
            f"— PyBank"
        )
    )


def notify_transfer_sent(email, owner_name, amount, to_id, balance):
    send_email(
        email,
        subject="PyBank — Transfer Sent",
        body=(
            f"Hi {owner_name},\n\n"
            f"You transferred ${amount:.2f} to account {to_id}.\n"
            f"New balance: ${balance:.2f}\n\n"
            f"If this wasn't you, contact us immediately.\n\n"
            f"— PyBank"
        )
    )


def notify_transfer_received(email, owner_name, amount, from_id, balance):
    send_email(
        email,
        subject="PyBank — Transfer Received",
        body=(
            f"Hi {owner_name},\n\n"
            f"You received ${amount:.2f} from account {from_id}.\n"
            f"New balance: ${balance:.2f}\n\n"
            f"— PyBank"
        )
    )


def notify_pin_changed(email, owner_name):
    send_email(
        email,
        subject="PyBank — PIN Changed",
        body=(
            f"Hi {owner_name},\n\n"
            f"Your PIN was successfully changed.\n\n"
            f"If this wasn't you, contact us immediately.\n\n"
            f"— PyBank"
        )
    )


def notify_account_created(email, owner_name, account_id, account_type):
    send_email(
        email,
        subject="PyBank — Welcome!",
        body=(
            f"Hi {owner_name},\n\n"
            f"Your PyBank account has been created!\n\n"
            f"Account ID   : {account_id}\n"
            f"Account Type : {account_type}\n\n"
            f"Keep your PIN safe — it cannot be recovered.\n\n"
            f"— PyBank"
        )
    )


def notify_account_locked(email, owner_name):
    send_email(
        email,
        subject="PyBank — Account Locked",
        body=(
            f"Hi {owner_name},\n\n"
            f"Your account has been locked due to too many failed PIN attempts.\n\n"
            f"Please contact support to unlock it.\n\n"
            f"— PyBank"
        )
    )
