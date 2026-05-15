import argparse
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import async_session
from app.models import User


async def create_admin(username: str, password: str) -> None:
    if not username.strip():
        raise ValueError("El username no puede estar vacío")
    if not password:
        raise ValueError("El password no puede estar vacío")
    if len(password.encode("utf-8")) > 72:
        raise ValueError("El password no puede superar 72 bytes para bcrypt")

    async with async_session() as db:
        result = await db.execute(select(User).where(User.username == username))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ValueError(f"Ya existe un usuario con username '{username}'")

        user = User(
            username=username,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
        db.add(user)
        await db.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crea el usuario admin inicial")
    parser.add_argument("--username", required=True, help="Username del admin")
    parser.add_argument("--password", required=True, help="Password del admin")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(create_admin(args.username, args.password))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    print(f"Admin '{args.username}' creado correctamente")
