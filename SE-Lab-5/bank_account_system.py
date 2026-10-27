"""Manage a small in-memory bank account ledger."""

import hashlib
import json
import secrets

ACCOUNT_DATA = {}


def create_account(acc_id, name, initial_deposit=0, transactions=None):
    """Create an account and optionally append a creation event."""
    if acc_id in ACCOUNT_DATA:
        return False
    if initial_deposit < 0:
        return False
    ACCOUNT_DATA[acc_id] = {"name": name, "balance": initial_deposit}
    if transactions is None:
        transactions = []
    transactions.append(
        f"Created {acc_id} with initial balance {initial_deposit}"
    )
    return True


def deposit(acc_id, amount):
    """Deposit a positive amount; return whether the operation succeeded."""
    account = ACCOUNT_DATA.get(acc_id)
    if account is None or amount <= 0:
        return False
    account["balance"] += amount
    return True


def withdraw(acc_id, amount):
    """Withdraw an amount plus the service fee when funds are sufficient."""
    service_fee = 2.50
    account = ACCOUNT_DATA.get(acc_id)
    if account is None or amount <= 0:
        return False
    total = amount + service_fee
    if account["balance"] < total:
        return False
    account["balance"] -= total
    return True


def compute_bonus(acc_id, rate):
    """Compute a bonus from a numeric rate without evaluating code."""
    account = ACCOUNT_DATA.get(acc_id)
    if account is None or not 0 <= rate <= 1:
        return 0
    return account["balance"] * rate


def get_hash(pin):
    """Return a salted PBKDF2 digest for a PIN."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, 200_000)
    return f"{salt.hex()}${digest.hex()}"


def generate_temp_pin():
    """Generate a four-digit temporary PIN using a secure random source."""
    return secrets.randbelow(9000) + 1000


def backup_data(filename="backup.txt"):
    """Write the account ledger to a JSON backup file."""
    with open(filename, "w", encoding="utf-8") as backup_file:
        json.dump(ACCOUNT_DATA, backup_file, indent=2)
    print(f"Backup complete: {filename}")


def main():
    """Run a small demonstration of the account operations."""
    create_account("A01", "Alice", 1000)
    deposit("A01", 500)
    withdraw("A01", 200)
    print("Bonus:", compute_bonus("A01", 0.05))
    print("PIN Hash:", get_hash("1234"))
    print("Temp PIN:", generate_temp_pin())
    backup_data()


if __name__ == "__main__":
    main()
