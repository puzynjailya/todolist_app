import marshmallow_dataclass
import requests

from bot.tg.dc import SendMessageResponse, GetUpdatesResponse


class TgClient:

    def __init__(self, token: str):
        self.token = token

    def get_url(self, method):
        return f'https://api.telegram.org/bot{self.token}/{method}'

    def get_updates(self, offset: int=0, timeout: int=60) -> GetUpdatesResponse:
        actual_url = self.get_url('getUpdates')
        response = requests.get(url=actual_url, params={'offset': offset, 'timeout': timeout})
        GetUpdatesSchema = marshmallow_dataclass.class_schema(GetUpdatesResponse)
        return GetUpdatesSchema().load(response.json())

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        actual_url = self.get_url('sendMessage')
        response = requests.post(url=actual_url, json={'chat_id': chat_id, 'text': text})
        SendMessageSchema = marshmallow_dataclass.class_schema(SendMessageResponse)
        return SendMessageSchema().load(response.json())

