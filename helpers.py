"""
helpers.py — Small reusable utility functions
"""

import hashlib
from getpass import getpass
from config import ACCOUNT_TYPES


def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()


def get_pin(prompt="Enter PIN: ") -> str:
    """Ask for a 4-digit PIN (input hidden)."""
    while True:
        pin = getpass(prompt).strip()
        if pin.isdigit() and len(pin) == 4:
            return pin
        print("❌ PIN must be exactly 4 digits.")


def get_amount(prompt: str) -> float:
    """Ask for a positive dollar amount."""
    while True:
        try:
            amount = float(input(prompt))
            if amount < 0:
                print("❌ Amount cannot be negative.")
                continue
            return amount
        except ValueError:
            print("❌ Please enter a valid number.")


def get_email(prompt="Enter your email (or press Enter to skip): ") -> str:
    """Ask for an optional email address."""
    while True:
        email = input(prompt).strip()
        if email == "":
            return ""
        if "@" in email and "." in email:
            return email
        print("❌ Invalid email address. Try again or press Enter to skip.")


def pick_account_type() -> tuple:
    """Show account type menu and return (name, rate)."""
    from rich.table import Table
    from rich.console import Console
    console = Console()

    table = Table(title="Account Types", style="cyan")
    table.add_column("No.", style="bold yellow")
    table.add_column("Type")
    table.add_column("Interest Rate", style="green")

    for key, val in ACCOUNT_TYPES.items():
        table.add_row(key, val["name"], f"{val['rate']}% / month")

    console.print(table)

    while True:
        choice = input("  Enter choice (1-5): ").strip()
        if choice in ACCOUNT_TYPES:
            return ACCOUNT_TYPES[choice]["name"], ACCOUNT_TYPES[choice]["rate"]
        print("❌ Invalid choice.")
