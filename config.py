import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    BOT_TOKEN: str
    ADMIN_CHAT_ID: int
    ADMIN_IDS: list[int]
    DATABASE_PATH: str


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        print("[WARNING] BOT_TOKEN is empty! Please set it in .env file.")

    raw_admin_chat_id = os.getenv("ADMIN_CHAT_ID", "0").strip()
    try:
        admin_chat_id = int(raw_admin_chat_id)
    except ValueError:
        admin_chat_id = 0

    raw_admins = os.getenv("ADMIN_IDS", "").strip()
    admin_ids: list[int] = []
    if raw_admins:
        for item in raw_admins.split(","):
            item = item.strip()
            if item.lstrip("-").isdigit():
                admin_ids.append(int(item))

    db_path = os.getenv("DATABASE_PATH", "shop.db").strip()

    return Config(
        BOT_TOKEN=token,
        ADMIN_CHAT_ID=admin_chat_id,
        ADMIN_IDS=admin_ids,
        DATABASE_PATH=db_path,
    )


config = load_config()
