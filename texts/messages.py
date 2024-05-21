greeting_message = "Привет! Я бот напоминалка"

create_group_enter_name = (
    "Здесь вы можете создать группу для того чтобы иметь общие напоминания с другими людьми\n"
    "Чтобы продолжить, введите название группы. \n"
    "Для отмены используйте /cancel"
)

cancel_command = "❌ Операция отменена"
create_group_success = (
    "Отлично! Группа создана, вот ссылка на вашу группу. "
    "Отправьте её тем, кого хотите добавить к группе \n\n"
    "Ссылка:\n"
    "{link}"
)

# joining to remind group
user_already_in_group = "Вы уже в группе <b>{name} (#{id})</b>. Ливните."
user_joined_to_group = (
    "Вы присоединились к группе <b>{name} (#{id})</b>. \n"
    "Теперь вы будете получить общие напоминания."
)

# remind groups management
show_groups_list = "Вот список групп, в которых вы состоите. Выберите группу для просмотра и редактирования"
group_management = (
    "Выберите действие с <b>{name} (#{id})</b>\n\n"
    "Ссылка на вашу группочку:\n"
    "{link}"
)

# remind group deletion
delete_remind_group_success = (
    "Группа <b>{name} (#{id})</b> и все связанные с ней напоминания были успешно удалены.\n"
    "Все участники группы получили об этом уведомление."
)
delete_remind_group_fail = "🤔 Похоже, группа уже была удалена..."
delete_remind_group_notification = "Группа <b>{name} (#{id})</b> и все связанные с ней напоминания были удалены."

# other remind group management messages
remind_group_does_not_exists_error = "⚠️ Этой группы не существует!"

# leave from remind group
leave_from_remind_group = (
    "Вы вышли из группы <b>{name} (#{id})</b>. "
    "Если захотите, вы можете вернуться в неё по ссылке."
)
leave_from_remind_group_fail = "🤷‍♂️ Похоже, вы уже не в группе. Незачем выходить ещё раз"

# notifications
remind_notification = (
    "🔔 Вам новое напоминание!\n"
    "💬: {text}"
)
group_remind_notification = (
    "🔔 Вам новое напоминание из группы <b>{group} (#{id}</b>) от {user}\n"
    "💬: {text}"
)
leave_from_remind_group_notification = \
    "🔔 Пользователь <b>{user_name}</b> вышел из группы <b>{group_name} (#{group_id})</b>"

user_join_to_remind_group_notification = \
    "🔔 Пользователь <b>{user_name}</b> присоединился к группе <b>{group_name} (#{group_id})</b>"

group_remind_created_notification = (
    '{user} создал новое напоминание для группы <b>{name} (#{id})</b>.\n'
    'Напоминание:\n'
    '{time_text}, {text}'
)

# remind creation
remind_creation_successful = "☑️ Напоминание успешно создано"
entering_remind_creation = "Давай создадим новое напоминание! Для начала введи текст напоминания"
new_group_remind = (
    "Выберите группу, для которой хотите создать напоминание. "
    "Это напоминание получат все участники группы."
)
select_group_for_new_remind = (
    "Вы выбрали группу <b>{name} (#{id})</b>\n"
    "Теперь введите текст напоминания"
)
entering_remind_time = (
    "Окей, теперь давай определимся со временем\n"
    "Вы можете ввести время в свободной форме, или в формате DD/MM hh:mm"
)
edit_remind_time = "Введите новое время напоминания"
edit_remind_text = "Введите новый текст напоминания"
confirm_remind_creation = (
    "Почти готов, давай проверим, всё ли правильно?\n\n"
    "Напоминание будет <b>{time_text}</b>\n"
    "{text}"
)
time_from_past_error = (
    "Вы указали {time_text}\n"
    "Нельзя указывать дату из прошлого. Введите другую дату"
)
data_parse_error = "Неверный формат даты! Попробуйте ещё раз"
