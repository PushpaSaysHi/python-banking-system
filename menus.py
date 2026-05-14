"""
menus.py — All CLI menus using Rich for styling
"""

from getpass import getpass
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from helpers import get_amount, get_pin, get_email

# ── Admin password (change this to something strong!) ────────
ADMIN_PASSWORD = "admin1234"

console = Console()


# ── Reusable UI helpers ──────────────────────────────────────

def print_header(title: str, subtitle: str = ""):
    console.print(Panel(
        Text(title, justify="center", style="bold cyan"),
        subtitle=subtitle,
        border_style="cyan"
    ))


def print_menu(options: list):
    """Print a numbered menu from a list of strings."""
    for i, option in enumerate(options, 1):
        console.print(f"  [bold yellow]{i}.[/bold yellow] {option}")


def get_menu_choice(max_choice: int) -> str:
    while True:
        choice = input(f"\nEnter choice (1-{max_choice}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= max_choice:
            return choice
        print(f"❌ Please enter a number between 1 and {max_choice}.")


# ── Account menu ─────────────────────────────────────────────

def account_menu(bank, acc):
    while True:
        console.print()
        print_header(
            f"👤 {acc.owner_name}",
            subtitle=f"{acc.account_type} Account  |  Balance: ${acc.balance:.2f}"
        )
        print_menu([
            "Deposit",
            "Withdraw",
            "Transfer",
            "Transaction history",
            "Mini statement (last 5)",
            "Apply interest",
            "Change PIN",
            "Account info",
            "Login activity",
            "Close account",
            "Log out",
        ])

        choice = get_menu_choice(11)

        if choice == "1":
            amount = get_amount("Enter deposit amount: $")
            acc.deposit(amount)

        elif choice == "2":
            amount = get_amount("Enter withdrawal amount: $")
            acc.withdraw(amount)

        elif choice == "3":
            to_id  = input("Enter RECIPIENT account ID: ").strip()
            amount = get_amount("Enter transfer amount: $")
            bank.transfer(acc, to_id, amount)

        elif choice == "4":
            acc.get_history()

        elif choice == "5":
            acc.get_history(limit=5)

        elif choice == "6":
            acc.apply_interest()

        elif choice == "7":
            _change_pin_menu(acc)

        elif choice == "8":
            _show_account_info(acc)

        elif choice == "9":
            bank.show_login_log(acc.account_id)

        elif choice == "10":
            confirm = input("Are you sure you want to close this account? (yes/no): ").strip().lower()
            if confirm == "yes":
                if bank.close_account(acc):
                    print("👋 Account closed. Logging out...")
                    return

        elif choice == "11":
            console.print(f"👋 Logged out of [cyan]{acc.owner_name}[/cyan]'s account.")
            return


def _change_pin_menu(acc):
    print("\n🔑 Change PIN")
    current = get_pin("Enter current PIN: ")
    if not acc.verify_pin(current):
        print("❌ Incorrect current PIN.")
        return
    new_pin = get_pin("Enter new PIN: ")
    confirm = get_pin("Confirm new PIN: ")
    if new_pin != confirm:
        print("❌ PINs do not match.")
        return
    acc.change_pin(new_pin)


def _show_account_info(acc):
    table = Table(title="Account Info", style="cyan")
    table.add_column("Field",  style="bold yellow")
    table.add_column("Value")

    table.add_row("Name",          acc.owner_name)
    table.add_row("Account ID",    acc.account_id)
    table.add_row("Account Type",  acc.account_type)
    table.add_row("Interest Rate", f"{acc.interest_rate}% per month")
    table.add_row("Balance",       f"${acc.balance:.2f}")
    table.add_row("Last Interest", acc.last_interest_date)
    table.add_row("Email",         acc.email or "Not set")
    table.add_row("Status",        "🔒 Locked" if acc.is_locked else "✅ Active")

    console.print(table)


# ── Main menu ────────────────────────────────────────────────

def main_menu(bank):
    while True:
        console.print()
        print_header("🏦 Welcome to PyBank", subtitle="Your simple Python bank")
        print_menu([
            "Login",
            "Create account",
            "List all accounts",
            "Admin",
            "Exit",
        ])

        choice = get_menu_choice(5)

        if choice == "1":
            acc_id = input("Enter your account ID: ").strip()
            acc = bank.login(acc_id)
            if acc:
                account_menu(bank, acc)

        elif choice == "2":
            _create_account_menu(bank)

        elif choice == "3":
            bank.list_accounts()

        elif choice == "4":
            _admin_login(bank)

        elif choice == "5":
            console.print("\n👋 [cyan]Thanks for using PyBank. Goodbye![/cyan]\n")
            break


# ── Admin ────────────────────────────────────────────────────

def _admin_login(bank):
    password = getpass("Enter admin password: ")
    if password != ADMIN_PASSWORD:
        print("❌ Incorrect admin password.")
        return
    console.print("✅ [green]Admin access granted.[/green]")
    _admin_menu(bank)


def _admin_menu(bank):
    while True:
        console.print()
        print_header("🔐 Admin Panel", subtitle="PyBank Admin")
        print_menu([
            "List all accounts",
            "Unlock an account",
            "Reset account PIN",
            "View login log for account",
            "Delete account",
            "Exit admin",
        ])

        choice = get_menu_choice(6)

        if choice == "1":
            bank.list_accounts()

        elif choice == "2":
            acc_id = input("Enter account ID to unlock: ").strip()
            acc = bank.load_account(acc_id)
            if not acc:
                print(f"❌ No account found with ID: {acc_id}")
            elif not acc.is_locked:
                print("ℹ️  Account is not locked.")
            else:
                bank.unlock_account(acc_id)

        elif choice == "3":
            acc_id = input("Enter account ID: ").strip()
            acc = bank.load_account(acc_id)
            if not acc:
                print(f"❌ No account found with ID: {acc_id}")
            else:
                new_pin = get_pin("Enter new PIN for account: ")
                confirm = get_pin("Confirm new PIN: ")
                if new_pin != confirm:
                    print("❌ PINs do not match.")
                else:
                    acc.change_pin(new_pin)
                    print(f"✅ PIN reset for {acc.owner_name}.")

        elif choice == "4":
            acc_id = input("Enter account ID: ").strip()
            bank.show_login_log(acc_id)

        elif choice == "5":
            acc_id = input("Enter account ID to delete: ").strip()
            acc = bank.load_account(acc_id)
            if not acc:
                print(f"❌ No account found with ID: {acc_id}")
            else:
                confirm = input(f"Are you sure you want to delete {acc.owner_name}'s account? (yes/no): ").strip().lower()
                if confirm == "yes":
                    bank.close_account(acc)

        elif choice == "6":
            console.print("👋 [cyan]Exited admin panel.[/cyan]")
            return


def _create_account_menu(bank):
    from helpers import pick_account_type
    print("\n📝 Create New Account")
    name    = input("Enter your name: ").strip()
    if not name:
        print("❌ Name cannot be empty.")
        return
    email   = get_email("Enter your email (for notifications, or press Enter to skip): ")
    pin     = get_pin("Set a 4-digit PIN: ")
    confirm = get_pin("Confirm PIN: ")
    if pin != confirm:
        print("❌ PINs do not match. Account not created.")
        return
    account_type, interest_rate = pick_account_type()
    bal = get_amount("Enter initial deposit (or 0): $")
    bank.create_account(name, pin, email, account_type, interest_rate, bal)
