"""
config.py — All constants and settings for PyBank
"""
from dotenv import load_dotenv
import os

load_dotenv()

DB_FILE = "bank.db"

ACCOUNT_TYPES = {
    "1": {"name": "Kids",     "rate": 5.0},
    "2": {"name": "Student",  "rate": 3.5},
    "3": {"name": "Adult",    "rate": 2.0},
    "4": {"name": "Veteran",  "rate": 4.0},
    "5": {"name": "Business", "rate": 1.5},
}

# ── Email settings ──────────────────────────────────────────
# Fill these in with your own Gmail credentials
# For Gmail: enable 2FA then create an App Password at
#   https://myaccount.google.com/apppasswords
EMAIL_ENABLED  = True           # set to True once you fill in credentials
EMAIL_ADDRESS  = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_HOST     = "smtp.gmail.com"
EMAIL_PORT     = 587
