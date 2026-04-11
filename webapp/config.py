import os
from werkzeug.security import generate_password_hash


def _parse_users_from_env() -> dict[str, str]:
    """Parse WEBAPP_USERS like: user1:pass1,user2:pass2"""
    raw = os.getenv("WEBAPP_USERS", "").strip()
    if not raw:
        return {
            "petp-admin": generate_password_hash("petp-admin"),
            "petp": generate_password_hash("petp"),
        }

    users_map: dict[str, str] = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair or ":" not in pair:
            continue
        username, password = pair.split(":", 1)
        username = username.strip()
        if not username:
            continue
        users_map[username] = generate_password_hash(password)

    return users_map or {
        "petp-admin": generate_password_hash("petp-admin"),
        "petp": generate_password_hash("petp"),
    }


port = int(os.getenv("PORT", "5555"))
shared_folder = os.getenv("SHARED_FOLDER", "shared")
users = _parse_users_from_env()
