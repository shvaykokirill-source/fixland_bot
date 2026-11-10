from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from config import config
from database import save_complaint
from keyboards import complaint_menu_kb, cancel_inline_kb, complaint_admin_kb
from states import ComplaintState

router = Router()

RULES_HEADER = (
    "🚨 <b>РАЗДЕЛ ПОДАЧИ ЖАЛОБ FIXLAND</b>\n\n"
    "⚠️ <b>ВНИМАТЕЛЬНО ОЗНАКОМЬТЕСЬ С ПРАВИЛАМИ:</b>\n"
    "➤ Обрезанные скриншоты = <b>отказ!</b>\n"
    "➤ Фото сделанные на телефон = <b>отказ!</b>\n"
    "➤ Если жалоба составлена не по форме = <b>отказ!</b>\n"
    "➤ Если в жалобе присутствуют оскорбления = <b>отказ!</b>\n"
    "➤ Рек принимается только ссылкой на Google Диск / YouTube!\n"
    "➤ Если рек идет более 1-ой минуты, обязательно пишите таймкод нарушения!\n\n"
    "Выберите категорию жалобы:"
)

@router.message(F.text == "🚨 Подать жалобу")
async def show_complaints_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(RULES_HEADER, reply_markup=complaint_menu_kb(), parse_mode="HTML")

@router.callback_query(F.data == "complaint:player")
async def start_player_complaint(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.update_data(target_type="player", title="Жалоба на игрока")
    await callback.message.answer(
        "👤 <b>Жалоба на игрока</b>\n\n"
        "➤ <b>1. Укажите ваш никнейм на сервере:</b>",
        reply_markup=cancel_inline_kb(),
        parse_mode="HTML"
    )
    await state.set_state(ComplaintState.waiting_for_my_nick)
    await callback.answer()

@router.callback_query(F.data == "complaint:staff")
async def start_staff_complaint(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.update_data(target_type="staff", title="Жалоба на команду проекта")
    await callback.message.answer(
        "🛡️ <b>Жалоба на команду проекта (Администратора)</b>\n\n"
        "➤ <b>1. Укажите ваш никнейм на сервере:</b>",
        reply_markup=cancel_inline_kb(),
        parse_mode="HTML"
    )
    await state.set_state(ComplaintState.waiting_for_my_nick)
    await callback.answer()

@router.message(ComplaintState.waiting_for_my_nick)
async def process_my_nick(message: types.Message, state: FSMContext):
    await state.update_data(my_nick=message.text.strip())
    data = await state.get_data()
    prompt = "➤ <b>2. Укажите ник нарушителя:</b>" if data.get("target_type") == "player" else "➤ <b>2. Укажите ник администратора:</b>"
    await message.answer(prompt, reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(ComplaintState.waiting_for_target_nick)

@router.message(ComplaintState.waiting_for_target_nick)
async def process_target_nick(message: types.Message, state: FSMContext):
    await state.update_data(target_nick=message.text.strip())
    data = await state.get_data()
    prompt = "➤ <b>3. Укажите дату нарушения (например, 10.11.2026):</b>" if data.get("target_type") == "player" else "➤ <b>3. Укажите дату инцидента:</b>"
    await message.answer(prompt, reply_markup=cancel_inline_kb(), parse_mode="HTML")
    await state.set_state(ComplaintState.waiting_for_date)

@router.message(ComplaintState.waiting_for_date)
async def process_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text.strip())
    await message.answer(
        "➤ <b>4. Опишите причину жалобы и суть нарушения:</b>",
        reply_markup=cancel_inline_kb(),
        parse_mode="HTML"
    )
    await state.set_state(ComplaintState.waiting_for_reason)

@router.message(ComplaintState.waiting_for_reason)
async def process_reason(message: types.Message, state: FSMContext):
    await state.update_data(reason=message.text.strip())
    await message.answer(
        "➤ <b>5. Предоставьте скриншот или ссылку на рек:</b>\n\n"
        "<i>Напоминание: фото с телефона и обрезанные скрины не принимаются. Рек только ссылкой (YouTube/Google Drive), если видео больше 1 мин — укажите таймкод!</i>",
        reply_markup=cancel_inline_kb(),
        parse_mode="HTML"
    )
    await state.set_state(ComplaintState.waiting_for_evidence)

@router.message(ComplaintState.waiting_for_evidence)
async def process_evidence(message: types.Message, state: FSMContext):
    # Если прислали фото напрямую или текст со ссылкой
    evidence_text = ""
    if message.photo:
        evidence_text = f"[Фото ID: {message.photo[-1].file_id}]"
        if message.caption:
            evidence_text += f" {message.caption}"
    else:
        evidence_text = message.text.strip() if message.text else "Без текста"

    await state.update_data(evidence=evidence_text)
    await message.answer(
        "➤ <b>6. Дополнительная информация</b> (или напишите 'Нет'):",
        reply_markup=cancel_inline_kb(),
        parse_mode="HTML"
    )
    await state.set_state(ComplaintState.waiting_for_additional)

@router.message(ComplaintState.waiting_for_additional)
async def process_additional(message: types.Message, state: FSMContext):
    additional_text = message.text.strip() if message.text else "—"
    data = await state.get_data()
    await state.clear()

    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    target_type = data.get("target_type", "player")
    type_name = "👤 ИГРОКА" if target_type == "player" else "🛡️ АДМИНИСТРАТОРА (КП)"

    comp_id = await save_complaint(
        user_id=message.from_user.id,
        username=username,
        complaint_type=target_type,
        my_nick=data.get("my_nick", "—"),
        target_nick=data.get("target_nick", "—"),
        incident_date=data.get("date", "—"),
        reason=data.get("reason", "—"),
        evidence=data.get("evidence", "—"),
        additional=additional_text
    )

    card_text = (
        f"🚨 <b>НОВАЯ ЖАЛОБА #{comp_id} (НА {type_name})</b>\n\n"
        f"👤 <b>Отправитель:</b> {username} (ID: <code>{message.from_user.id}</code>)\n"
        f"➤ <b>1. Ник подателя:</b> {data.get('my_nick')}\n"
        f"➤ <b>2. Ник нарушителя:</b> {data.get('target_nick')}\n"
        f"➤ <b>3. Дата:</b> {data.get('date')}\n"
        f"➤ <b>4. Причина:</b> {data.get('reason')}\n"
        f"➤ <b>5. Доказательства (скрин/рек):</b> {data.get('evidence')}\n"
        f"➤ <b>6. Дополнительно:</b> {additional_text}"
    )

    try:
        await message.bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,
            text=card_text,
            reply_markup=complaint_admin_kb(comp_id),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"[ERROR] Could not send complaint to ADMIN_CHAT_ID: {e}")

    await message.answer(
        f"✅ <b>Ваша жалоба #{comp_id} успешно зарегистрирована!</b>\n\n"
        "Она передана модераторам и администраторам на проверку. В случае принятия мер вы будете проинформированы.",
        parse_mode="HTML"
    )
