from enum import Enum
from pydantic import BaseModel
from bot.tg.state_machine.base import Storage


class DataStorage(BaseModel):
    state: Enum | None = None
    data: dict = {}


class MemoryStorage(Storage):
    '''
    Класс для хранения данных о состоянии в памяти в памяти.
    При перезапуске приложения все данные будут затираться
    '''

    def __init__(self):
        self.data: dict[int, DataStorage] = {}

    def _resolve_data(self, chat_id: int):
        if chat_id not in self.data:
            self.data[chat_id] = DataStorage()
        return self.data[chat_id]

    def get_state(self, chat_id: int) -> Enum | None:
        return self._resolve_data(chat_id).state

    def get_data(self, chat_id: int) -> dict:
        return self._resolve_data(chat_id).data

    def set_state(self, chat_id: int, state: Enum) -> None:
        self._resolve_data(chat_id).state = state

    def set_data(self, chat_id: int, data: dict) -> None:
        self._resolve_data(chat_id).data = data

    def destroy_state(self, chat_id: int) -> None:
        self._resolve_data(chat_id).state = None

    def destroy_data(self, chat_id: int) -> None:
        self._resolve_data(chat_id).data.clear()

    def destroy(self, chat_id: int) -> bool:
        return bool(self.data.pop(chat_id, None))

    def update_data(self, chat_id: int, **kwargs):
        self._resolve_data(chat_id).data.update(**kwargs)
