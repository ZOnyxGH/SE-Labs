# Static analysis findings

The **before** findings below were collected from the original `bank_account_system.py` using Pylint 4.1.3, Bandit 1.9.4, and Flake8 7.4.1 on Python 3.14.4. Line numbers refer to that original file. The **after** reports are saved as `pylint_report.txt`, `bandit_report.txt`, and `flake8_report.txt`; the original reports have `_before` in their filenames.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shell command uses an untrusted filename (B605) | Security - High | 55 | `os.system` passed the backup filename to a shell command, allowing shell metacharacters in the filename to be interpreted. | Removed shell execution and used a normal Python status message after writing the backup. |
| Weak PIN digest (B324) | Security - High | 44 | MD5 is unsuitable for protecting PINs because it is fast and unsalted. | Replaced MD5 with PBKDF2-HMAC-SHA256 and a fresh random salt per PIN. |
| Dynamic code execution (B307) | Security - Medium | 39 | `eval` executed an arbitrary caller-supplied expression to calculate a bonus. | Changed the function to accept a numeric bonus rate and calculate the bonus directly. |
| Predictable temporary PIN (B311) | Security - Low | 48 | `random.randint` is intended for simulation and can be predictable. | Used `secrets.randbelow` to generate a cryptographically secure four-digit PIN. |
| Broad exception swallowed (B110 / E722) | Reliability / Style | 22 | A bare `except` followed by `pass` hid every deposit error and gave no indication that the operation failed. | Removed the exception handler and return `False` for a missing account or invalid amount. |
| Shared mutable default (W0102) | Correctness | 11 | `transactions=[]` reused the same list between calls. | Changed the default to `None` and create a new list for each call. |
| Unused withdrawal fee and insufficient-fee check | Correctness / Quality | 27 | `service_fee` was assigned but never used; the old check could permit a withdrawal that left less than the fee. | Validate funds for the withdrawal plus the fee, then subtract the total. |
| Style and maintainability findings (Pylint / Flake8) | Style / Quality | 6, 11, 15, 28, 38, 70 | Unused import, non-snake-case name, long line, `== None`, unused local variables, and missing final newline. | Removed unused code, adopted snake_case, used `is None`, formatted the message, and added a final newline. |
| Hard-coded token (B105) | Security - Low | 59 | A token-like secret was embedded in source code. | Removed the demonstration token instead of printing a fake secret. |

## Verification

- Pylint: **10.00/10** after the changes.
- Bandit: **No issues identified** after the changes.
- Flake8: **No findings** after the changes.
- The program was run before and after the changes; the final run created a JSON backup and completed the account demonstration.
