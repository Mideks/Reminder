create_group_enter_name = (
    "Здесь вы можете создать группу для того чтобы иметь общие напоминания с другими людьми\n"
    "Чтобы продолжить, введите название группы. \n"
    "Для отмены используйте /cancel"
)

cancel_command = "Операция отменена"
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
user_join_to_remind_group_notification = \
    "🔔 Пользователь <b>{user_name}</b> присоединился к группе <b>{group_name} (#{group_id})</b>"

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

leave_from_remind_group_notification = \
    "🔔 Пользователь <b>{user_name}</b> вышел из группы <b>{group_name} (#{group_id})</b>"
leave_from_remind_group_fail = "🤷‍♂️ Похоже, вы уже не в группе. Незачем выходить ещё раз"
