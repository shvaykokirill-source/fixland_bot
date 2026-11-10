import asyncio
import logging
import os
import sys
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database import init_db
from handlers import admin, shop, common, applications, complaints, media


async def handle_ping(request):
    """Ответ для проверки работоспособности от Render."""
    return web.Response(text="FixLand Bot is live!")


async def start_dummy_server():
    """Запуск фонового веб-сервера для удовлетворения требований Render Web Service."""
    port = int(os.environ.get("PORT", 10000))
    app = web.Application()
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Фоновый HTTP-сервер успешно запущен на порту {port}")


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        stream=sys.stdout
    )

    if not config.BOT_TOKEN:
        print("Ошибка: BOT_TOKEN не указан в .env!")
        sys.exit(1)

    # 1. Запуск фонового веб-сервера (для Render/серверов с портом)
    try:
        await start_dummy_server()
    except Exception as e:
        logging.warning(f"Не удалось поднять фоновый HTTP-сервер (некритично для локального запуска): {e}")

    # 2. Инициализация SQLite базы данных
    await init_db()

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Подключение роутеров
    dp.include_router(admin.router)
    dp.include_router(shop.router)
    dp.include_router(applications.router)
    dp.include_router(complaints.router)
    dp.include_router(media.router)
    dp.include_router(common.router)

    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Бот FixLand успешно запущен в режиме polling!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
