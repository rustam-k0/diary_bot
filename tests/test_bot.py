import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from aiogram.types import Message, Chat, Voice, File
from aiogram import Bot

from tg_bot.handlers import format_entry, handle_voice, handle_text
from core.schemas import DiaryEntry

def test_format_entry():
    """Проверка форматирования объекта DiaryEntry в Markdown."""
    entry = DiaryEntry(
        facts=["Проснулся в 7 утра", "Выпил кофе"],
        stressors=["Опоздал на автобус"],
        metrics={"Настроение": "5/10", "Сон": "6 часов"},
        action_items=["Лечь спать пораньше", "Купить молоко"]
    )
    
    result = format_entry(entry)
    
    assert "Проснулся в 7 утра" in result
    assert "Опоздал на автобус" in result
    assert "Настроение: 5/10" in result
    assert "Лечь спать пораньше" in result
    assert "⚠️ **Триггеры & Стресс:**" in result

@pytest.mark.asyncio
async def test_handle_text():
    """Проверка ответа на текстовое сообщение (заглушка)."""
    message_mock = AsyncMock(spec=Message)
    
    await handle_text(message_mock)
    
    # Проверяем, что бот ответил заглушкой
    message_mock.reply.assert_called_once()
    args, kwargs = message_mock.reply.call_args
    assert "Я дневник. Принимаю только голосовые сообщения" in args[0]

@pytest.mark.asyncio
@patch("tg_bot.handlers.convert_ogg_to_wav")
@patch("tg_bot.handlers.transcribe_audio")
@patch("tg_bot.handlers.extract_diary_entry")
async def test_handle_voice_success(mock_extract, mock_transcribe, mock_convert):
    """Интеграционный тест обработки голосового сообщения с моками сервисов."""
    
    # Мокаем внешний сервис
    mock_convert.return_value = b"fake_wav_data"
    mock_transcribe.return_value = "Распознанный текст из аудио"
    
    # Мокаем ответ LLM
    mock_extract.return_value = DiaryEntry(
        facts=["Тестовый факт"],
        stressors=[],
        metrics={},
        action_items=[]
    )
    
    # Мокаем бота и сообщение
    bot_mock = AsyncMock(spec=Bot)
    bot_mock.get_file.return_value = File(file_id="123", file_unique_id="123", file_path="fake/path.ogg", file_size=100)
    
    message_mock = AsyncMock(spec=Message)
    message_mock.chat = Chat(id=123456, type="private")
    message_mock.voice = Voice(file_id="123", file_unique_id="123", duration=10)
    
    # Мокаем первичное сообщение со статусом
    status_msg_mock = AsyncMock()
    status_msg_mock.message_id = 999
    message_mock.reply.return_value = status_msg_mock
    
    # Вызываем хэндлер
    await handle_voice(message_mock, bot_mock)
    
    # Проверяем вызовы
    bot_mock.get_file.assert_called_once_with("123")
    bot_mock.download_file.assert_called_once()
    
    mock_convert.assert_called_once()
    mock_transcribe.assert_called_once_with(b"fake_wav_data")
    mock_extract.assert_called_once_with("Распознанный текст из аудио")
    
    # Проверяем, что финальное сообщение было отредактировано с результатом
    assert bot_mock.edit_message_text.call_count >= 1
    last_call_args = bot_mock.edit_message_text.call_args[0]
    last_call_kwargs = bot_mock.edit_message_text.call_args[1]
    
    assert "Тестовый факт" in last_call_args[0]
    assert last_call_kwargs["chat_id"] == 123456
    assert last_call_kwargs["message_id"] == 999
