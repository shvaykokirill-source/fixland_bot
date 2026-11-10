from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

# Главное меню пользователя
def main_menu_kb(is_admin_or_moder: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="💎 Донат-магазин"), KeyboardButton(text="📝 Подать заявку")],
        [KeyboardButton(text="🚨 Подать жалобу"), KeyboardButton(text="🎬 Медиа-центр")],
        [KeyboardButton(text="❓ Вопросы / Поддержка")]
    ]
    if is_admin_or_moder:
        keyboard.append([KeyboardButton(text="👑 Панель управления")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Кнопка отмены для Reply/Inline
def cancel_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_action")]
    ])

# Меню выбора заявок
def apply_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ Заявка на Хелпера (КП)", callback_data="apply:helper")],
        [InlineKeyboardButton(text="🎬 Заявка на Медиа-партнёра", callback_data="apply:media")]
    ])

# Меню подачи жалоб
def complaint_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Жалоба на игрока", callback_data="complaint:player")],
        [InlineKeyboardButton(text="🛡️ Жалоба на команду проекта", callback_data="complaint:staff")]
    ])

# Меню категорий магазина
def shop_categories_kb(privileges: list[dict]) -> InlineKeyboardMarkup:
    buttons = []
    # Привилегии
    for p in privileges:
        badge = f" {p['badge']}" if p.get('badge') else ""
        buttons.append([
            InlineKeyboardButton(text=f"👑 {p['name']}{badge} — {p['price']} ₽", callback_data=f"shop_priv:{p['code']}")
        ])
    
    # Дополнительные товары
    buttons.append([
        InlineKeyboardButton(text="💰 Донат-рубли Ⓟ", callback_data="shop_item:rubles")
    ])
    buttons.append([
        InlineKeyboardButton(text="🔓 Разбан на сервере", callback_data="shop_item:unban"),
        InlineKeyboardButton(text="🔈 Размут на сервере", callback_data="shop_item:unmute")
    ])
    buttons.append([
        InlineKeyboardButton(text="📦 Мои заказы", callback_data="shop_my_orders")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Выбор способов оплаты
def payment_methods_kb(item_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Банковская карта РФ / СБП", callback_data=f"pay:{item_code}:card_rf")],
        [InlineKeyboardButton(text="🇪🇺 Карта Европы (Visa/Mastercard)", callback_data=f"pay:{item_code}:card_eu")],
        [InlineKeyboardButton(text="🅿️ PayPal", callback_data=f"pay:{item_code}:paypal")],
        [InlineKeyboardButton(text="💸 FunPay", callback_data=f"pay:{item_code}:funpay")],
        [InlineKeyboardButton(text="⚡ CryptoBot / Криптовалюта", callback_data=f"pay:{item_code}:crypto")],
        [InlineKeyboardButton(text="💬 Другое (Обсудить с менеджером)", callback_data=f"pay:{item_code}:other")],
        [InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_action")]
    ])

# Кнопка отправки чека
def receipt_action_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить заказ", callback_data="cancel_action")]
    ])

# Меню поддержки и вопросов
def support_kb(support_url: str = "https://t.me/Hupiiaristo") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написать в поддержку (Telegram)", url=support_url)],
        [InlineKeyboardButton(text="📋 Частые вопросы (FAQ)", callback_data="faq_info")]
    ])

# Меню медиа-центра
def media_center_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 Запросить выплату", callback_data="media_payout")],
        [InlineKeyboardButton(text="🎁 Запросить промокод / бонусы", callback_data="media_perks")],
        [InlineKeyboardButton(text="📜 Расценки и критерии", callback_data="media_rates")]
    ])

# Меню заявки в медиа для обычных игроков
def media_guest_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📽️ Подать заявку на Медиа", callback_data="apply:media")]
    ])

# --- Клавиатуры модерации в чате администрации ---

# Модерация заказа/доната
def order_admin_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"order_act:approve:{order_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"order_act:reject:{order_id}")
        ]
    ])

# Модерация заявки на Хелпера
def app_admin_kb(app_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять кандидата", callback_data=f"app_act:approve:{app_id}"),
            InlineKeyboardButton(text="❌ Отклонить заявку", callback_data=f"app_act:reject:{app_id}")
        ]
    ])

# Модерация жалобы
def complaint_admin_kb(comp_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить (Наказать)", callback_data=f"comp_act:approve:{comp_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"comp_act:reject:{comp_id}")
        ]
    ])

# Модерация медиа-выплаты
def media_payout_admin_kb(req_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Выплачено", callback_data=f"media_act:approve:{req_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"media_act:reject:{req_id}")
        ]
    ])

# --- Админ-панель ---

def admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats"),
            InlineKeyboardButton(text="⚙️ Настройки и реквизиты", callback_data="admin:requisites")
        ],
        [
            InlineKeyboardButton(text="👥 Состав проекта", callback_data="admin:staff"),
            InlineKeyboardButton(text="📢 Рассылка", callback_data="admin:broadcast")
        ],
        [
            InlineKeyboardButton(text="❌ Закрыть панель", callback_data="admin:close")
        ]
    ])

def admin_requisites_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Карта РФ / СБП", callback_data="admin_set:requisites_card_rf")],
        [InlineKeyboardButton(text="🇪🇺 Карта Европы", callback_data="admin_set:requisites_card_eu")],
        [InlineKeyboardButton(text="🅿️ PayPal", callback_data="admin_set:requisites_paypal")],
        [InlineKeyboardButton(text="💸 FunPay", callback_data="admin_set:requisites_funpay")],
        [InlineKeyboardButton(text="⚡ CryptoBot", callback_data="admin_set:requisites_crypto")],
        [InlineKeyboardButton(text="💬 Другие способы", callback_data="admin_set:requisites_other")],
        [
            InlineKeyboardButton(text="🔓 Цена разбана", callback_data="admin_set:unban_price"),
            InlineKeyboardButton(text="🔈 Цена размута", callback_data="admin_set:unmute_price")
        ],
        [InlineKeyboardButton(text="📞 Ссылка поддержки", callback_data="admin_set:support_contact")],
        [InlineKeyboardButton(text="◀️ Назад в админку", callback_data="admin:main")]
    ])

def admin_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в админку", callback_data="admin:main")]
    ])
