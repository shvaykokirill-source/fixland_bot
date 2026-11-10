from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from config import config
from database import add_user, is_moderator_or_higher, get_setting
from keyboards import main_menu_kb, apply_menu_kb, support_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else None
    full_name = message.from_user.full_name

    # Сохраняем пользователя в БД
    await add_user(user_id, username, full_name)

    is_admin_or_moder = await is_moderator_or_higher(user_id)

    welcome_text = (
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Добро пожаловать в официальный Telegram-бот проекта <b>FixLand Minecraft</b>! ⚔️\n\n"
        "Здесь вы можете:\n"
        "• 💎 Приобрести донат-привилегии, валюту, разбан или размут\n"
        "• 📝 Подать заявку на должность Хелпера или Медиа-партнёра\n"
        "• 🚨 Отправить жалобу на нарушителя или администратора\n"
        "• 🎬 Получить доступ к Медиа-Центру и выплатам за видео\n"
        "• ❓ Задать вопрос и обратиться в службу поддержки\n\n"
        "<i>Используйте кнопки меню ниже для навигации:</i>"
    )

    await message.answer(
        welcome_text,
        reply_markup=main_menu_kb(is_admin_or_moder),
        parse_mode="HTML"
    )

@router.message(F.text == "📝 Подать заявку")
async def show_applications(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📝 <b>Выберите направление для подачи заявки:</b>\n\n"
        "• ⚔️ <b>Хелпер</b> — станьте частью Команды Проекта, следите за чатом и порядком на сервере.\n"
        "• 🎬 <b>Медиа</b> — получайте выплаты, кейсы и привилегии за съемку видео/стримов.",
        reply_markup=apply_menu_kb(),
        parse_mode="HTML"
    )

@router.message(F.text.in_({"❓ Вопросы / Поддержка", "💬 Поддержка", "❓ Вопросы"}))
async def show_support(message: types.Message, state: FSMContext):
    await state.clear()
    support_link = await get_setting("support_contact", "https://t.me/Hupiiaristo")
    
    support_text = (
        "❓ <b>ЦЕНТР ПОДДЕРЖКИ И ВОПРОСОВ FIXLAND</b>\n\n"
        "Возникли сложности с покупкой, есть вопросы по игровому процессу или нужна помощь администратора?\n\n"
        "👤 <b>Главный администратор поддержки:</b> @Hupiiaristo\n"
        f"🔗 <b>Прямая ссылка для связи:</b> {support_link}\n\n"
        "Мы всегда рады помочь вам оперативно решить любую проблему! Нажмите кнопку ниже для перехода в диалог:"
    )
    await message.answer(support_text, reply_markup=support_kb(support_link), parse_mode="HTML")

@router.callback_query(F.data == "faq_info")
async def show_faq(callback: types.CallbackQuery):
    faq_text = (
        "📋 <b>ЧАСТЫЕ ВОПРОСЫ (FAQ):</b>\n\n"
        "1. <b>Когда придёт донат после отправки чека?</b>\n"
        "Обычно проверка чека занимает от 5 до 15 минут. В ночное время проверка может занять чуть больше времени.\n\n"
        "2. <b>Как подать заявку в команду проекта?</b>\n"
        "Нажмите кнопку <code>📝 Подать заявку</code> в главном меню и выберите «Заявка на Хелпера».\n\n"
        "3. <b>Что делать, если меня забанили по ошибке?</b>\n"
        "Подайте жалобу в разделе <code>🚨 Подать жалобу</code> -> <code>🛡️ Жалоба на команду проекта</code> или обратитесь в поддержку @Hupiiaristo."
    )
    await callback.message.answer(faq_text, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "cancel_action")
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    is_admin_or_moder = await is_moderator_or_higher(callback.from_user.id)
    await callback.message.answer("❌ Действие отменено.", reply_markup=main_menu_kb(is_admin_or_moder))
    await callback.answer("Отменено")
