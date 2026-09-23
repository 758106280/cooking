import hashlib
import hmac
import secrets

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240_000)
    return f"pbkdf2_sha256$240000${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt_hex, digest_hex = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds)
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int) -> str:
    serializer = URLSafeTimedSerializer(settings.secret_key, salt="cooking-access-token")
    return serializer.dumps({"user_id": user_id})


def verify_access_token(token: str) -> int | None:
    serializer = URLSafeTimedSerializer(settings.secret_key, salt="cooking-access-token")
    try:
        payload = serializer.loads(token, max_age=settings.access_token_max_age)
    except (BadSignature, SignatureExpired, TypeError, ValueError):
        return None

    user_id = payload.get("user_id") if isinstance(payload, dict) else None
    return user_id if isinstance(user_id, int) else None
