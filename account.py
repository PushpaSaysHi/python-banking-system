"""
account.py — Account class
"""

import datetime
from database import get_connection
from helpers import hash_pin
from email_service import (
    notify_deposit, notify_withdrawal,
    notify_pin_changed
)


class Account:
    def __init__(self, account_id, owner_name, pin_hash, email,
                 account_type, interest_rate, balance=0,
                 last_interest_date=None, is_locked=0, failed_attempts=0):
        self.account_id         = account_id
        self.owner_name         = owner_name
        self.pin_hash           = pin_hash
        self.email              = email
        self.account_type       = account_type
        self.interest_rate      = interest_rate
        self.balance            = balance
        self.last_interest_date = last_interest_date or datetime.date.today().isoformat()
        self.is_locked          = bool(is_locked)
        self.failed_attempts    = failed_attempts

    # ── PIN ─────────────────────────────────────────────────

    def verify_pin(self, pin: str) -> bool:
        return hash_pin(pin) == self.pin_hash

    def change_pin(self, new_pin: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE accounts SET pin_hash = ? WHERE account_id = ?",
            (hash_pin(new_pin), self.account_id)
        )
        conn.commit()
        conn.close()
        self.pin_hash = hash_pin(new_pin)
        notify_pin_changed(self.email, self.owner_name)
        print("✅ PIN changed successfully.")

    # ── Internal helpers ─────────────────────────────────────

    def _record_transaction(self, cursor, transaction_type: str, amount: float):
        cursor.execute("""
            INSERT INTO transactions (account_id, date, type, amount)
            VALUES (?, ?, ?, ?)
        """, (
            self.account_id,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            transaction_type,
            amount
        ))

    def _save_balance(self, cursor):
        cursor.execute("""
            UPDATE accounts
            SET balance = ?, last_interest_date = ?
            WHERE account_id = ?
        """, (self.balance, self.last_interest_date, self.account_id))

    # ── Transactions ─────────────────────────────────────────

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            print("❌ Deposit amount must be positive.")
            return False

        self.balance += amount
        conn = get_connection()
        cursor = conn.cursor()
        self._save_balance(cursor)
        self._record_transaction(cursor, "Deposit", amount)
        conn.commit()
        conn.close()

        print(f"✅ Deposited ${amount:.2f}. New balance: ${self.balance:.2f}")
        notify_deposit(self.email, self.owner_name, amount, self.balance)
        return True

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            print("❌ Withdrawal amount must be positive.")
            return False
        if amount > self.balance:
            print(f"❌ Insufficient funds. Available: ${self.balance:.2f}")
            return False

        self.balance -= amount
        conn = get_connection()
        cursor = conn.cursor()
        self._save_balance(cursor)
        self._record_transaction(cursor, "Withdrawal", -amount)
        conn.commit()
        conn.close()

        print(f"✅ Withdrew ${amount:.2f}. New balance: ${self.balance:.2f}")
        notify_withdrawal(self.email, self.owner_name, amount, self.balance)
        return True

    def apply_interest(self) -> bool:
        today = datetime.date.today()
        last  = datetime.date.fromisoformat(self.last_interest_date)
        months_passed = (today.year - last.year) * 12 + (today.month - last.month)

        if months_passed < 1:
            days_left = (last.replace(month=last.month % 12 + 1, day=1) - today).days
            print(f"  ⏳ Next interest in ~{days_left} day(s).")
            return False

        total_interest = 0
        for _ in range(months_passed):
            interest = round(self.balance * (self.interest_rate / 100), 2)
            self.balance   += interest
            total_interest += interest

        self.last_interest_date = today.isoformat()

        conn = get_connection()
        cursor = conn.cursor()
        self._save_balance(cursor)
        self._record_transaction(cursor, "Interest Payment", total_interest)
        conn.commit()
        conn.close()

        print(f"✅ ${total_interest:.2f} interest applied ({self.interest_rate}% x {months_passed} month(s)).")
        print(f"   New balance: ${self.balance:.2f}")
        return True

    # ── History ──────────────────────────────────────────────

    def get_history(self, limit: int = None):
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT date, type, amount FROM transactions
            WHERE account_id = ?
            ORDER BY id DESC
        """
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, (self.account_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("  No transactions yet.")
            return

        from rich.table import Table
        from rich.console import Console
        from rich.text import Text
        console = Console()

        table = Table(title=f"Transactions — {self.owner_name} ({self.account_id})")
        table.add_column("Date",   style="cyan")
        table.add_column("Type",   style="white")
        table.add_column("Amount", justify="right")

        for row in rows:
            amount_str = f"+${row['amount']:.2f}" if row["amount"] >= 0 else f"-${abs(row['amount']):.2f}"
            color = "green" if row["amount"] >= 0 else "red"
            table.add_row(row["date"], row["type"], Text(amount_str, style=color))

        console.print(table)
        print(f"  Current Balance: ${self.balance:.2f}\n")
