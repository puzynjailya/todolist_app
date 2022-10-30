from dataclasses import dataclass, field
from typing import List, Optional
from marshmallow import EXCLUDE


@dataclass
class Chat:
    id: int
    username: str
    type: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class MessageFrom:
    id: int
    is_bot: bool
    username: str
    first_name: Optional[str]
    last_name: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class Message:
    message_id: int
    chat: Chat
    from_: MessageFrom = field(metadata={"data_key": "from"})
    text: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class UpdateObj:
    update_id: int
    message: Message

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetUpdatesResponse:
    ok: bool
    result: List[UpdateObj]

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    ok: bool
    result: Message

    class Meta:
        unknown = EXCLUDE
