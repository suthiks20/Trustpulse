"""One-off admin seed: hashes ADMIN_PASSWORD from .env with argon2 and writes
ADMIN_PASSWORD_HASH back into .env. Run once: `python scripts/seed_admin.py`.

Never prints the password or hash to stdout.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402
from app.shared.security import hash_password  # noqa: E402

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def main() -> None:
    settings = get_settings()
    if not settings.ADMIN_PASSWORD:
        print("ADMIN_PASSWORD is not set in .env — nothing to seed.")
        return

    password_hash = hash_password(settings.ADMIN_PASSWORD)

    text = ENV_PATH.read_text()
    if "ADMIN_PASSWORD_HASH=" in text:
        text = re.sub(r"^ADMIN_PASSWORD_HASH=.*$", f"ADMIN_PASSWORD_HASH={password_hash}", text, flags=re.MULTILINE)
    else:
        text = text.rstrip("\n") + f"\nADMIN_PASSWORD_HASH={password_hash}\n"
    text = re.sub(r"^ADMIN_PASSWORD=.*$\n?", "", text, flags=re.MULTILINE)
    ENV_PATH.write_text(text)

    print(f"Admin seeded for {settings.ADMIN_EMAIL}. ADMIN_PASSWORD_HASH written to .env, plaintext removed.")


if __name__ == "__main__":
    main()
