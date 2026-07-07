"""Minimal password hashing + bearer-token helpers for the staff login flow.

Prototype scope only: a real rollout would sit behind IDBI's staff SSO/AD, not
a local password table. PBKDF2 with a fixed salt is good enough to avoid
storing staff passwords in plaintext for a hackathon demo without adding a
new dependency (passlib/bcrypt) just for this.
"""
import base64
import hashlib
import hmac

_SALT = b"saarthi-staff-proto-salt"
_TOKEN_PREFIX = "saarthi-staff:"


def hash_password(password: str) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), _SALT, 100_000)
    return digest.hex()


def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)


def issue_staff_token(staff_id: str) -> str:
    return base64.b64encode(f"{_TOKEN_PREFIX}{staff_id}".encode()).decode()


def staff_id_from_token(token: str) -> str | None:
    try:
        decoded = base64.b64decode(token.encode()).decode()
    except Exception:
        return None
    if not decoded.startswith(_TOKEN_PREFIX):
        return None
    return decoded[len(_TOKEN_PREFIX):]
