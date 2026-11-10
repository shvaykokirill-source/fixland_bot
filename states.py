from aiogram.fsm.state import State, StatesGroup

# Состояния админ-панели
class AdminState(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_setting_value = State()
    waiting_for_role_user_id = State()
    waiting_for_reject_reason = State()

# Состояния анкеты на должность Хелпера (16 пунктов)
class HelperApplicationState(StatesGroup):
    step1_nick = State()
    step2_age = State()
    step3_adequacy = State()
    step4_literacy = State()
    step5_experience = State()
    step6_cheat_check = State()
    step7_programs = State()
    step8_mic_headphones = State()
    step9_hours = State()
    step10_why_you = State()
    step11_essay = State()
    step12_rules = State()
    step13_terms = State()
    step14_timezone = State()
    step15_tg_linked = State()
    step16_device = State()

# Состояния заявки в Медиа
class MediaApplicationState(StatesGroup):
    waiting_for_channel = State()
    waiting_for_stats = State()

# Состояния подачи жалобы (на игрока / на команду проекта)
class ComplaintState(StatesGroup):
    choosing_target = State()
    waiting_for_my_nick = State()
    waiting_for_target_nick = State()
    waiting_for_date = State()
    waiting_for_reason = State()
    waiting_for_evidence = State()
    waiting_for_additional = State()

# Состояния донат-магазина
class ShopState(StatesGroup):
    waiting_for_priv_nick = State()
    waiting_for_rub_amount = State()
    waiting_for_rub_nick = State()
    waiting_for_unban_nick = State()
    waiting_for_unmute_nick = State()
    waiting_for_payment_method = State()
    waiting_for_receipt = State()
    in_manager_chat = State()

# Состояния Медиа-Центра
class MediaCenterState(StatesGroup):
    waiting_for_payout_details = State()
    waiting_for_perk_request = State()
