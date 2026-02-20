import instructor
from openai import OpenAI
from core.schemas import DiaryEntry
from core.config import OLLAMA_URI, MODEL_NAME

# Инициализируем клиента OpenAI, направленного на локальный Ollama
# Патчим его с помощью instructor, чтобы гарантировать JSON на выходе
client = instructor.from_openai(
    OpenAI(
        base_url=OLLAMA_URI,
        api_key="ollama", # api_key не важен для ollama, но нужен для клиента
    ),
    mode=instructor.Mode.JSON,
)

def extract_diary_entry(text: str) -> DiaryEntry:
    """
    Извлекает структурированную запись из сырого текста 
    с помощью локальной модели qwen2.5:7b-instruct.
    """
    prompt = (
        "Ты беспощадный аналитический бот. Твоя задача — "
        "превратить хаотичную голосовую заметку (текст) в структурированный лог. "
        "Вся вода должна быть отброшена. Извлеки факты, триггеры стресса, метрики и планы.\n\n"
        f"Текст пользователя:\n{text}"
    )

    # instructor автоматически преобразует ответ LLM в Pydantic объект (DiaryEntry)
    res = client.chat.completions.create(
        model=MODEL_NAME,
        response_model=DiaryEntry,
        messages=[
            {"role": "system", "content": "Ты парсер. Извлеки данные по заданной JSON схеме. Никаких рассуждений, только данные."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0, # 0.0 для максимальной детерминированности и следования формату
    )
    
    return res
