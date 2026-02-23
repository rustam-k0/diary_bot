import io
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message
from services.audio import convert_ogg_to_wav
from services.stt import transcribe_audio

router = Router()

@router.message(F.voice)
async def handle_voice(message: Message, bot: Bot):
    """
    Обрабатывает голосовые сообщения максимально быстро.
    1. Скачивает OGG
    2. Конвертирует в WAV
    3. Транскрибирует текст (STT) и сразу отвечает
    """
    status_msg = await message.reply("⏳ Распознаю...")

    try:
        # 1. Скачиваем голосовое сообщение в память
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_bytes = io.BytesIO()
        await bot.download_file(file.file_path, file_bytes)
        ogg_data = file_bytes.getvalue()

        # 2. Конвертируем OGG -> WAV
        wav_data = convert_ogg_to_wav(ogg_data)
        
        # 3. Транскрибуем с помощью STT
        raw_text = transcribe_audio(wav_data)
        
        if not raw_text:
            raise ValueError("Не удалось распознать текст из голосового или тишина.")
        
        # Отправляем результат
        await bot.edit_message_text(
            f"📝 **Текст:**\n\n{raw_text}",
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logging.error(f"Error handling voice: {e}")
        await bot.edit_message_text(
            f"❌ Ошибка обработки: {str(e)}",
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode="Markdown"
        )

@router.message(F.text)
async def handle_text(message: Message):
    """
    Заглушечное сообщение для текстовых вводов.
    """
    await message.reply(
        "Я бот-транскрибатор. Отправь мне голосовое сообщение, и я мгновенно переведу его в текст."
    )

