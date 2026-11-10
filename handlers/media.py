from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from config import config
from database import is_media_partner, is_admin_user, save_media_request
from keyboards import media_center_kb, media_guest_kb, cancel_inline_kb, media_payout_admin_kb
from states import MediaCenterState

router = Router()

RATES_TEXT = (
    "📜 <b>ТАРИФЫ И КРИТЕРИИ ДЛЯ МЕДИА-ПАРТНЁРОВ FIXLAND:</b>\n\n"
    "🎥 <b>Полноценные ролики на YouTube:</b>\n"
    "• От 1 000 просмотров — <b>от 250 ₽</b> + донат-кейсы\n"
    "• От 5 000 просмотров — <b>от 1 200 ₽</b>\n"
    "• От 10 000 просмотров — <b>индивидуальные условия</b>\n\n"
    "📱 <b>YouTube Shorts / TikTok / Reels:</b>\n"
    "• От 3 000 просмотров — <b>от 100 ₽</b>\n"
    "• От 10 000 просмотров — <b>от 350 ₽</b>\n\n"
    "🟣 <b>Стримы (Twitch / YouTube):</b>\n"
    "• От 1.5 часов стрима при среднем онлайне от 10-15 зрителей — <b>бонусы и донат</b>\n\n"
    "📌 <b>Обязательные требования:</b>\n"
    "➤ В описании/закрепе должен быть указан IP сервера и ссылки на наш проект.\n"
    "➤ Качественная картинка и звук, отсутствие сторонней рекламы без согласования.\n"
    "➤ Накрутка просмотров строго запрещена (проверяется аналитикой)!"
)

# Вход в Медиа-Центр
@router.message(F.text == "🎬 Медиа-центр")
async def open_media_center(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    
    # Проверка доступа: медиа или админ
    if not (await is_media_partner(user_id) or await is_admin_user(user_id)):
        await message.answer(
            "🔒 <b>Доступ ограничен!</b>\n\n"
            "Раздел «Медиа-центр» доступен только официальным медиа-партнёрам FixLand.\n\n"
            "Если вы снимаете контент по Minecraft (YouTube, TikTok, Twitch) — подайте заявку на сотрудничество прямо сейчас!",
            reply_markup=media_guest_kb(),
            parse_mode="HTML"
        )
        return

    await message.answer(
        "🎬 <b>Добро пожаловать в Медиа-Центр FixLand!</b>\n\n"
        "Здесь вы можете оформлять заявки на денежные выплаты за просмотры роликов, "
        "запрашивать ресурсы/промокоды для съемок и следить за условиями партнёрства.",
        reply_markup=media_center_kb(),
        parse_mode="HTML"
    )

# Тарифы
@router.callback_query(F.data == "media_rates")
async def show_rates(callback: types.CallbackQuery):
    await callback.message.answer(RATES_TEXT, parse_mode="HTML")
    await callback.answer()

# Запрос выплаты
@router.callback_query(F.data == "media_payout")
async def request_payout(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "💸 <b>Запрос выплаты за контент</b>\n\n"
        "Отправьте одним сообщением:\n"
        "1. Ссылку на вышедший ролик / Shorts / TikTok\n"
        "2. Количество набранных просмотров (со скриншотом/статистикой)\n"
        "3. Ваши реквизиты для получения выплаты (Карта / СБП / СБер / Крипта)",
        reply_markup=cancel_inline_kb(),
        parse_mode="HTML"
    )
    await state.set_state(MediaCenterState.waiting_for_payout_details)
    await callback.answer()

@router.message(MediaCenterState.waiting_for_payout_details)
async def process_payout_details(message: types.Message, state: FSMContext):
    text = message.text.strip() if message.text else "Без текста (медиа файл)"
    await state.clear()

    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    req_id = await save_media_request(
        user_id=message.from_user.id,
        username=username,
        request_type="Выплата за просмотры",
        content=text
    )

    card_text = (
        f"💸 <b>ЗАПРОС ВЫПЛАТЫ МЕДИА #{req_id}</b>\n\n"
        f"👤 <b>Медиа-партнёр:</b> {username} (ID: <code>{message.from_user.id}</code>)\n"
        f"📝 <b>Детали и реквизиты:</b>\n{text}"
    )

    try:
        await message.bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,
            text=card_text,
            reply_markup=media_payout_admin_kb(req_id),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"[ERROR] Could not send payout request to ADMIN_CHAT_ID: {e}")

    await message.answer(
        "✅ <b>Запрос на выплату успешно передан медиа-менеджеру!</b>\nПосле проверки статистики вам поступят средства.",
        parse_mode="HTML"
    )

# Запрос промокода / бонусов
@router.callback_query(F.data == "media_perks")
async def request_perks(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "🎁 <b>Запрос медиа-набора / промокода</b>\n\n"
        "Напишите ваш игровой никнейм на сервере и что вам необходимо для создания контента (привилегия, ресурсы, кейсы или личный промокод):",
        reply_markup=cancel_inline_kb(),
        parse_mode="HTML"
    )
    await state.set_state(MediaCenterState.waiting_for_perk_request)
    await callback.answer()

@router.message(MediaCenterState.waiting_for_perk_request)
async def process_perk_request(message: types.Message, state: FSMContext):
    text = message.text.strip() if message.text else "—"
    await state.clear()

    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    req_id = await save_media_request(
        user_id=message.from_user.id,
        username=username,
        request_type="Запрос бонусов / набора",
        content=text
    )

    card_text = (
        f"🎁 <b>ЗАПРОС МЕДИА-БОНУСОВ #{req_id}</b>\n\n"
        f"👤 <b>Медиа:</b> {username} (ID: <code>{message.from_user.id}</code>)\n"
        f"📦 <b>Запрос:</b>\n{text}"
    )

    try:
        await message.bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,
            text=card_text,
            reply_markup=media_payout_admin_kb(req_id),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"[ERROR] Could not send perks request to ADMIN_CHAT_ID: {e}")

    await message.answer(
        "✅ <b>Запрос на бонусы передан кураторам!</b> Скоро все необходимые вещи будут выданы вам на сервере.",
        parse_mode="HTML"
    )
