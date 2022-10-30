from abc import ABC, abstractmethod
from enum import Enum


class Storage(ABC):

    @abstractmethod
    def get_state(self, chat_id: int) -> Enum | None:
        raise NotImplementedError

    @abstractmethod
    def get_data(self, chat_id: int) -> dict:
        raise NotImplementedError

    @abstractmethod
    def set_state(self, chat_id: int, state: Enum) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_data(self, chat_id: int, data: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def destroy_state(self, chat_id: int):
        raise NotImplementedError

    @abstractmethod
    def destroy_data(self, chat_id: int):
        raise NotImplementedError

    @abstractmethod
    def destroy(self, chat_id: int):
        raise NotImplementedError

    @abstractmethod
    def update_data(self, chat_id: int, **kwargs):
        raise NotImplementedError