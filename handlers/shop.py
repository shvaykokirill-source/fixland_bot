from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from config import config
from database import (
    get_privileges,
    get_privilege_by_code,
    create_ticket,
    get_user_orders,
    get_setting,
    get_order,
    update_order_status
)
from keyboards import (
    shop_categories_kb,
    payment_methods_kb,
    receipt_action_kb,
    order_admin_kb,
    cancel_inline_kb
)
from states import ShopState

router = Router()

PAY_METHOD_NAMES = {
    "card_rf": "🇷🇺 Карта РФ / СБП",
    "card_eu": "🇪🇺 Карта Европы",
    "paypal": "🅿️ PayPal",
    "funpay": "💸 FunPay",
    "crypto": "⚡ CryptoBot / Криптовалюта",
    "other": "💬 Другое (Менеджер)"
}

SETTINGS_KEYS = {
    "card_rf": "requisites_card_rf",
    "card_eu": "requisites_card_eu",
    "paypal": "requisites_paypal",
    "funpay": "requisites_funpay",
    "crypto": "requisites_crypto",
    "other": "requisites_other"
}

# Открытие магазина
@router.message(F.text == "💎 Донат-магазин")
async def show_shop(message: types.Message, state: FSMContext):
    await state.clear()
    privs = await get_privileges()
    await message.answer(
        "🛍️ <b>Добро пожаловать в официальный Донат-Магазин FixLand!</b>\n\n"
        "Выберите желаемую привилегию, игровую валюту или услугу снятия наказания (разбан/размут):",
        reply_markup=shop_categories_kb(privs),
        parse_mode="HTML"
    )

# Выбор привилегии
@router.callback_query(F.data.startswith("shop_priv:"))
async def select_privilege(callback: types.CallbackQuery, state: FSMContext):
    code = callback.data.split(":")[1]
    priv = await get_privilege_by_code(code)
    if not priv:
        await callback.answer("Привилегия не найдена!", show_alert=True)
        return

    await state.update_data(
        item_type="privilege",
        item_code=code,
        item_name=priv["name"],
        price=priv["price"]
    )

    desc = (
        f"👑 <b>Привилегия {priv['name']}</b> {priv['badge']}\n\n"
        f"💰 <b>Стоимость:</b> <code>{priv['price']} ₽</code>\n\n"
        f"📦 <b>Входящие наборы:</b>\n{priv['kits']}\n\n"
        f"⚡ <b>Доступные команды:</b>\n<code>{priv['commands']}</code>\n\n"
        "🎮 <b>Введите ваш игровой никнейм на сервере:</b>"
    )
    await callback.message.answer(desc, reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(ShopState.waiting_for_priv_nick)
    await callback.answer()

@router.message(ShopState.waiting_for_priv_nick)
async def process_priv_nick(message: types.Message, state: FSMContext):
    nick = message.text.strip()
    if len(nick) < 3 or len(nick) > 16 or " " in nick:
        await message.answer("⚠️ Введите корректный игровой никнейм (от 3 до 16 символов без пробелов):")
        return

    await state.update_data(mc_nickname=nick)
    data = await state.get_data()

    await message.answer(
        f"✅ Привилегия: <b>{data['item_name']}</b>\n"
        f"🎮 Игровой ник: <b>{nick}</b>\n"
        f"💵 К оплате: <b>{data['price']} ₽</b>\n\n"
        "Выберите удобный способ оплаты:",
        reply_markup=payment_methods_kb(data["item_code"]),
        parse_mode="HTML"
    )

# Выбор донат-рублей
@router.callback_query(F.data == "shop_item:rubles")
async def select_rubles(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(item_type="rubles")
    await callback.message.answer(
        "💰 <b>Покупка донат-рублей Ⓟ</b>\n\n"
        "Курс конвертации: <b>1 ₽ = 100 Ⓟ</b>\n\n"
        "Введите желаемую сумму в рублях (от 10 до 50 000 ₽):",
        reply_markup=cancel_inline_kb(),
        parse_mode="HTML"
    )
    await state.set_state(ShopState.waiting_for_rub_amount)
    await callback.answer()

@router.message(ShopState.waiting_for_rub_amount)
async def process_rub_amount(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit() or not (10 <= int(text) <= 50000):
        await message.answer("⚠️ Введите корректное число от 10 до 50 000 ₽:")
        return

    rub = int(text)
    points = rub * 100
    await state.update_data(
        item_code="rubles",
        item_name=f"{points:,} Ⓟ ({rub} ₽)",
        price=rub
    )
    await message.answer("🎮 <b>Введите ваш точный игровой никнейм на сервере:</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(ShopState.waiting_for_rub_nick)

@router.message(ShopState.waiting_for_rub_nick)
async def process_rub_nick(message: types.Message, state: FSMContext):
    nick = message.text.strip()
    await state.update_data(mc_nickname=nick)
    data = await state.get_data()

    await message.answer(
        f"✅ Валюта: <b>{data['item_name']}</b>\n"
        f"🎮 Игровой ник: <b>{nick}</b>\n"
        f"💵 К оплате: <b>{data['price']} ₽</b>\n\n"
        "Выберите удобный способ оплаты:",
        reply_markup=payment_methods_kb("rubles"),
        parse_mode="HTML"
    )

# Разбан
@router.callback_query(F.data == "shop_item:unban")
async def select_unban(callback: types.CallbackQuery, state: FSMContext):
    price_str = await get_setting("unban_price", "150")
    price = int(price_str) if price_str.isdigit() else 150
    await state.update_data(
        item_type="unban",
        item_code="unban",
        item_name="Разбан игрового аккаунта",
        price=price
    )
    await callback.message.answer(
        f"🔓 <b>Снятие блокировки (Разбан)</b>\n\n"
        f"Стоимость услуги: <b>{price} ₽</b>\n\n"
        "🎮 <b>Введите игровой никнейм, который заблокирован на сервере:</b>",
        reply_markup=cancel_inline_kb(),
        parse_mode="HTML"
    )
    await state.set_state(ShopState.waiting_for_unban_nick)
    await callback.answer()

@router.message(ShopState.waiting_for_unban_nick)
async def process_unban_nick(message: types.Message, state: FSMContext):
    nick = message.text.strip()
    await state.update_data(mc_nickname=nick)
    data = await state.get_data()
    await message.answer(
        f"🔓 Товар: <b>{data['item_name']}</b>\n"
        f"🎮 Никнейм: <b>{nick}</b>\n"
        f"💵 К оплате: <b>{data['price']} ₽</b>\n\n"
        "Выберите способ оплаты:",
        reply_markup=payment_methods_kb("unban"),
        parse_mode="HTML"
    )

# Размут
@router.callback_query(F.data == "shop_item:unmute")
async def select_unmute(callback: types.CallbackQuery, state: FSMContext):
    price_str = await get_setting("unmute_price", "75")
    price = int(price_str) if price_str.isdigit() else 75
    await state.update_data(
        item_type="unmute",
        item_code="unmute",
        item_name="Размут игрового аккаунта",
        price=price
    )
    await callback.message.answer(
        f"🔈 <b>Снятие блокировки чата (Размут)</b>\n\n"
        f"Стоимость услуги: <b>{price} ₽</b>\n\n"
        "🎮 <b>Введите игровой никнейм, которому выдан мут:</b>",
        reply_markup=cancel_inline_kb(),
        parse_mode="HTML"
    )
    await state.set_state(ShopState.waiting_for_unmute_nick)
    await callback.answer()

@router.message(ShopState.waiting_for_unmute_nick)
async def process_unmute_nick(message: types.Message, state: FSMContext):
    nick = message.text.strip()
    await state.update_data(mc_nickname=nick)
    data = await state.get_data()
    await message.answer(
        f"🔈 Товар: <b>{data['item_name']}</b>\n"
        f"🎮 Никнейм: <b>{nick}</b>\n"
        f"💵 К оплате: <b>{data['price']} ₽</b>\n\n"
        "Выберите способ оплаты:",
        reply_markup=payment_methods_kb("unmute"),
        parse_mode="HTML"
    )

# Мои заказы
@router.callback_query(F.data == "shop_my_orders")
async def show_my_orders(callback: types.CallbackQuery):
    orders = await get_user_orders(callback.from_user.id)
    if not orders:
        await callback.message.answer("📦 У вас пока нет оформленных заказов.")
        await callback.answer()
        return

    text = "📦 <b>История ваших заказов:</b>\n\n"
    status_map = {
        "pending": "⏳ На проверке",
        "approved": "✅ Выдан / Оплачен",
        "rejected": "❌ Отклонён",
        "closed": "🔒 Закрыт"
    }
    for o in orders[:8]:
        st = status_map.get(o["status"], o["status"])
        nick = f" (Ник: {o['mc_nickname']})" if o.get("mc_nickname") else ""
        text += f"• <b>Заказ #{o['id']}</b> — {o['item_name']}{nick}\n  Статус: <b>{st}</b>\n"

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

# Выбор конкретного способа оплаты и выдача реквизитов
@router.callback_query(F.data.startswith("pay:"))
async def process_payment_selection(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    method_key = parts[2]
    user_data = await state.get_data()

    item_name = user_data.get("item_name", "Товар FixLand")
    price = user_data.get("price", 0)
    nick = user_data.get("mc_nickname", "Не указан")
    item_type = user_data.get("item_type", "privilege")

    method_title = PAY_METHOD_NAMES.get(method_key, "Банковский перевод")
    setting_key = SETTINGS_KEYS.get(method_key, "requisites_card_rf")
    requisites = await get_setting(setting_key, "Реквизиты уточняйте у поддержки: @Hupiiaristo")

    username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name

    ticket_id = await create_ticket(
        user_id=callback.from_user.id,
        username=username,
        item_name=item_name,
        pay_method=method_title,
        item_type=item_type,
        price=price,
        mc_nickname=nick
    )

    await state.update_data(ticket_id=ticket_id, pay_method_title=method_title)
    await state.set_state(ShopState.waiting_for_receipt)

    bill_text = (
        f"🧾 <b>СЧЁТ НА ОПЛАТУ #{ticket_id}</b>\n\n"
        f"📦 <b>Товар:</b> {item_name}\n"
        f"🎮 <b>Никнейм:</b> <code>{nick}</code>\n"
        f"💵 <b>Сумма к оплате:</b> <b>{price} ₽</b>\n"
        f"💳 <b>Способ оплаты:</b> {method_title}\n\n"
        f"📌 <b>Реквизиты для перевода:</b>\n{requisites}\n\n"
        "⚠️ <i>После совершения перевода отправьте сюда скриншот чека об оплате (фото или документом):</i>"
    )

    await callback.message.answer(bill_text, reply_markup=receipt_action_kb(), parse_mode="HTML")
    await callback.answer()

# Загрузка чека пользователем
@router.message(ShopState.waiting_for_receipt, F.photo | F.document)
async def process_receipt_upload(message: types.Message, state: FSMContext):
    data = await state.get_data()
    ticket_id = data.get("ticket_id")
    if not ticket_id:
        await message.answer("Сессия заказа устарела. Пожалуйста, начните оформление заново.")
        await state.clear()
        return

    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

    # Обновляем чек в тикете
    from database import get_connection
    conn = await get_connection()
    try:
        await conn.execute("UPDATE tickets SET receipt_file_id = ? WHERE id = ?", (file_id, ticket_id))
        await conn.commit()
    finally:
        await conn.close()

    card_text = (
        f"🛒 <b>НОВЫЙ ЗАКАЗ #{ticket_id}</b>\n\n"
        f"👤 <b>Покупатель:</b> {username} (ID: <code>{message.from_user.id}</code>)\n"
        f"🎮 <b>Игровой ник:</b> <code>{data.get('mc_nickname', '—')}</code>\n"
        f"📦 <b>Товар:</b> {data.get('item_name')}\n"
        f"💵 <b>Сумма:</b> {data.get('price')} ₽\n"
        f"💳 <b>Способ:</b> {data.get('pay_method_title')}"
    )

    # Отправляем фото чека с кнопками в группу администрации
    try:
        if message.photo:
            await message.bot.send_photo(
                chat_id=config.ADMIN_CHAT_ID,
                photo=file_id,
                caption=card_text,
                reply_markup=order_admin_kb(ticket_id),
                parse_mode="HTML"
            )
        else:
            await message.bot.send_document(
                chat_id=config.ADMIN_CHAT_ID,
                document=file_id,
                caption=card_text,
                reply_markup=order_admin_kb(ticket_id),
                parse_mode="HTML"
            )
    except Exception as e:
        print(f"[ERROR] Could not forward receipt to ADMIN_CHAT_ID: {e}")

    await state.clear()
    await message.answer(
        f"✅ <b>Чек по заказу #{ticket_id} успешно получен!</b>\n\n"
        "Наши хелперы и администраторы проверят поступление средств. "
        "Как только донат/услуга будут начислены, вам придёт подтверждение!",
        parse_mode="HTML"
    )
