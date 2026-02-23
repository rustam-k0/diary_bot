import pytest
from unittest.mock import AsyncMock, patch
from aiogram.types import Message, Chat, Voice, File
from aiogram import Bot

from tg_bot.handlers import handle_voice, handle_text

@pytest.mark.asyncio
async def test_handle_text():
    """Проверка ответа на текстовое сообщение (заглушка)."""
    message_mock = AsyncMock(spec=Message)
    # MagicMock -> AsyncMock for reply
    message_mock.reply = AsyncMock()
    
    await handle_text(message_mock)
    
    # Проверяем, что бот ответил заглушкой
    message_mock.reply.assert_called_once()
    args, kwargs = message_mock.reply.call_args
    assert "Я бот-транскрибатор" in args[0]

@pytest.mark.asyncio
@patch("tg_bot.handlers.convert_ogg_to_wav")
@patch("tg_bot.handlers.transcribe_audio")
async def test_handle_voice_success(mock_transcribe, mock_convert):
    """Интеграционный тест обработки голосового сообщения с моками сервисов."""
    
    # Мокаем внешний сервис
    mock_convert.return_value = b"fake_wav_data"
    mock_transcribe.return_value = "Распознанный текст из аудио"
    
    # Мокаем бота и сообщение
    bot_mock = AsyncMock(spec=Bot)
    bot_mock.get_file = AsyncMock(return_value=File(file_id="123", file_unique_id="123", file_path="fake/path.ogg", file_size=100))
    bot_mock.download_file = AsyncMock()
    bot_mock.edit_message_text = AsyncMock()
    
    message_mock = AsyncMock(spec=Message)
    message_mock.chat = Chat(id=123456, type="private")
    message_mock.voice = Voice(file_id="123", file_unique_id="123", duration=10)
    
    # Мокаем первичное сообщение со статусом
    status_msg_mock = AsyncMock()
    status_msg_mock.message_id = 999
    message_mock.reply = AsyncMock(return_value=status_msg_mock)
    
    # Вызываем хэндлер
    await handle_voice(message_mock, bot_mock)
    
    # Проверяем вызовы
    bot_mock.get_file.assert_called_once_with("123")
    bot_mock.download_file.assert_called_once()
    
    mock_convert.assert_called_once()
    mock_transcribe.assert_called_once_with(b"fake_wav_data")
    
    # Проверяем, что финальное сообщение было отредактировано с результатом
    assert bot_mock.edit_message_text.call_count >= 1
    last_call_args = bot_mock.edit_message_text.call_args[0]
    last_call_kwargs = bot_mock.edit_message_text.call_args[1]
    
    assert "Распознанный текст из аудио" in last_call_args[0]
    assert last_call_kwargs["chat_id"] == 123456
    assert last_call_kwargs["message_id"] == 999
