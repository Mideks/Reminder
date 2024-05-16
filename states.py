from aiogram.fsm.state import StatesGroup, State


# Состояния для создания напоминаний
class CreateNewReminder(StatesGroup):
    entering_text = State()  # ввод текста напоминания
    entering_time = State()  # ввод времени напоминания
    confirm_creation = State()  # подтверждаем создание напоминания
    finish_creation = State()  # завершение создания напоминания
    editing_text = State() # редактируем текст
    editing_time = State() # редактируем время


class CreateReminderGroup(StatesGroup):
    entering_name = State()
