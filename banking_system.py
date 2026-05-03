"""
Interactive Banking System in Python
With login/signup, account types, interest rates, and persistent storage.
"""

import datetime
import random
import json
import os
import hashlib


DATA_FILE = "bank_data.json"

# Interest rates for each account type
ACCOUNT_TYPES = {
    "1": {"name": "Kids",     "rate": 5.0},
    "2": {"name": "Student",  "rate": 3.5},
    "3": {"name": "Adult",    "rate": 2.0},
    "4": {"name": "Veteran",  "rate": 4.0},
    "5": {"name": "Business", "rate": 1.5},
}


def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


def get_pin(prompt="Enter PIN: "):
    while True:
        pin = input(prompt).strip()
        if pin.isdigit() and len(pin) == 4:
            return pin
        print("❌ PIN must be exactly 4 digits.")


def get_amount(prompt):
    while True:
        try:
            amount = float(input(prompt))
            return amount
        except ValueError:
            print("❌ Please enter a valid number.")


def pick_account_type():
    """Show account type menu and return the chosen type name and rate."""
    print("\n  Select account type:")
    for key, val in ACCOUNT_TYPES.items():
        print(f"    {key}. {val['name']:<10} — {val['rate']}% interest/month")
    while True:
        choice = input("  Enter choice (1-5): ").strip()
        if choice in ACCOUNT_TYPES:
            return ACCOUNT_TYPES[choice]["name"], ACCOUNT_TYPES[choice]["rate"]
        print("❌ Invalid choice.")


class Account:
    def __init__(self, account_id, owner_name, pin_hash, account_type, interest_rate,
                 initial_balance=0, transactions=None, last_interest_date=None):
        self.account_id = account_id
        self.owner_name = owner_name
        self.pin_hash = pin_hash
        self.account_type = account_type
        self.interest_rate = interest_rate
        self.balance = initial_balance
        self.transactions = transactions or []
        self.last_interest_date = last_interest_date or datetime.date.today().isoformat()

        if initial_balance > 0 and not self.transactions:
            self._record_transaction("Initial deposit", initial_balance)

    def verify_pin(self, pin):
        return hash_pin(pin) == self.pin_hash

    def deposit(self, amount):
        if amount <= 0:
            print("❌ Deposit amount must be positive.")
            return False
        self.balance += amount
        self._record_transaction("Deposit", amount)
        print(f"✅ Deposited ${amount:.2f}. New balance: ${self.balance:.2f}")
        return True

    def withdraw(self, amount):
        if amount <= 0:
            print("❌ Withdrawal amount must be positive.")
            return False
        if amount > self.balance:
            print(f"❌ Insufficient funds. Available: ${self.balance:.2f}")
            return False
        self.balance -= amount
        self._record_transaction("Withdrawal", -amount)
        print(f"✅ Withdrew ${amount:.2f}. New balance: ${self.balance:.2f}")
        return True

    def apply_interest(self):
        """Apply monthly interest if a month has passed since last applied."""
        today = datetime.date.today()
        last = datetime.date.fromisoformat(self.last_interest_date)
        months_passed = (today.year - last.year) * 12 + (today.month - last.month)

        if months_passed < 1:
            days_left = (last.replace(month=last.month % 12 + 1, day=1) - today).days
            print(f"  ⏳ Next interest in ~{days_left} day(s).")
            return False

        # Apply interest for each month passed
        total_interest = 0
        for _ in range(months_passed):
            interest = round(self.balance * (self.interest_rate / 100), 2)
            self.balance += interest
            total_interest += interest

        self.last_interest_date = today.isoformat()
        self._record_transaction("Interest Payment", total_interest)
        print(f"✅ ${total_interest:.2f} interest applied ({self.interest_rate}% x {months_passed} month(s)).")
        print(f"   New balance: ${self.balance:.2f}")
        return True

    def get_history(self):
        if not self.transactions:
            print("  No transactions yet.")
            return
        print(f"\n📄 Transaction History — {self.owner_name} (ID: {self.account_id})")
        print("-" * 55)
        for t in self.transactions:
            sign = "+" if t["amount"] >= 0 else ""
            print(f"  {t['date']}  |  {t['type']:<20}  |  {sign}${t['amount']:.2f}")
        print("-" * 55)
        print(f"  Current Balance: ${self.balance:.2f}\n")

    def _record_transaction(self, transaction_type, amount):
        self.transactions.append({
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "type": transaction_type,
            "amount": amount
        })

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "owner_name": self.owner_name,
            "pin_hash": self.pin_hash,
            "account_type": self.account_type,
            "interest_rate": self.interest_rate,
            "balance": self.balance,
            "transactions": self.transactions,
            "last_interest_date": self.last_interest_date
        }


class Bank:
    def __init__(self, name):
        self.name = name
        self.accounts = {}
        self.load()

    def create_account(self, owner_name, pin, account_type, interest_rate, initial_balance=0):
        while True:
            account_id = str(random.randint(10000000, 99999999))
            if account_id not in self.accounts:
                break

        account = Account(account_id, owner_name, hash_pin(pin),
                          account_type, interest_rate, initial_balance)
        self.accounts[account_id] = account
        self.save()
        print(f"\n🏦 Account created for {owner_name}!")
        print(f"   Account ID   : {account_id}")
        print(f"   Account Type : {account_type}")
        print(f"   Interest Rate: {interest_rate}% per month")
        print(f"   Balance      : ${initial_balance:.2f}")
        print(f"   Keep your PIN safe — it cannot be recovered!\n")
        return account_id

    def login(self, account_id):
        acc = self.accounts.get(account_id)
        if not acc:
            print(f"❌ No account found with ID: {account_id}")
            return None

        for attempt in range(3):
            pin = get_pin(f"Enter PIN (attempt {attempt + 1}/3): ")
            if acc.verify_pin(pin):
                print(f"\n✅ Welcome back, {acc.owner_name}!")
                return acc
            else:
                print("❌ Incorrect PIN.")

        print("🔒 Too many failed attempts. Access denied.")
        return None

    def transfer(self, sender, to_id, amount):
        receiver = self.accounts.get(to_id)
        if not receiver:
            print(f"❌ No account found with ID: {to_id}")
            return False
        if sender.balance < amount:
            print(f"❌ Insufficient funds. Available: ${sender.balance:.2f}")
            return False
        sender.balance -= amount
        sender._record_transaction(f"Transfer to {to_id}", -amount)
        receiver.balance += amount
        receiver._record_transaction(f"Transfer from {sender.account_id}", amount)
        self.save()
        print(f"✅ Transferred ${amount:.2f} to account {to_id}.")
        return True

    def list_accounts(self):
        if not self.accounts:
            print("  No accounts yet.")
            return
        print(f"\n{'='*45}")
        print(f"  {self.name} — All Accounts")
        print(f"{'='*45}")
        for acc_id, acc in self.accounts.items():
            print(f"  ID: {acc_id}  |  {acc.owner_name:<20}  |  {acc.account_type}")
        print(f"{'='*45}\n")

    def close_account(self, acc):
        if acc.balance > 0:
            print(f"⚠️  Account still has ${acc.balance:.2f} in it.")
            confirm = input("Withdraw remaining balance before closing? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("❌ Account closure cancelled.")
                return False
            print(f"💸 ${acc.balance:.2f} has been returned to {acc.owner_name}.")

        del self.accounts[acc.account_id]
        self.save()
        print(f"✅ Account {acc.account_id} has been closed.")
        return True

    def save(self):
        data = {
            "bank_name": self.name,
            "accounts": {acc_id: acc.to_dict() for acc_id, acc in self.accounts.items()}
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if not os.path.exists(DATA_FILE):
            return
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        for acc_id, acc_data in data["accounts"].items():
            self.accounts[acc_id] = Account(
                account_id=acc_data["account_id"],
                owner_name=acc_data["owner_name"],
                pin_hash=acc_data["pin_hash"],
                account_type=acc_data["account_type"],
                interest_rate=acc_data["interest_rate"],
                initial_balance=acc_data["balance"],
                transactions=acc_data["transactions"],
                last_interest_date=acc_data.get("last_interest_date")
            )
        print(f"✅ Loaded {len(self.accounts)} account(s) from saved data.\n")


def account_menu(bank, acc):
    while True:
        print(f"\n{'='*40}")
        print(f"  👤 {acc.owner_name} | {acc.account_type} Account")
        print(f"  💰 Balance: ${acc.balance:.2f}")
        print(f"{'='*40}")
        print("  1. Deposit")
        print("  2. Withdraw")
        print("  3. Transfer")
        print("  4. Transaction history")
        print("  5. Apply interest")
        print("  6. Account info")
        print("  7. Close account")
        print("  8. Log out")

        choice = input("\nEnter choice (1-8): ").strip()

        if choice == "1":
            amount = get_amount("Enter deposit amount: $")
            acc.deposit(amount)
            bank.save()

        elif choice == "2":
            amount = get_amount("Enter withdrawal amount: $")
            acc.withdraw(amount)
            bank.save()

        elif choice == "3":
            to_id = input("Enter RECIPIENT account ID: ").strip()
            amount = get_amount("Enter transfer amount: $")
            bank.transfer(acc, to_id, amount)

        elif choice == "4":
            acc.get_history()

        elif choice == "5":
            acc.apply_interest()
            bank.save()

        elif choice == "6":
            print(f"\n📋 Account Info")
            print(f"   Name          : {acc.owner_name}")
            print(f"   Account ID    : {acc.account_id}")
            print(f"   Account Type  : {acc.account_type}")
            print(f"   Interest Rate : {acc.interest_rate}% per month")
            print(f"   Balance       : ${acc.balance:.2f}")
            print(f"   Last Interest : {acc.last_interest_date}\n")

        elif choice == "7":
            confirm = input(f"Are you sure you want to close this account? (yes/no): ").strip().lower()
            if confirm == "yes":
                bank.close_account(acc)
                print("👋 Account closed. Logging out...")
                return

        elif choice == "8":
            print(f"👋 Logged out of {acc.owner_name}'s account.")
            return

        else:
            print("❌ Invalid choice. Please enter a number between 1 and 8.")


def main():
    bank = Bank("PyBank")

    while True:
        print("\n" + "=" * 40)
        print("   Welcome to PyBank 🏦")
        print("=" * 40)
        print("  1. Login")
        print("  2. Create account")
        print("  3. List all accounts")
        print("  4. Exit")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            acc_id = input("Enter your account ID: ").strip()
            acc = bank.login(acc_id)
            if acc:
                account_menu(bank, acc)

        elif choice == "2":
            name = input("Enter your name: ").strip()
            pin  = get_pin("Set a 4-digit PIN: ")
            confirm = get_pin("Confirm PIN: ")
            if pin != confirm:
                print("❌ PINs do not match. Account not created.")
                continue
            account_type, interest_rate = pick_account_type()
            bal = get_amount("Enter initial deposit (or 0): $")
            bank.create_account(name, pin, account_type, interest_rate, bal)

        elif choice == "3":
            bank.list_accounts()

        elif choice == "4":
            print("\n👋 Thanks for using PyBank. Goodbye!\n")
            break

        else:
            print("❌ Invalid choice. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    main()
