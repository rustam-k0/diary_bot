import io
from faster_whisper import WhisperModel

# Инициализируем модель (загружается единажды при старте)
# Используем 'base' для скорости, можно поменять на 'small' или 'medium' 
# для лучшего качества распознавания.
# device="cpu", compute_type="int8" для оптимизации на CPU.
model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_audio(wav_data: bytes) -> str:
    """
    Транскрибует WAV аудио (байты) в текст с помощью faster-whisper.
    """
    # Превращаем байты в file-like объект
    audio_file = io.BytesIO(wav_data)
    
    # Запускаем распознавание
    segments, info = model.transcribe(audio_file, beam_size=5, language="ru")
    
    # Собираем все сегменты текста в одну строку
    text = " ".join([segment.text for segment in segments])
    
    return text.strip()
