import aiosqlite
import json
from typing import Any, Optional
from config import config

DB_PATH = config.DATABASE_PATH

async def get_connection() -> aiosqlite.Connection:
    """Открывает и возвращает соединение с БД."""
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    return conn

DEFAULT_PRIVILEGES = [
    ("hero", "Hero", "", 9, "Алмазный сет Z2, инструменты Эфф. 3, 16 золотых яблок, 32 стейка", "/kit hero, /craft, /feed, /hat, /salary"),
    ("titan", "Titan", "", 18, "Алмазный сет Z3, оружие Острота 3, 24 золотых яблока, 1 тотем", "/kit titan, /enderchest, /heal, /rtp far, /salary"),
    ("prince", "Prince", "", 37, "Алмазный сет Z4, меч Острота 4, 32 золотых яблока, 2 тотема", "/kit prince, /repair, /near, /afk, /salary"),
    ("phoenix", "Phoenix", "[ХИТ]", 75, "Незеритовый сет Z3, меч Острота 4 + Огонь, 1 чар-яблоко, 2 тотема", "/kit phoenix, /nick, /invsee, /setwarp (1 варп), /salary"),
    ("overlord", "Overlord", "[ВЫБОР]", 150, "Незеритовый сет Z4, оружие Острота 5, 2 чар-яблока, 3 тотема", "/kit overlord, /fly, /repair all, /broadcast, /salary"),
    ("guardian", "Guardian", "", 284, "Незеритовый сет Z4+, инструменты Эфф. 5, 4 чар-яблока, 4 тотема", "/kit guardian, /checkban, /checkmute, /setwarp (5 варпов), /salary"),
    ("kratos", "Kratos", "", 375, "Сет Kratos, клинок Kratos X, 6 чар-яблок, 5 тотемов", "/kit kratos, /grant, /top, /setwarp (5 варпов), /salary"),
    ("phantom", "Phantom", "", 636, "Мифический сет Phantom, оружие Бога войны, 8 чар-яблок, 6 тотемов", "/kit phantom, /god, /back, /setwarp (8 варпов), /salary"),
    ("custom", "Custom", "[ТОП]", 1120, "Эксклюзивный сет Custom, спавнеры и артефакты, 12 чар-яблок", "/kit custom, /prefix, /god (+ /fly), /setwarp (12 варпов), /salary")
]

DEFAULT_SETTINGS = {
    "requisites_card_rf": "💳 Сбербанк / Тинькофф (СБП): `+7 999 000-00-00`",
    "requisites_card_eu": "🇪🇺 Карта Европы / IBAN: `EU0000000000000000`",
    "requisites_paypal": "🅿️ PayPal: `donate@fixland.net`",
    "requisites_funpay": "💸 FunPay: https://funpay.com",
    "requisites_crypto": "⚡ CryptoBot / USDT TRC-20",
    "requisites_other": "💬 Напишите напрямую администрации для обсуждения индивидуального способа",
    "support_contact": "https://t.me/Hupiiaristo",
    "unban_price": "150",
    "unmute_price": "75"
}

async def init_db() -> None:
    conn = await get_connection()
    try:
        # Пользователи
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Привилегии
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS privileges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                name TEXT NOT NULL,
                badge TEXT DEFAULT '',
                price INTEGER NOT NULL,
                kits TEXT NOT NULL,
                commands TEXT NOT NULL
            )
        """)

        # Медиа-партнёры
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS media_partners (
                user_id INTEGER PRIMARY KEY,
                channel_link TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Персонал проекта (админы, модераторы, хелперы, медиа)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS staff (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                role TEXT NOT NULL,
                added_by TEXT DEFAULT '',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Заказы и тикеты доната
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                item_type TEXT DEFAULT 'privilege',
                item_name TEXT NOT NULL,
                price INTEGER DEFAULT 0,
                mc_nickname TEXT DEFAULT '',
                pay_method TEXT NOT NULL,
                receipt_file_id TEXT DEFAULT '',
                status TEXT DEFAULT 'pending',
                helper_id INTEGER DEFAULT 0,
                helper_username TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Заявки на Хелпера / в КП
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                app_type TEXT NOT NULL,
                answers_json TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                reviewer TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Жалобы (на игроков / на команду проекта)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                complaint_type TEXT NOT NULL,
                my_nick TEXT NOT NULL,
                target_nick TEXT NOT NULL,
                incident_date TEXT NOT NULL,
                reason TEXT NOT NULL,
                evidence TEXT NOT NULL,
                additional TEXT DEFAULT '',
                status TEXT DEFAULT 'pending',
                reviewer TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Запросы на выплату / плюшки от медиа
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS media_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                request_type TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                reviewer TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Системные настройки
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Миграция: убедимся, что все колонки в tickets существуют
        async with conn.execute("PRAGMA table_info(tickets)") as cursor:
            cols = [row["name"] for row in await cursor.fetchall()]
            if "item_type" not in cols:
                await conn.execute("ALTER TABLE tickets ADD COLUMN item_type TEXT DEFAULT 'privilege'")
            if "price" not in cols:
                await conn.execute("ALTER TABLE tickets ADD COLUMN price INTEGER DEFAULT 0")
            if "mc_nickname" not in cols:
                await conn.execute("ALTER TABLE tickets ADD COLUMN mc_nickname TEXT DEFAULT ''")
            if "receipt_file_id" not in cols:
                await conn.execute("ALTER TABLE tickets ADD COLUMN receipt_file_id TEXT DEFAULT ''")
            if "helper_id" not in cols:
                await conn.execute("ALTER TABLE tickets ADD COLUMN helper_id INTEGER DEFAULT 0")
            if "helper_username" not in cols:
                await conn.execute("ALTER TABLE tickets ADD COLUMN helper_username TEXT DEFAULT ''")

        # Заполнение дефолтных привилегий
        async with conn.execute("SELECT COUNT(*) as count FROM privileges") as cursor:
            row = await cursor.fetchone()
            if row and row["count"] == 0:
                await conn.executemany("""
                    INSERT INTO privileges (code, name, badge, price, kits, commands)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, DEFAULT_PRIVILEGES)

        # Заполнение дефолтных настроек
        for key, val in DEFAULT_SETTINGS.items():
            await conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))

        await conn.commit()
    finally:
        await conn.close()

# --- Пользователи ---
async def add_user(user_id: int, username: Optional[str], full_name: str) -> None:
    conn = await get_connection()
    try:
        await conn.execute("""
            INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, full_name=excluded.full_name
        """, (user_id, username, full_name))
        await conn.commit()
    finally:
        await conn.close()

async def get_all_users() -> list[dict[str, Any]]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT * FROM users") as cursor:
            return [dict(row) for row in await cursor.fetchall()]
    finally:
        await conn.close()

# --- Персонал и Роли ---
async def set_staff_role(user_id: int, username: str, role: str, added_by: str = "") -> None:
    conn = await get_connection()
    try:
        await conn.execute("""
            INSERT INTO staff (user_id, username, role, added_by) VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET role=excluded.role, username=excluded.username, added_by=excluded.added_by
        """, (user_id, username, role, added_by))
        
        # Если роль медиа, также синхронизируем с media_partners
        if role == "media":
            await conn.execute("INSERT OR IGNORE INTO media_partners (user_id) VALUES (?)", (user_id,))
        elif role != "media":
            await conn.execute("DELETE FROM media_partners WHERE user_id = ?", (user_id,))
            
        await conn.commit()
    finally:
        await conn.close()

async def remove_staff_role(user_id: int) -> bool:
    conn = await get_connection()
    try:
        cursor = await conn.execute("DELETE FROM staff WHERE user_id = ?", (user_id,))
        await conn.execute("DELETE FROM media_partners WHERE user_id = ?", (user_id,))
        await conn.commit()
        return cursor.rowcount > 0
    finally:
        await conn.close()

async def get_staff_role(user_id: int) -> Optional[str]:
    if user_id in config.ADMIN_IDS:
        return "admin"
    conn = await get_connection()
    try:
        async with conn.execute("SELECT role FROM staff WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row["role"]
        # Проверка старой таблицы media_partners
        async with conn.execute("SELECT 1 FROM media_partners WHERE user_id = ?", (user_id,)) as cursor:
            if await cursor.fetchone():
                return "media"
        return None
    finally:
        await conn.close()

async def get_all_staff() -> list[dict[str, Any]]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT * FROM staff ORDER BY role ASC, added_at DESC") as cursor:
            return [dict(row) for row in await cursor.fetchall()]
    finally:
        await conn.close()

async def is_admin_user(user_id: int) -> bool:
    if user_id in config.ADMIN_IDS:
        return True
    role = await get_staff_role(user_id)
    return role == "admin"

async def is_moderator_or_higher(user_id: int) -> bool:
    if user_id in config.ADMIN_IDS:
        return True
    role = await get_staff_role(user_id)
    return role in ("admin", "moderator")

async def is_staff_user(user_id: int) -> bool:
    if user_id in config.ADMIN_IDS:
        return True
    role = await get_staff_role(user_id)
    return role in ("admin", "moderator", "helper")

async def is_media_partner(user_id: int) -> bool:
    if user_id in config.ADMIN_IDS:
        return True
    role = await get_staff_role(user_id)
    if role in ("media", "admin"):
        return True
    conn = await get_connection()
    try:
        async with conn.execute("SELECT 1 FROM media_partners WHERE user_id = ?", (user_id,)) as cursor:
            return bool(await cursor.fetchone())
    finally:
        await conn.close()

async def add_media_partner(user_id: int, channel_link: str = "") -> None:
    await set_staff_role(user_id, "", "media", "system/add_media")
    conn = await get_connection()
    try:
        await conn.execute("INSERT OR REPLACE INTO media_partners (user_id, channel_link) VALUES (?, ?)", (user_id, channel_link))
        await conn.commit()
    finally:
        await conn.close()

async def remove_media_partner(user_id: int) -> None:
    await remove_staff_role(user_id)

# --- Тикеты и заказы ---
async def create_ticket(
    user_id: int,
    username: str,
    item_name: str,
    pay_method: str,
    item_type: str = "privilege",
    price: int = 0,
    mc_nickname: str = "",
    receipt_file_id: str = ""
) -> int:
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            """INSERT INTO tickets 
            (user_id, username, item_type, item_name, price, mc_nickname, pay_method, receipt_file_id, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
            (user_id, username, item_type, item_name, price, mc_nickname, pay_method, receipt_file_id)
        )
        ticket_id = cursor.lastrowid
        await conn.commit()
        return ticket_id
    finally:
        await conn.close()

async def get_active_ticket_by_user(user_id: int) -> Optional[dict]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT * FROM tickets WHERE user_id = ? AND status = 'pending' ORDER BY id DESC LIMIT 1", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    finally:
        await conn.close()

async def close_ticket(ticket_id: int) -> None:
    conn = await get_connection()
    try:
        await conn.execute("UPDATE tickets SET status = 'closed' WHERE id = ?", (ticket_id,))
        await conn.commit()
    finally:
        await conn.close()

async def get_order(order_id: int) -> Optional[dict[str, Any]]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT * FROM tickets WHERE id = ?", (order_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    finally:
        await conn.close()

async def update_order_status(
    order_id: int,
    status: str,
    helper_id: int = 0,
    helper_username: str = ""
) -> bool:
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            """UPDATE tickets 
            SET status = ?, helper_id = ?, helper_username = ? 
            WHERE id = ?""",
            (status, helper_id, helper_username, order_id)
        )
        await conn.commit()
        return cursor.rowcount > 0
    finally:
        await conn.close()

async def get_user_orders(user_id: int) -> list[dict[str, Any]]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT * FROM tickets WHERE user_id = ? ORDER BY id DESC", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    finally:
        await conn.close()

async def get_all_orders() -> list[dict[str, Any]]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT * FROM tickets ORDER BY id DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    finally:
        await conn.close()

# --- Заявки на Хелпера ---
async def save_application(user_id: int, username: str, app_type: str, data: dict) -> int:
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            "INSERT INTO applications (user_id, username, app_type, answers_json, status) VALUES (?, ?, ?, ?, 'pending')",
            (user_id, username, app_type, json.dumps(data, ensure_ascii=False))
        )
        app_id = cursor.lastrowid
        await conn.commit()
        return app_id
    finally:
        await conn.close()

async def get_application(app_id: int) -> Optional[dict[str, Any]]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            try:
                res["answers"] = json.loads(res["answers_json"])
            except Exception:
                res["answers"] = {}
            return res
    finally:
        await conn.close()

async def update_application_status(app_id: int, status: str, reviewer: str = "") -> bool:
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            "UPDATE applications SET status = ?, reviewer = ? WHERE id = ?",
            (status, reviewer, app_id)
        )
        await conn.commit()
        return cursor.rowcount > 0
    finally:
        await conn.close()

# --- Жалобы ---
async def save_complaint(
    user_id: int,
    username: str,
    complaint_type: str,
    my_nick: str,
    target_nick: str,
    incident_date: str,
    reason: str,
    evidence: str,
    additional: str = ""
) -> int:
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            """INSERT INTO complaints 
            (user_id, username, complaint_type, my_nick, target_nick, incident_date, reason, evidence, additional, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
            (user_id, username, complaint_type, my_nick, target_nick, incident_date, reason, evidence, additional)
        )
        comp_id = cursor.lastrowid
        await conn.commit()
        return comp_id
    finally:
        await conn.close()

async def get_complaint(comp_id: int) -> Optional[dict[str, Any]]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT * FROM complaints WHERE id = ?", (comp_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    finally:
        await conn.close()

async def update_complaint_status(comp_id: int, status: str, reviewer: str = "") -> bool:
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            "UPDATE complaints SET status = ?, reviewer = ? WHERE id = ?",
            (status, reviewer, comp_id)
        )
        await conn.commit()
        return cursor.rowcount > 0
    finally:
        await conn.close()

# --- Медиа выплаты ---
async def save_media_request(
    user_id: int,
    username: str,
    request_type: str,
    content: str
) -> int:
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            "INSERT INTO media_requests (user_id, username, request_type, content, status) VALUES (?, ?, ?, ?, 'pending')",
            (user_id, username, request_type, content)
        )
        req_id = cursor.lastrowid
        await conn.commit()
        return req_id
    finally:
        await conn.close()

async def get_media_request(req_id: int) -> Optional[dict[str, Any]]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT * FROM media_requests WHERE id = ?", (req_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    finally:
        await conn.close()

async def update_media_request_status(req_id: int, status: str, reviewer: str = "") -> bool:
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            "UPDATE media_requests SET status = ?, reviewer = ? WHERE id = ?",
            (status, reviewer, req_id)
        )
        await conn.commit()
        return cursor.rowcount > 0
    finally:
        await conn.close()

# --- Настройки и статистика ---
async def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row["value"] if row else default
    finally:
        await conn.close()

async def get_all_settings() -> dict[str, str]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT key, value FROM settings") as cursor:
            rows = await cursor.fetchall()
            return {row["key"]: row["value"] for row in rows}
    finally:
        await conn.close()

async def update_setting(key: str, value: str) -> None:
    conn = await get_connection()
    try:
        await conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        await conn.commit()
    finally:
        await conn.close()

async def set_setting(key: str, value: str) -> None:
    await update_setting(key, value)

async def get_statistics() -> dict[str, Any]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT COUNT(*) as count FROM users") as cursor:
            users_count = (await cursor.fetchone())["count"]
            
        async with conn.execute("SELECT COUNT(*) as count FROM tickets") as cursor:
            tickets_total = (await cursor.fetchone())["count"]
            
        async with conn.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'pending'") as cursor:
            tickets_pending = (await cursor.fetchone())["count"]
            
        async with conn.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'approved'") as cursor:
            tickets_approved = (await cursor.fetchone())["count"]
            
        async with conn.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'rejected'") as cursor:
            tickets_rejected = (await cursor.fetchone())["count"]
            
        async with conn.execute("SELECT SUM(price) as total FROM tickets WHERE status = 'approved'") as cursor:
            row = await cursor.fetchone()
            total_revenue = row["total"] if row and row["total"] else 0

        async with conn.execute("SELECT COUNT(*) as count FROM applications") as cursor:
            apps_total = (await cursor.fetchone())["count"]
            
        async with conn.execute("SELECT COUNT(*) as count FROM applications WHERE status = 'pending'") as cursor:
            apps_pending = (await cursor.fetchone())["count"]

        async with conn.execute("SELECT COUNT(*) as count FROM complaints") as cursor:
            complaints_total = (await cursor.fetchone())["count"]
            
        async with conn.execute("SELECT COUNT(*) as count FROM complaints WHERE status = 'pending'") as cursor:
            complaints_pending = (await cursor.fetchone())["count"]

        async with conn.execute("SELECT COUNT(*) as count FROM staff") as cursor:
            staff_count = (await cursor.fetchone())["count"]

        # Статистика хелперов
        async with conn.execute("""
            SELECT helper_username, COUNT(*) as processed_count 
            FROM tickets 
            WHERE helper_username != '' AND status IN ('approved', 'rejected')
            GROUP BY helper_username 
            ORDER BY processed_count DESC 
            LIMIT 10
        """) as cursor:
            helpers = [dict(row) for row in await cursor.fetchall()]

        return {
            "users": users_count,
            "users_count": users_count,
            "tickets": tickets_total,
            "open_tickets": tickets_pending,
            "orders_total": tickets_total,
            "orders_pending": tickets_pending,
            "orders_approved": tickets_approved,
            "orders_rejected": tickets_rejected,
            "total_revenue": total_revenue,
            "apps_total": apps_total,
            "apps_pending": apps_pending,
            "complaints_total": complaints_total,
            "complaints_pending": complaints_pending,
            "staff_count": staff_count,
            "helpers": helpers
        }
    finally:
        await conn.close()

# --- Привилегии ---
async def get_privileges() -> list[dict[str, Any]]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT * FROM privileges ORDER BY price ASC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    finally:
        await conn.close()

async def get_privilege_by_code(code: str) -> Optional[dict[str, Any]]:
    conn = await get_connection()
    try:
        async with conn.execute("SELECT * FROM privileges WHERE code = ?", (code,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
    finally:
        await conn.close()
