import io
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message
from services.audio import convert_ogg_to_wav
from services.stt import transcribe_audio
from services.llm import extract_diary_entry

router = Router()

@router.message(F.voice)
async def handle_voice(message: Message, bot: Bot):
    """
    Обрабатывает голосовые сообщения.
    1. Скачивает OGG
    2. Конвертирует в WAV
    3. Транскрибирует текст (STT)
    4. Извлекает структурированную запись (LLM)
    5. Форматирует ответ в Markdown
    """
    # Сообщаем пользователю, что начали обработку
    status_msg = await message.reply("⏳ Выдыхаю. Начинаю анализ...")

    try:
        # 1. Скачиваем голосовое сообщение в память
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_bytes = io.BytesIO()
        await bot.download_file(file.file_path, file_bytes)
        ogg_data = file_bytes.getvalue()
        
        await bot.edit_message_text(
            "⏳ Конвертирую аудио...", 
            chat_id=message.chat.id, 
            message_id=status_msg.message_id
        )

        # 2. Конвертируем OGG -> WAV
        wav_data = convert_ogg_to_wav(ogg_data)
        
        await bot.edit_message_text(
            "⏳ Слушаю и перевожу в текст...", 
            chat_id=message.chat.id, 
            message_id=status_msg.message_id
        )

        # 3. Транскрибуем с помощью STT
        raw_text = transcribe_audio(wav_data)
        
        if not raw_text:
            raise ValueError("Не удалось распознать текст из голосового.")
        
        await bot.edit_message_text(
            "⏳ Включаю циничного аналитика...", 
            chat_id=message.chat.id, 
            message_id=status_msg.message_id
        )

        # 4. Прогоняем через LLM-пайплайн
        entry = extract_diary_entry(raw_text)
        
        # 5. Собираем Markdown-строку
        response_text = format_entry(entry)
        
        # Отправляем результат
        await bot.edit_message_text(
            response_text,
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        # В случае ошибки логируем и сообщаем пользователю
        logging.error(f"Error handling voice: {e}")
        await bot.edit_message_text(
            f"❌ Ошибка обработки: {str(e)}\n\n*Возможно сервер Ollama не запущен или модель не скачана.*",
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode="Markdown"
        )


def format_entry(entry) -> str:
    """
    Форматирует Pydantic объект DiaryEntry в красивый текст Markdown без воды.
    """
    text = "📝 **Анализ Записи:**\n\n"
    
    text += "🔹 **Сухие Факты:**\n"
    if entry.facts:
        for f in entry.facts:
            text += f"- {f}\n"
    else:
        text += "- Нет явных фактов\n"
        
    if entry.stressors:
        text += "\n⚠️ **Триггеры & Стресс:**\n"
        for s in entry.stressors:
            text += f"- {s}\n"
            
    if entry.metrics:
        text += "\n📊 **Метрики:**\n"
        for k, v in entry.metrics.items():
            text += f"- {k}: {v}\n"
            
    if entry.action_items:
        text += "\n🎯 **Ближайшие шаги:**\n"
        for a in entry.action_items:
            text += f"- [ ] {a}\n"
            
    return text

@router.message(F.text)
async def handle_text(message: Message):
    """
    Приветственное или заглушечное сообщение для текстовых вводов.
    """
    await message.reply(
        "Я дневник. Принимаю только голосовые сообщения.\n"
        "Выговаривайся, а я структурирую и выкину всё лишнее."
    )
