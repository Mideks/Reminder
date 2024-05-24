import os
from pathlib import Path

from aiogram import Router, types, F

from remind_parser.STT import STT
from remind_parser.gpt import remind_summary

stt = STT()

router = Router()


# Хэндлер на получение голосового и аудио сообщения
@router.message(F.content_type.in_({
    types.ContentType.VOICE,
    types.ContentType.AUDIO,
    types.ContentType.DOCUMENT
}))
async def voice_message_handler(message: types.Message):
    """
    Обработчик на получение голосового и аудио сообщения.
    """
    if message.content_type == types.ContentType.VOICE:
        file_id = message.voice.file_id
    elif message.content_type == types.ContentType.AUDIO:
        file_id = message.audio.file_id
    elif message.content_type == types.ContentType.DOCUMENT:
        file_id = message.document.file_id
    else:
        await message.reply("Формат документа не поддерживается")
        return

    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"{file_id}.tmp")
    await message.bot.download_file(file_path, destination=file_on_disk)
    await message.reply("Аудио получено")

    text = stt.audio_to_text(file_on_disk)
    if not text:
        text = "Формат документа не поддерживается"

    await message.answer(f"Расшифровка:\n {text}")
    summary = remind_summary(text)
    await message.answer(f"Напоминания:\n {summary}")

    os.remove(file_on_disk)  # Удаление временного файла
