"""
bank.py — Bank class
"""

import datetime
import random
from database import get_connection, setup_database
from account import Account
from helpers import hash_pin, get_pin
from email_service import (
    notify_account_created, notify_transfer_sent,
    notify_transfer_received, notify_account_locked
)


class Bank:
    def __init__(self, name: str):
        self.name = name
        setup_database()
        count = self._count_accounts()
        if count > 0:
            print(f"✅ Loaded {count} account(s) from saved data.\n")

    # ── Internal helpers ─────────────────────────────────────

    def _count_accounts(self) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM accounts")
        total = cursor.fetchone()["total"]
        conn.close()
        return total

    def load_account(self, account_id: str):
        """Load a single account from the DB by ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE account_id = ?", (account_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return Account(
            account_id         = row["account_id"],
            owner_name         = row["owner_name"],
            pin_hash           = row["pin_hash"],
            email              = row["email"],
            account_type       = row["account_type"],
            interest_rate      = row["interest_rate"],
            balance            = row["balance"],
            last_interest_date = row["last_interest_date"],
            is_locked          = row["is_locked"],
            failed_attempts    = row["failed_attempts"],
        )

    def _log_login(self, account_id: str, status: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO login_log (account_id, date, status)
            VALUES (?, ?, ?)
        """, (account_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), status))
        conn.commit()
        conn.close()

    # ── Account creation ─────────────────────────────────────

    def create_account(self, owner_name, pin, email, account_type, interest_rate, initial_balance=0):
        # Generate a unique ID
        while True:
            account_id = str(random.randint(10000000, 99999999))
            if not self.load_account(account_id):
                break

        today = datetime.date.today().isoformat()
        conn  = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO accounts
            (account_id, owner_name, pin_hash, email, account_type,
             interest_rate, balance, last_interest_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (account_id, owner_name, hash_pin(pin), email,
              account_type, interest_rate, initial_balance, today))

        if initial_balance > 0:
            cursor.execute("""
                INSERT INTO transactions (account_id, date, type, amount)
                VALUES (?, ?, ?, ?)
            """, (account_id,
                  datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                  "Initial deposit", initial_balance))

        conn.commit()
        conn.close()

        print(f"\n🏦 Account created for {owner_name}!")
        print(f"   Account ID   : {account_id}")
        print(f"   Account Type : {account_type}")
        print(f"   Interest Rate: {interest_rate}% per month")
        print(f"   Balance      : ${initial_balance:.2f}")
        if email:
            print(f"   Email        : {email}")
        print(f"   Keep your PIN safe — it cannot be recovered!\n")

        notify_account_created(email, owner_name, account_id, account_type)
        return account_id

    # ── Login ────────────────────────────────────────────────

    def login(self, account_id: str):
        acc = self.load_account(account_id)
        if not acc:
            print(f"❌ No account found with ID: {account_id}")
            return None

        if acc.is_locked:
            print("🔒 This account is locked due to too many failed attempts.")
            print("   Please contact the admin to unlock it.")
            return None

        for attempt in range(3):
            pin = get_pin(f"Enter PIN (attempt {attempt + 1}/3): ")
            if acc.verify_pin(pin):
                # reset failed attempts on success
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE accounts SET failed_attempts = 0 WHERE account_id = ?",
                    (account_id,)
                )
                conn.commit()
                conn.close()
                self._log_login(account_id, "SUCCESS")
                print(f"\n✅ Welcome back, {acc.owner_name}!")
                return acc
            else:
                print("❌ Incorrect PIN.")
                self._log_login(account_id, "FAILED")

        # lock the account after 3 failed attempts
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE accounts SET is_locked = 1, failed_attempts = 3 WHERE account_id = ?",
            (account_id,)
        )
        conn.commit()
        conn.close()

        notify_account_locked(acc.email, acc.owner_name)
        print("🔒 Too many failed attempts. Account is now locked.")
        return None

    # ── Transfer ─────────────────────────────────────────────

    def transfer(self, sender: Account, to_id: str, amount: float) -> bool:
        receiver = self.load_account(to_id)
        if not receiver:
            print(f"❌ No account found with ID: {to_id}")
            return False
        if sender.account_id == to_id:
            print("❌ Cannot transfer to your own account.")
            return False
        if sender.balance < amount:
            print(f"❌ Insufficient funds. Available: ${sender.balance:.2f}")
            return False

        sender.balance   -= amount
        receiver.balance += amount

        conn   = get_connection()
        cursor = conn.cursor()
        now    = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        cursor.execute("UPDATE accounts SET balance = ? WHERE account_id = ?",
                       (sender.balance,   sender.account_id))
        cursor.execute("UPDATE accounts SET balance = ? WHERE account_id = ?",
                       (receiver.balance, receiver.account_id))

        cursor.execute("""
            INSERT INTO transactions (account_id, date, type, amount)
            VALUES (?, ?, ?, ?)
        """, (sender.account_id,   now, f"Transfer to {to_id}",              -amount))
        cursor.execute("""
            INSERT INTO transactions (account_id, date, type, amount)
            VALUES (?, ?, ?, ?)
        """, (receiver.account_id, now, f"Transfer from {sender.account_id}", amount))

        conn.commit()
        conn.close()

        print(f"✅ Transferred ${amount:.2f} to account {to_id}.")
        notify_transfer_sent(sender.email,   sender.owner_name,   amount, to_id,              sender.balance)
        notify_transfer_received(receiver.email, receiver.owner_name, amount, sender.account_id, receiver.balance)
        return True

    # ── List accounts ────────────────────────────────────────

    def list_accounts(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT account_id, owner_name, account_type, balance, is_locked FROM accounts")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("  No accounts yet.")
            return

        from rich.table import Table
        from rich.console import Console
        from rich.text import Text
        console = Console()

        table = Table(title=f"{self.name} — All Accounts", style="cyan")
        table.add_column("Account ID",   style="yellow")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Balance",      justify="right", style="green")
        table.add_column("Status")

        for row in rows:
            status = Text("🔒 Locked", style="red") if row["is_locked"] else Text("✅ Active", style="green")
            table.add_row(
                row["account_id"],
                row["owner_name"],
                row["account_type"],
                f"${row['balance']:.2f}",
                status
            )

        console.print(table)

    # ── Close account ────────────────────────────────────────

    def close_account(self, acc: Account) -> bool:
        if acc.balance > 0:
            print(f"⚠️  Account still has ${acc.balance:.2f} in it.")
            confirm = input("Withdraw remaining balance before closing? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("❌ Account closure cancelled.")
                return False
            print(f"💸 ${acc.balance:.2f} has been returned to {acc.owner_name}.")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE account_id = ?", (acc.account_id,))
        cursor.execute("DELETE FROM login_log    WHERE account_id = ?", (acc.account_id,))
        cursor.execute("DELETE FROM accounts     WHERE account_id = ?", (acc.account_id,))
        conn.commit()
        conn.close()

        print(f"✅ Account {acc.account_id} has been closed.")
        return True

    # ── Admin: unlock account ────────────────────────────────

    def unlock_account(self, account_id: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE accounts SET is_locked = 0, failed_attempts = 0 WHERE account_id = ?",
            (account_id,)
        )
        conn.commit()
        conn.close()
        print(f"✅ Account {account_id} has been unlocked.")

    # ── Login activity log ───────────────────────────────────

    def show_login_log(self, account_id: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, status FROM login_log
            WHERE account_id = ?
            ORDER BY id DESC
            LIMIT 20
        """, (account_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("  No login history.")
            return

        from rich.table import Table
        from rich.console import Console
        from rich.text import Text
        console = Console()

        table = Table(title=f"Login Log — {account_id}")
        table.add_column("Date",   style="cyan")
        table.add_column("Status")

        for row in rows:
            status = Text("✅ Success", style="green") if row["status"] == "SUCCESS" else Text("❌ Failed", style="red")
            table.add_row(row["date"], status)

        console.print(table)
