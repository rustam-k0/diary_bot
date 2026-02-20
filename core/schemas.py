from pydantic import BaseModel, Field
from typing import List

class DiaryEntry(BaseModel):
    """
    Структурированная дневниковая запись, извлеченная из голосового сообщения.
    """
    facts: List[str] = Field(
        ..., 
        description="Сухие факты, описанные пользователем. Что произошло, без воды."
    )
    stressors: List[str] = Field(
        default_factory=list, 
        description="Триггеры или факторы стресса, упомянутые пользователем."
    )
    metrics: dict = Field(
        default_factory=dict, 
        description="Любые числовые показатели: часы сна, оценка настроения, кол-во работы."
    )
    action_items: List[str] = Field(
        default_factory=list, 
        description="Планы на будущее, задачи или следующие шаги."
    )
