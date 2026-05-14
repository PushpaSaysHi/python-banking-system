"""
main.py — Entry point for PyBank
"""

from bank import Bank
from menus import main_menu


def main():
    bank = Bank("PyBank")
    main_menu(bank)


if __name__ == "__main__":
    main()
