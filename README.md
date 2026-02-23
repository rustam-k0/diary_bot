# Fast Voice-to-Text Bot

Минималистичный, быстрый бот для мгновенного перевода потока мыслей (голосовых сообщений) в текст. Работает полностью локально, без использования сторонних API (OpenAI/Google) и дополнительных LLM для анализа. Главный приоритет — скорость.

## Сценарий использования (Current State)

1. Вы отправляете боту голосовое сообщение.
2. Бот мгновенно скачивает его и конвертирует в `.wav` прямо в оперативной памяти с помощью FFmpeg.
3. Локальная модель `faster-whisper` (оптимизированная под CPU) переводит голос в текст и сразу отправляет вам ответ.
4. Отсутствуют любые задержки на анализ или перефразирование (LLM вырезано для скорости).

## Технический стек (Stack)

*   **Python 3.11+**, **aiogram 3.x**
*   **faster-whisper** (STT движок)
*   **FFmpeg** (конвертация)
*   **pytest, pytest-asyncio** (для тестирования)

## Локальный запуск (Local Development)

1. Установите систему `ffmpeg` (например, `brew install ffmpeg` для Mac или `apt install ffmpeg` для Linux).
2. Создайте виртуальное окружение: `python -m venv venv`
3. Активируйте: `source venv/bin/activate`
4. Установите зависимости: `pip install -r requirements.txt`
5. Скопируйте `.env.example` в `.env` и добавьте ваш `BOT_TOKEN`.
6. Запустите бота: `python -m tg_bot.bot`

## Тестирование
```bash
source venv/bin/activate
pytest tests/
```

---

## Варианты деплоя в интернет (Online Deployment)

Чтобы бот работал не локально, а онлайн 24/7, вам потребуется виртуальный сервер (VPS) с установленным Linux (например, Ubuntu 22.04). Модели faster-whisper (tiny/base) отлично работают на недорогих VPS (от 2 GB RAM / 2 CPU).

### Вариант 1: Деплой как системный сервис (Systemd)

Самый простой способ заставить бота работать в фоне и автоматически перезапускаться.

1. Подключитесь к VPS: `ssh root@your_server_ip`
2. Обновите пакеты и установите ffmpeg: `sudo apt update && sudo apt install ffmpeg python3-venv`
3. Склонируйте ваш код на сервер (например, в `/opt/fast_bot`).
4. Настройте окружение внутри папки проекта:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. Добавьте ваш токен: `nano .env` (и впишите `BOT_TOKEN=...`).
6. Создайте Systemd сервис: `sudo nano /etc/systemd/system/fastbot.service`
   ```ini
   [Unit]
   Description=Fast Telegram Voice Bot
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/opt/fast_bot
   ExecStart=/opt/fast_bot/venv/bin/python -m tg_bot.bot
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
7. Запустите и добавьте в автозагрузку:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable fastbot
   sudo systemctl start fastbot
   sudo systemctl status fastbot
   ```

### Вариант 2: Деплой через Docker (Рекомендуемый)

Если вы хотите изолировать приложение.

1. Установите Docker на вашем VPS.
2. Создайте `Dockerfile` в корне проекта:
   ```dockerfile
   FROM python:3.11-slim
   RUN apt-update && apt-install -y ffmpeg
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   CMD ["python", "-m", "tg_bot.bot"]
   ```
3. Соберите и запустите образ:
   ```bash
   docker build -t fastbot .
   docker run -d --name bot_instance --env-file .env fastbot
   ```

*Примечание: для высокой нагрузки и веб-хуков (Webhooks) потребуется переход от long-polling (`dp.start_polling()`) на FastAPI/Aiohttp, а также настройка Nginx в качестве Reverse Proxy.*