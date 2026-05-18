# 🏦 PyBank — Python Banking System

A command-line banking system built in Python with SQLite database, rich CLI interface, and email notifications.

---

## ✨ Features

- 🔐 **Secure login** — PIN hashing with SHA-256, account lockout after 3 failed attempts
- 👤 **Multiple account types** — Kids, Student, Adult, Veteran, Business
- 💰 **Full banking operations** — Deposit, Withdraw, Transfer between accounts
- 📈 **Monthly interest** — Auto calculated based on account type
- 📧 **Email notifications** — Get notified on every transaction
- 📄 **Transaction history** — Full history and mini statement (last 5)
- 🔑 **PIN management** — Change PIN securely anytime
- 🔒 **Admin panel** — Unlock accounts, reset PINs, view login logs
- 🗄️ **SQLite database** — Data persists permanently across sessions
- 🎨 **Rich CLI** — Colored tables and styled menus

---

## 📁 Project Structure

```
pybank/
├── main.py            # Entry point — run this to start
├── config.py          # Settings and email credentials
├── database.py        # Database connection and table setup
├── helpers.py         # Utility functions (PIN, amount, email input)
├── account.py         # Account class
├── bank.py            # Bank class
├── menus.py           # All CLI menus
└── email_service.py   # Email notification service
```

---

## 🚀 How to Run

**1. Clone the repo**
```bash
git clone https://github.com/PushpaSaysHi/python-banking-system.git
cd python-banking-system
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
python main.py
```

---

## 📧 Email Setup (Optional)

To enable email notifications, open `config.py` and update:

```python
EMAIL_ENABLED  = True
EMAIL_ADDRESS  = "your_gmail@gmail.com"
EMAIL_PASSWORD = "your_app_password"   # Google App Password (not your Gmail password)
```

To get an App Password:
1. Enable 2-Step Verification at [myaccount.google.com/security](https://myaccount.google.com/security)
2. Create an App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

---

## 🏦 Account Types & Interest Rates

| Type     | Interest Rate |
|----------|--------------|
| Kids     | 5.0% / month |
| Student  | 3.5% / month |
| Adult    | 2.0% / month |
| Veteran  | 4.0% / month |
| Business | 1.5% / month |

---

## 🔐 Admin Panel

Access the admin panel from the main menu with your admin password (default: `admin1234`).

Admin can:
- View all accounts
- Unlock locked accounts
- Reset any account's PIN
- View login activity logs
- Delete accounts

---

## 🛠️ Built With

- **Python 3** — Core language
- **SQLite3** — Built-in database (no installation needed)
- **Rich** — Beautiful CLI formatting
- **Hashlib** — PIN hashing (SHA-256)
- **Smtplib** — Email notifications
- **Getpass** — Secure PIN input

---

## 📸 Screenshots

### Main Menu
```
╭─────────────────────────────────╮
│       🏦 Welcome to PyBank      │
│      Your simple Python bank    │
╰─────────────────────────────────╯
  1. Login
  2. Create account
  3. List all accounts
  4. Search account by name
  5. Admin
  6. Exit
```

### Transaction History
```
┌─────────────────────────────────────────────────────┐
│         Transactions — John (12345678)              │
├──────────────────┬──────────────────┬───────────────┤
│ Date             │ Type             │ Amount        │
├──────────────────┼──────────────────┼───────────────┤
│ 2024-01-01 10:00 │ Initial deposit  │ +$500.00      │
│ 2024-01-02 11:00 │ Deposit          │ +$200.00      │
│ 2024-01-03 12:00 │ Withdrawal       │ -$100.00      │
└──────────────────┴──────────────────┴───────────────┘
  Current Balance: $600.00
```

---

## 👤 Author

**Puspa Narayan Mandal**
- GitHub: [@PushpaSaysHi](https://github.com/PushpaSaysHi)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
