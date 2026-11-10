import asyncio
from aiogram import Router, F, Bot, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import config
from database import (
    get_order,
    update_order_status,
    get_statistics,
    get_all_settings,
    set_setting,
    get_setting,
    set_staff_role,
    remove_staff_role,
    get_all_staff,
    is_admin_user,
    is_moderator_or_higher,
    get_application,
    update_application_status,
    get_complaint,
    update_complaint_status,
    get_media_request,
    update_media_request_status,
    get_all_users,
    main_menu_kb
)
from states import AdminState
from keyboards import admin_panel_kb, admin_requisites_kb, admin_back_kb

router = Router()

ROLE_MAPPING = {
    "медиа": "media",
    "media": "media",
    "модер": "moderator",
    "модератор": "moderator",
    "moder": "moderator",
    "moderator": "moderator",
    "хелпер": "helper",
    "helper": "helper",
    "админ": "admin",
    "admin": "admin",
    "снять": "remove",
    "remove": "remove",
    "user": "remove"
}

ROLE_TITLES = {
    "admin": "👑 Администратор",
    "moderator": "⚖️ Модератор",
    "helper": "⚔️ Хелпер",
    "media": "🎬 Медиа-партнёр",
    "remove": "👤 Обычный игрок"
}


# ===================== КОМАНДЫ РОЛЕЙ В ГРУППЕ АДМИНИСТРАЦИИ =====================

async def can_manage_roles(message: Message) -> bool:
    """Проверка прав: команда выполняется админом проекта."""
    user_id = message.from_user.id if message.from_user else 0
    return await is_admin_user(user_id)

@router.message(Command("role", "роль"))
async def cmd_manage_role(message: Message):
    if not await can_manage_roles(message):
        return

    parts = message.text.split()
    target_id = None
    target_role_raw = None

    if len(parts) >= 3 and parts[2].isdigit():
        target_role_raw = parts[1].lower()
        target_id = int(parts[2])
    elif len(parts) >= 2 and message.reply_to_message and message.reply_to_message.from_user:
        target_role_raw = parts[1].lower()
        target_id = message.reply_to_message.from_user.id
    else:
        await message.reply(
            "ℹ️ <b>Формат выдачи роли:</b>\n"
            "<code>/роль &lt;роль&gt; &lt;ID&gt;</code>\n"
            "Или ответом на сообщение: <code>/роль &lt;роль&gt;</code>\n\n"
            "Доступные роли: <code>медиа</code>, <code>модератор</code>, <code>хелпер</code>, <code>админ</code>, <code>снять</code>",
            parse_mode="HTML"
        )
        return

    role = ROLE_MAPPING.get(target_role_raw)
    if not role:
        await message.reply("⚠️ Неизвестная роль! Допустимо: медиа, модератор, хелпер, админ, снять.")
        return

    admin_tag = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

    if role == "remove":
        await remove_staff_role(target_id)
        await message.reply(f"✅ У пользователя с ID <code>{target_id}</code> успешно сняты все роли персонала.", parse_mode="HTML")
        try:
            await message.bot.send_message(
                chat_id=target_id,
                text="ℹ️ <b>Ваши специальные роли на проекте FixLand были сняты.</b>",
                reply_markup=main_menu_kb(False),
                parse_mode="HTML"
            )
        except Exception:
            pass
        return

    await set_staff_role(user_id=target_id, username="", role=role, added_by=admin_tag)
    role_title = ROLE_TITLES.get(role, role)

    await message.reply(
        f"👑 <b>Роль успешно обновлена!</b>\n\n"
        f"👤 <b>Пользователь ID:</b> <code>{target_id}</code>\n"
        f"📌 <b>Назначена роль:</b> {role_title}\n"
        f"✍️ <b>Назначил:</b> {admin_tag}",
        parse_mode="HTML"
    )

    # Уведомляем пользователя в ЛС и обновляем его меню
    try:
        is_adm = role in ("admin", "moderator")
        await message.bot.send_message(
            chat_id=target_id,
            text=(
                f"🎉 <b>Поздравляем!</b>\n\n"
                f"Вам была выдана роль <b>{role_title}</b> на проекте FixLand!\n"
                "Ваше меню в боте было обновлено."
            ),
            reply_markup=main_menu_kb(is_adm),
            parse_mode="HTML"
        )
    except Exception:
        pass


# Прямые быстрые команды: /медиа, /модератор, /хелпер, /админ, /снять
@router.message(Command("media", "медиа", "модератор", "модер", "moder", "хелпер", "helper", "админ", "admin", "снять"))
async def cmd_quick_role(message: Message):
    if not await can_manage_roles(message):
        return

    cmd_raw = message.text.split()[0].lstrip("/").lower().split("@")[0]
    role = ROLE_MAPPING.get(cmd_raw)
    if not role:
        return

    parts = message.text.split()
    target_id = None

    if len(parts) >= 2 and parts[1].isdigit():
        target_id = int(parts[1])
    elif message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
    else:
        await message.reply(
            f"ℹ️ Использование: <code>/{cmd_raw} &lt;ID игрока&gt;</code> или ответом на сообщение игрока.",
            parse_mode="HTML"
        )
        return

    admin_tag = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

    if role == "remove":
        await remove_staff_role(target_id)
        await message.reply(f"✅ Пользователь <code>{target_id}</code> лишен полномочий.", parse_mode="HTML")
        try:
            await message.bot.send_message(chat_id=target_id, text="ℹ️ Ваши полномочия были сняты.", reply_markup=main_menu_kb(False), parse_mode="HTML")
        except Exception:
            pass
        return

    await set_staff_role(user_id=target_id, username="", role=role, added_by=admin_tag)
    role_title = ROLE_TITLES.get(role, role)

    await message.reply(
        f"👑 <b>Назначение выполнено!</b>\n"
        f"Пользователь <code>{target_id}</code> теперь <b>{role_title}</b>.",
        parse_mode="HTML"
    )

    try:
        is_adm = role in ("admin", "moderator")
        await message.bot.send_message(
            chat_id=target_id,
            text=f"🎉 Вам успешно выдана роль <b>{role_title}</b> на сервере FixLand!",
            reply_markup=main_menu_kb(is_adm),
            parse_mode="HTML"
        )
    except Exception:
        pass


# Список персонала: /staff или /состав
@router.message(Command("staff", "состав"))
async def cmd_staff_list(message: Message):
    staff_members = await get_all_staff()
    text = "👥 <b>СОСТАВ ПРОЕКТА FIXLAND:</b>\n\n"
    if not staff_members:
        text += "<i>В базе данных пока нет назначенных сотрудников.</i>\n"
    else:
        for idx, s in enumerate(staff_members, 1):
            r_title = ROLE_TITLES.get(s["role"], s["role"])
            u_tag = s.get("username") or f"ID: {s['user_id']}"
            text += f"{idx}. {r_title} — <code>{u_tag}</code> (Добавил: {s.get('added_by', '—')})\n"

    text += "\n🔑 <b>Главные администраторы из .env:</b>\n"
    for a_id in config.ADMIN_IDS:
        text += f"• <code>{a_id}</code>\n"

    await message.reply(text, parse_mode="HTML")


# ===================== ИНТЕРАКТИВНЫЕ ДЕЙСТВИЯ В ЧАТЕ АДМИНИСТРАЦИИ =====================

# 1. Заказы (Донат / Валюта / Разбан / Размут)
@router.callback_query(F.data.startswith("order_act:"))
async def process_order_moderation(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split(":")
    action = parts[1]  # approve / reject
    order_id = int(parts[2])

    order = await get_order(order_id)
    if not order:
        await callback.answer("Заказ не найден!", show_alert=True)
        return

    if order["status"] != "pending":
        await callback.answer(f"Заказ уже обработан (статус: {order['status']})!", show_alert=True)
        return

    admin = callback.from_user
    admin_tag = f"@{admin.username}" if admin.username else admin.full_name

    new_status = "approved" if action == "approve" else "rejected"
    await update_order_status(
        order_id=order_id,
        status=new_status,
        helper_id=admin.id,
        helper_username=admin_tag
    )

    caption = callback.message.caption or callback.message.text or ""
    if action == "approve":
        status_line = f"\n\n✅ <b>ОДОБРЕНО И ВЫДАНО</b> (Обработал: {admin_tag})"
    else:
        status_line = f"\n\n❌ <b>ОТКЛОНЕНО</b> (Обработал: {admin_tag})"

    try:
        if callback.message.photo or callback.message.document:
            await callback.message.edit_caption(caption=caption + status_line, reply_markup=None, parse_mode="HTML")
        else:
            await callback.message.edit_text(text=caption + status_line, reply_markup=None, parse_mode="HTML")
    except Exception as e:
        print(f"[WARNING] Edit order message error: {e}")

    await callback.answer(f"Заказ #{order_id} {'одобрен' if action == 'approve' else 'отклонен'}!")

    # Уведомление покупателю
    user_id = order["user_id"]
    if action == "approve":
        buyer_msg = (
            f"🎉 <b>Ваш заказ #{order_id} ({order['item_name']}) успешно подтвержден!</b>\n\n"
            f"Услуга зачислена на ник <b>{order.get('mc_nickname', '—')}</b>.\n"
            "Приятной игры на FixLand! 🎮"
        )
    else:
        buyer_msg = (
            f"❌ <b>Ваш заказ #{order_id} ({order['item_name']}) был отклонён.</b>\n\n"
            "Возможные причины: чек не читается или средства не поступили.\n"
            "Для выяснения обстоятельств обратитесь в поддержку: @Hupiiaristo"
        )

    try:
        await bot.send_message(chat_id=user_id, text=buyer_msg, parse_mode="HTML")
    except Exception:
        pass


# 2. Заявки на Хелпера / Медиа
@router.callback_query(F.data.startswith("app_act:"))
async def process_app_moderation(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split(":")
    action = parts[1]
    app_id = int(parts[2])

    app = await get_application(app_id)
    if not app:
        await callback.answer("Заявка не найдена!", show_alert=True)
        return

    if app["status"] != "pending":
        await callback.answer(f"Заявка уже рассмотрена ({app['status']})!", show_alert=True)
        return

    admin = callback.from_user
    admin_tag = f"@{admin.username}" if admin.username else admin.full_name

    new_status = "approved" if action == "approve" else "rejected"
    await update_application_status(app_id, new_status, admin_tag)

    msg_text = callback.message.text or ""
    status_line = f"\n\n✅ <b>ЗАЯВКА ОДОБРЕНА</b> (Куратор: {admin_tag})" if action == "approve" else f"\n\n❌ <b>ЗАЯВКА ОТКЛОНЕНА</b> (Куратор: {admin_tag})"

    try:
        await callback.message.edit_text(text=msg_text + status_line, reply_markup=None, parse_mode="HTML")
    except Exception:
        pass

    await callback.answer(f"Заявка #{app_id} рассмотрена!")

    # Уведомление кандидату
    user_id = app["user_id"]
    app_type = app.get("app_type", "Хелпер")
    if action == "approve":
        cand_msg = (
            f"🎉 <b>ПОЗДРАВЛЯЕМ! Ваша анкета на должность {app_type} одобрена!</b>\n\n"
            f"Куратор (<b>{admin_tag}</b>) свяжется с вами в Telegram для прохождения собеседования.\n"
            "Пожалуйста, откройте личные сообщения для входящих контактов!"
        )
    else:
        cand_msg = (
            f"❌ <b>Ваша анкета на должность {app_type} была отклонена.</b>\n\n"
            "Не расстраивайтесь! Вы можете освежить правила сервера и подать заявку повторно через некоторое время."
        )

    try:
        await bot.send_message(chat_id=user_id, text=cand_msg, parse_mode="HTML")
    except Exception:
        pass


# 3. Жалобы (на игроков / команду проекта)
@router.callback_query(F.data.startswith("comp_act:"))
async def process_complaint_moderation(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split(":")
    action = parts[1]
    comp_id = int(parts[2])

    comp = await get_complaint(comp_id)
    if not comp:
        await callback.answer("Жалоба не найдена!", show_alert=True)
        return

    if comp["status"] != "pending":
        await callback.answer(f"Жалоба уже обработана ({comp['status']})!", show_alert=True)
        return

    admin = callback.from_user
    admin_tag = f"@{admin.username}" if admin.username else admin.full_name

    new_status = "approved" if action == "approve" else "rejected"
    await update_complaint_status(comp_id, new_status, admin_tag)

    msg_text = callback.message.text or ""
    status_line = f"\n\n✅ <b>ЖАЛОБА УДОВЛЕТВОРЕНА / МЕРЫ ПРИНЯТЫ</b> ({admin_tag})" if action == "approve" else f"\n\n❌ <b>ОТКЛОНЕНО (НЕДОСТАТОЧНО ДОКАЗАТЕЛЬСТВ / НЕ ПО ФОРМЕ)</b> ({admin_tag})"

    try:
        await callback.message.edit_text(text=msg_text + status_line, reply_markup=None, parse_mode="HTML")
    except Exception:
        pass

    await callback.answer(f"Жалоба #{comp_id} обработана!")

    # Уведомление подателю жалобы
    user_id = comp["user_id"]
    if action == "approve":
        user_msg = (
            f"✅ <b>Ваша жалоба #{comp_id} успешно рассмотрена!</b>\n\n"
            f"Нарушитель <b>{comp['target_nick']}</b> получил соответствующее наказание.\n"
            "Благодарим за содействие в поддержании честной игры на FixLand!"
        )
    else:
        user_msg = (
            f"❌ <b>Ваша жалоба #{comp_id} была отклонена модерацией.</b>\n\n"
            "Возможные причины: доказательства не соответствуют правилам (скрин обрезан / фото с экрана / видео без таймкода) или нарушение не подтвердилось."
        )

    try:
        await bot.send_message(chat_id=user_id, text=user_msg, parse_mode="HTML")
    except Exception:
        pass


# 4. Медиа выплаты
@router.callback_query(F.data.startswith("media_act:"))
async def process_media_payout_moderation(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split(":")
    action = parts[1]
    req_id = int(parts[2])

    req = await get_media_request(req_id)
    if not req:
        await callback.answer("Запрос не найден!", show_alert=True)
        return

    if req["status"] != "pending":
        await callback.answer(f"Запрос уже обработан ({req['status']})!", show_alert=True)
        return

    admin = callback.from_user
    admin_tag = f"@{admin.username}" if admin.username else admin.full_name

    new_status = "approved" if action == "approve" else "rejected"
    await update_media_request_status(req_id, new_status, admin_tag)

    msg_text = callback.message.text or ""
    status_line = f"\n\n✅ <b>ВЫПЛАЧЕНО / ВЫДАНО</b> ({admin_tag})" if action == "approve" else f"\n\n❌ <b>ОТКЛОНЕНО</b> ({admin_tag})"

    try:
        await callback.message.edit_text(text=msg_text + status_line, reply_markup=None, parse_mode="HTML")
    except Exception:
        pass

    await callback.answer(f"Медиа-запрос #{req_id} обновлен!")

    user_id = req["user_id"]
    if action == "approve":
        msg = f"🎉 <b>Ваш медиа-запрос #{req_id} подтвержден!</b>\nВыплата отправлена по указанным реквизитам / бонусы начислены."
    else:
        msg = f"❌ <b>Ваш медиа-запрос #{req_id} был отклонен.</b> За подробностями обратитесь к куратору: @Hupiiaristo"

    try:
        await bot.send_message(chat_id=user_id, text=msg, parse_mode="HTML")
    except Exception:
        pass


# ===================== ПАНЕЛЬ УПРАВЛЕНИЯ БОТОМ =====================

@router.message(Command("admin"))
@router.message(F.text.in_({"👑 Панель управления", "Админы", "админы", "Админ-панель"}))
async def admin_panel_handler(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id if message.from_user else 0
    if not await is_moderator_or_higher(user_id):
        await message.answer("⛔ У вас нет доступа к панели администратора.")
        return

    text = (
        "👑 <b>Панель управления проектом FixLand</b>\n\n"
        "Выберите раздел для работы с ботом:"
    )
    await message.answer(text, reply_markup=admin_panel_kb(), parse_mode="HTML")


@router.callback_query(F.data == "admin:main")
async def admin_main_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    if not await is_moderator_or_higher(user_id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    text = (
        "👑 <b>Панель управления проектом FixLand</b>\n\n"
        "Выберите раздел для работы с ботом:"
    )
    try:
        await callback.message.edit_text(text, reply_markup=admin_panel_kb(), parse_mode="HTML")
    except Exception:
        await callback.message.answer(text, reply_markup=admin_panel_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:close")
async def admin_close_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer("Панель закрыта.")


@router.callback_query(F.data == "admin:stats")
async def admin_stats_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await is_moderator_or_higher(user_id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    stats = await get_statistics()

    text = (
        "📊 <b>Статистика проекта FixLand:</b>\n\n"
        f"👥 Всего пользователей: <b>{stats['users_count']}</b>\n"
        f"👮 Состав персонала: <b>{stats['staff_count']}</b>\n\n"
        f"🛒 <b>Заказы и магазин:</b>\n"
        f"• Всего заказов: <b>{stats['orders_total']}</b>\n"
        f"• ✅ Одобрено: <b>{stats['orders_approved']}</b>\n"
        f"• ⏳ Ожидают проверки: <b>{stats['orders_pending']}</b>\n"
        f"• ❌ Отклонено: <b>{stats['orders_rejected']}</b>\n"
        f"• 💵 Общая выручка: <b>{stats['total_revenue']:,} ₽</b>\n\n"
        f"📝 <b>Заявки в команду:</b>\n"
        f"• Всего заявок: <b>{stats['apps_total']}</b> (Ожидают: <b>{stats['apps_pending']}</b>)\n\n"
        f"🚨 <b>Жалобы:</b>\n"
        f"• Всего жалоб: <b>{stats['complaints_total']}</b> (Ожидают: <b>{stats['complaints_pending']}</b>)"
    )

    await callback.message.edit_text(text, reply_markup=admin_back_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:staff")
async def admin_staff_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await is_moderator_or_higher(user_id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    staff_members = await get_all_staff()
    text = "👥 <b>Список персонала и медиа:</b>\n\n"
    if not staff_members:
        text += "<i>В базе пока нет добавленных сотрудников.</i>\n\n"
    else:
        for idx, s in enumerate(staff_members, 1):
            r_title = ROLE_TITLES.get(s["role"], s["role"])
            u_tag = s.get("username") or f"ID: {s['user_id']}"
            text += f"{idx}. {r_title} — <code>{u_tag}</code> (Добавил: {s.get('added_by', '—')})\n"
        text += "\n"

    text += "<i>Назначить/снять роль можно в группе администрации командами:</i>\n"
    text += "<code>/роль медиа &lt;ID&gt;</code>\n<code>/роль модер &lt;ID&gt;</code>\n<code>/роль хелпер &lt;ID&gt;</code>\n<code>/роль снять &lt;ID&gt;</code>"

    await callback.message.edit_text(text, reply_markup=admin_back_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:requisites")
async def admin_requisites_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not await is_moderator_or_higher(user_id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    settings = await get_all_settings()

    text = (
        "⚙️ <b>Платёжные реквизиты и системные настройки:</b>\n\n"
        f"🇷🇺 <b>Карта РФ / СБП:</b>\n{settings.get('requisites_card_rf', '—')}\n\n"
        f"🇪🇺 <b>Карта Европы:</b>\n{settings.get('requisites_card_eu', '—')}\n\n"
        f"🅿️ <b>PayPal:</b>\n{settings.get('requisites_paypal', '—')}\n\n"
        f"💸 <b>FunPay:</b>\n{settings.get('requisites_funpay', '—')}\n\n"
        f"⚡ <b>CryptoBot:</b>\n{settings.get('requisites_crypto', '—')}\n\n"
        f"💬 <b>Другое:</b>\n{settings.get('requisites_other', '—')}\n\n"
        f"🔓 <b>Цена разбана:</b> {settings.get('unban_price', '150')} ₽\n"
        f"🔈 <b>Цена размута:</b> {settings.get('unmute_price', '75')} ₽\n"
        f"📞 <b>Поддержка:</b> {settings.get('support_contact', 'https://t.me/Hupiiaristo')}\n\n"
        "<i>Нажмите кнопку ниже, чтобы изменить соответствующий пункт:</i>"
    )
    await callback.message.edit_text(text, reply_markup=admin_requisites_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("admin_set:"))
async def admin_set_setting_prompt(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if not await is_moderator_or_higher(user_id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    key = callback.data.split(":")[1]
    titles = {
        "requisites_card_rf": "Реквизиты карты РФ / СБП",
        "requisites_card_eu": "Реквизиты европейской карты",
        "requisites_paypal": "Реквизиты PayPal",
        "requisites_funpay": "Ссылка / инструкция FunPay",
        "requisites_crypto": "Кошелек CryptoBot / USDT",
        "requisites_other": "Текст для других способов оплаты",
        "unban_price": "Стоимость разбана (в рублях)",
        "unmute_price": "Стоимость размута (в рублях)",
        "support_contact": "Ссылка на поддержку (@username или URL)"
    }
    title = titles.get(key, key)

    await state.set_state(AdminState.waiting_for_setting_value)
    await state.update_data(setting_key=key, setting_title=title)

    current_val = await get_setting(key, "Не задано")
    text = (
        f"✏️ <b>Редактирование: {title}</b>\n\n"
        f"Текущее значение:\n<code>{current_val}</code>\n\n"
        "<b>Отправьте новое значение ответным сообщением:</b>"
    )
    await callback.message.edit_text(text, reply_markup=admin_back_kb(), parse_mode="HTML")
    await callback.answer()


@router.message(AdminState.waiting_for_setting_value)
async def admin_save_setting_value(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not await is_moderator_or_higher(user_id):
        await state.clear()
        return

    new_value = message.text.strip() if message.text else ""
    if not new_value:
        await message.answer("⚠️ Значение не может быть пустым. Введите новое значение:")
        return

    data = await state.get_data()
    key = data["setting_key"]
    title = data.get("setting_title", key)

    await set_setting(key, new_value)
    await state.clear()

    await message.answer(
        f"✅ <b>Параметр «{title}» успешно сохранен!</b>\n\n"
        f"Новое значение:\n<code>{new_value}</code>",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )


# Рассылка всем игрокам
@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_prompt(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if not await is_admin_user(user_id):
        await callback.answer("⛔ Рассылка доступна только главным администраторам!", show_alert=True)
        return

    await state.set_state(AdminState.waiting_for_broadcast)
    await callback.message.edit_text(
        "📢 <b>Рассылка сообщений</b>\n\n"
        "Отправьте сообщение (текст, фото с описанием), которое будет разослано всем пользователям бота:",
        reply_markup=admin_back_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminState.waiting_for_broadcast)
async def admin_execute_broadcast(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if not await is_admin_user(user_id):
        await state.clear()
        return

    await state.clear()
    users = await get_all_users()
    total = len(users)
    success = 0
    blocked = 0

    status_msg = await message.answer(f"⏳ Начинаю рассылку для {total} пользователей...")

    for u in users:
        target_id = u["user_id"]
        try:
            if message.photo:
                await message.bot.send_photo(
                    chat_id=target_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption,
                    parse_mode="HTML"
                )
            else:
                await message.bot.send_message(
                    chat_id=target_id,
                    text=message.text,
                    parse_mode="HTML"
                )
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            blocked += 1

    await status_msg.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"• Всего пользователей: <b>{total}</b>\n"
        f"• Успешно доставлено: <b>{success}</b>\n"
        f"• Заблокировали бота / ошибка: <b>{blocked}</b>",
        reply_markup=admin_panel_kb(),
        parse_mode="HTML"
    )
