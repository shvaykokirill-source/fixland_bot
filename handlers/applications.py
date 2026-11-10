import json
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from config import config
from database import save_application, is_moderator_or_higher
from keyboards import cancel_inline_kb, app_admin_kb, main_menu_kb
from states import HelperApplicationState, MediaApplicationState

router = Router()

QUESTIONS = [
    ("1. 🎮 Ваш никнейм на сервере:", "nick"),
    ("2. 🎂 Ваш возраст:", "age"),
    ("3. 🧠 Оцените свою адекватность (по 10-балльной шкале):", "adequacy"),
    ("4. ✍️ Оцените свою грамотность (по 10-балльной шкале):", "literacy"),
    ("5. 💼 Есть ли у вас опыт работы в данной сфере? (На каких серверах работали? Приведите доказательства):", "experience"),
    ("6. 🔍 Как хорошо вы проверяете игроков на читы? (Оцените по 10-балльной шкале):", "cheat_check"),
    ("7. 🛠️ Какими программами пользуетесь для проверок (минимум 4 программы)? (Anydesk, Telegram и Discord не учитываются):", "programs"),
    ("8. 🎙️ Есть ли у вас микрофон и наушники? (Да/Нет):", "mic_headphones"),
    ("9. ⏰ Сколько часов в день можете уделять проекту? (Минимум 4 часа):", "hours"),
    ("10. 🌟 Почему мы должны выбрать именно вас в команду?:", "why_you"),
    ("11. 📖 Напишите мини-рассказ (от 35 слов) на тему:\n«Как я вижу себя в роли администратора сервера»:", "essay"),
    ("12. 📜 Насколько хорошо вы знаете правила проекта? (Оцените по 10-балльной шкале):", "rules"),
    ("13. 📚 Объясните значение этих терминов (минимум по 10 слов на каждый):\n\n• Бан:\n• Кик:\n• Мут:", "terms"),
    ("14. 🌍 Ваш часовой пояс (например, МСК, МСК+2):", "timezone"),
    ("15. 📱 Привязан ли у вас игровой аккаунт к Telegram? (Да/Нет):", "tg_linked"),
    ("16. 💻 Ваше устройство (PC, Ноутбук):", "device")
]

# Старт анкеты хелпера
@router.callback_query(F.data == "apply:helper")
async def start_helper_application(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "🛡️ <b>Форма заявки на должность Хелпера</b>\n\n"
        "Пожалуйста, отвечайте честно, развернуто и грамотно.\n"
        "Всего вам предстоит ответить на 16 вопросов.\n\n"
        f"<b>{QUESTIONS[0][0]}</b>",
        reply_markup=cancel_inline_kb(),
        parse_mode="HTML"
    )
    await state.set_state(HelperApplicationState.step1_nick)
    await callback.answer()

# 1. Никнейм
@router.message(HelperApplicationState.step1_nick)
async def process_step1(message: types.Message, state: FSMContext):
    await state.update_data(nick=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[1][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step2_age)

# 2. Возраст
@router.message(HelperApplicationState.step2_age)
async def process_step2(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[2][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step3_adequacy)

# 3. Адекватность
@router.message(HelperApplicationState.step3_adequacy)
async def process_step3(message: types.Message, state: FSMContext):
    await state.update_data(adequacy=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[3][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step4_literacy)

# 4. Грамотность
@router.message(HelperApplicationState.step4_literacy)
async def process_step4(message: types.Message, state: FSMContext):
    await state.update_data(literacy=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[4][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step5_experience)

# 5. Опыт
@router.message(HelperApplicationState.step5_experience)
async def process_step5(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[5][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step6_cheat_check)

# 6. Проверка на читы
@router.message(HelperApplicationState.step6_cheat_check)
async def process_step6(message: types.Message, state: FSMContext):
    await state.update_data(cheat_check=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[6][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step7_programs)

# 7. Программы для проверок
@router.message(HelperApplicationState.step7_programs)
async def process_step7(message: types.Message, state: FSMContext):
    await state.update_data(programs=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[7][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step8_mic_headphones)

# 8. Микрофон и наушники
@router.message(HelperApplicationState.step8_mic_headphones)
async def process_step8(message: types.Message, state: FSMContext):
    await state.update_data(mic_headphones=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[8][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step9_hours)

# 9. Часы в день
@router.message(HelperApplicationState.step9_hours)
async def process_step9(message: types.Message, state: FSMContext):
    await state.update_data(hours=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[9][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step10_why_you)

# 10. Почему вы
@router.message(HelperApplicationState.step10_why_you)
async def process_step10(message: types.Message, state: FSMContext):
    await state.update_data(why_you=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[10][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step11_essay)

# 11. Рассказ
@router.message(HelperApplicationState.step11_essay)
async def process_step11(message: types.Message, state: FSMContext):
    await state.update_data(essay=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[11][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step12_rules)

# 12. Знание правил
@router.message(HelperApplicationState.step12_rules)
async def process_step12(message: types.Message, state: FSMContext):
    await state.update_data(rules=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[12][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step13_terms)

# 13. Термины (Бан, Кик, Мут)
@router.message(HelperApplicationState.step13_terms)
async def process_step13(message: types.Message, state: FSMContext):
    await state.update_data(terms=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[13][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step14_timezone)

# 14. Часовой пояс
@router.message(HelperApplicationState.step14_timezone)
async def process_step14(message: types.Message, state: FSMContext):
    await state.update_data(timezone=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[14][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step15_tg_linked)

# 15. ТГ привязан
@router.message(HelperApplicationState.step15_tg_linked)
async def process_step15(message: types.Message, state: FSMContext):
    await state.update_data(tg_linked=message.text.strip())
    await message.answer(f"<b>{QUESTIONS[15][0]}</b>", reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(HelperApplicationState.step16_device)

# 16. Устройство и финал
@router.message(HelperApplicationState.step16_device)
async def process_step16(message: types.Message, state: FSMContext):
    await state.update_data(device=message.text.strip())
    data = await state.get_data()
    await state.clear()

    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    
    # Сохраняем в БД
    app_id = await save_application(
        user_id=message.from_user.id,
        username=username,
        app_type="Хелпер",
        data=data
    )

    # Формируем карточку для группы администрации
    card_text = (
        f"🛡️ <b>НОВАЯ ЗАЯВКА НА ХЕЛПЕРА #{app_id}</b>\n\n"
        f"👤 <b>Кандидат:</b> {username} (ID: <code>{message.from_user.id}</code>)\n"
        f"🎮 <b>Ник на сервере:</b> {data.get('nick')}\n"
        f"🎂 <b>Возраст:</b> {data.get('age')}\n"
        f"🧠 <b>Адекватность:</b> {data.get('adequacy')}/10 | ✍️ <b>Грамотность:</b> {data.get('literacy')}/10\n"
        f"💼 <b>Опыт:</b> {data.get('experience')}\n"
        f"🔍 <b>Проверка на читы:</b> {data.get('cheat_check')}/10\n"
        f"🛠️ <b>Программы:</b> {data.get('programs')}\n"
        f"🎙️ <b>Микрофон и уши:</b> {data.get('mic_headphones')}\n"
        f"⏰ <b>Онлайн в день:</b> {data.get('hours')}\n"
        f"🌟 <b>Почему именно он:</b> {data.get('why_you')}\n"
        f"📖 <b>Сочинение:</b>\n<i>{data.get('essay')}</i>\n\n"
        f"📜 <b>Правила:</b> {data.get('rules')}/10\n"
        f"📚 <b>Термины:</b>\n{data.get('terms')}\n"
        f"🌍 <b>Часовой пояс:</b> {data.get('timezone')}\n"
        f"📱 <b>ТГ привязан:</b> {data.get('tg_linked')}\n"
        f"💻 <b>Устройство:</b> {data.get('device')}"
    )

    # Отправляем в чат администрации
    try:
        await message.bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,
            text=card_text,
            reply_markup=app_admin_kb(app_id),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"[ERROR] Could not send application to ADMIN_CHAT_ID: {e}")

    await message.answer(
        "🎉 <b>Ваша анкета на должность Хелпера успешно принята и передана руководству проекта!</b>\n\n"
        "Мы внимательно изучим ваши ответы. В случае успешного прохождения вы получите уведомление в этом боте.\n"
        "Спасибо за желание развивать наш проект!",
        parse_mode="HTML"
    )

# --- Медиа заявка ---

@router.callback_query(F.data == "apply:media")
async def start_media_application(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "📽️ <b>Заявка на сотрудничество (Медиа-партнёр)</b>\n\n"
        "Мы рады авторам контента по Minecraft!\n"
        "Пришлите ссылку на ваш канал (YouTube, TikTok, Twitch, VK Видео):",
        reply_markup=cancel_inline_kb(),
        parse_mode="HTML"
    )
    await state.set_state(MediaApplicationState.waiting_for_channel)
    await callback.answer()

@router.message(MediaApplicationState.waiting_for_channel)
async def process_media_channel(message: types.Message, state: FSMContext):
    await state.update_data(channel=message.text.strip())
    await message.answer(
        "📊 Укажите среднее количество просмотров на роликах/стримах и ваш игровой никнейм:",
        reply_markup=cancel_inline_kb()
    )
    await state.set_state(MediaApplicationState.waiting_for_stats)

@router.message(MediaApplicationState.waiting_for_stats)
async def process_media_stats(message: types.Message, state: FSMContext):
    data = await state.get_data()
    channel = data.get("channel", "—")
    stats = message.text.strip()
    await state.clear()

    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    
    app_id = await save_application(
        user_id=message.from_user.id,
        username=username,
        app_type="Медиа",
        data={"channel": channel, "stats": stats}
    )

    card_text = (
        f"📽️ <b>НОВАЯ МЕДИА-ЗАЯВКА #{app_id}</b>\n\n"
        f"👤 <b>Кандидат:</b> {username} (ID: <code>{message.from_user.id}</code>)\n"
        f"🔗 <b>Канал:</b> {channel}\n"
        f"📊 <b>Статистика и ник:</b> {stats}"
    )

    try:
        await message.bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,
            text=card_text,
            reply_markup=app_admin_kb(app_id),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"[ERROR] Could not send media application: {e}")

    await message.answer(
        "✅ <b>Ваша медиа-заявка успешно отправлена!</b>\nМедиа-менеджер рассмотрит ее в ближайшее время.",
        parse_mode="HTML"
    )
