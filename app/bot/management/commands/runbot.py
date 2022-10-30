import logging
import secrets
from datetime import datetime, timedelta
from enum import IntEnum, auto

from django.core.management.base import BaseCommand, CommandError
from pydantic import BaseModel

from ToDoList import settings
from bot.models import TgUser
from bot.tg.clients import TgClient
from bot.tg.dc import Message
from bot.tg.state_machine.memory_storage import MemoryStorage
from goals.models import Goal, GoalCategory, BoardParticipant

# Добавляем логгер
logger = logging.getLogger(__name__)


# Добавляем состояния
class StateEnum(IntEnum):
    CREATE_CATEGORY_SELECT = auto()
    CHOSEN_CATEGORY = auto()


# Создаем модель данных для целей, которую будем использовать для формирования данных
class NewGoal(BaseModel):
    cat_id: int | None = None
    goal_title: str | None = None

    @property
    def is_completed(self) -> bool:
        return None not in [self.cat_id, self.goal_title]


class Command(BaseCommand):
    help = 'Запуск телеграмм бота'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.TG_TOKEN)
        self.storage = MemoryStorage()

    def handle(self, *args, **options):
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(message=item.message)

    def _get_and_send_verification_code(self, message: Message, telegram_user: TgUser):
        # Создаем код, сохраняем его в БД, отправляем пользователю, чтобы он авторизовался
        code: str = secrets.token_hex(8)
        telegram_user.verification_code = code
        telegram_user.save(update_fields=('verification_code',))
        self.tg_client.send_message(chat_id=message.chat.id, text=f'Ваш код верификации {code}')

    def _get_goals_list(self, message: Message, telegram_user: TgUser):
        goals_list: list[str] = [
            f'№{goal.id} - {goal.title}'
            for goal in Goal.objects.filter(user_id=telegram_user.user_id).order_by('id')
        ]
        if goals_list:
            self.tg_client.send_message(chat_id=message.chat.id, text='\n'.join(goals_list))
        else:
            self.tg_client.send_message(chat_id=message.chat.id, text='Целей не найдено')

    def _get_categories_list(self, message: Message, telegram_user: TgUser):
        category_list: list[str] = [
            f'№{category.id} - {category.title}'
            for category in GoalCategory.objects.filter(board__participants__user_id=telegram_user.user_id,
                                                        is_deleted=False).order_by('id')
        ]
        if category_list:
            self.tg_client.send_message(chat_id=message.chat.id, text='Выберите категорию\n'+'\n'.join(category_list))
        else:
            self.tg_client.send_message(chat_id=message.chat.id, text='Категорий не найдено')

    def _get_selected_category(self, message: Message, telegram_user: TgUser):
        if message.text.isdigit():
            category_id = int(message.text)
            self.tg_client.send_message(chat_id=message.chat.id, text=f'Выбрана категория {category_id}')
            if GoalCategory.objects.filter(
                        board__participants__user_id=telegram_user.user_id,
                        board__participants__role__in=[BoardParticipant.Roles.writer, BoardParticipant.Roles.owner],
                        is_deleted=False,
                        id=category_id
                        ).exists():
                self.storage.update_data(chat_id=message.chat.id, cat_id=category_id)
                self.tg_client.send_message(chat_id=message.chat.id, text='Создайте цель цель')
                self.storage.set_state(chat_id=message.chat.id, state=StateEnum.CHOSEN_CATEGORY)
            else:
                self.tg_client.send_message(chat_id=message.chat.id, text='Категория не найдена')
        else:
            self.tg_client.send_message(chat_id=message.chat.id, text='Введено неверное значение')

    def _save_new_category(self, message: Message, telegram_user: TgUser):
        goal = NewGoal(**self.storage.get_data(telegram_user.chat_id))
        goal.goal_title = message.text
        if goal.is_completed:
            Goal.objects.create(
                title=goal.goal_title,
                category_id=goal.cat_id,
                user_id=telegram_user.user_id,
                due_date=datetime.now() + timedelta(days=31)
            )
            self.tg_client.send_message(message.chat.id, text=f'Создана новая цель: {goal.goal_title}')
        else:
            logger.warning('Goal creation error')
            self.tg_client.send_message(message.chat.id, text=f'Ошибка создания цели')

        self.storage.destroy(telegram_user.chat_id)

    def handle_verified_user(self, message: Message, telegram_user: TgUser):
        # Создаем новую задачу (цель)
        if message.text == '/create':
            self._get_categories_list(message, telegram_user)
            self.storage.set_state(message.chat.id, state=StateEnum.CREATE_CATEGORY_SELECT)
            self.storage.set_data(message.chat.id, data=NewGoal().dict())

        # Выводим все текущие задачи (цели)
        elif message.text == '/goals':
            self._get_goals_list(message, telegram_user)

        # Отменяем текущее состояние
        elif message.text == '/cancel' and self.storage.get_state(telegram_user.chat_id):
            self.storage.destroy(telegram_user.chat_id)
            self.tg_client.send_message(chat_id=message.chat.id, text='Отменено')

        # Обрабатываем состояния
        elif state := self.storage.get_state(telegram_user.chat_id):
            match state:
                case StateEnum.CHOSEN_CATEGORY:
                    self._save_new_category(message, telegram_user)
                case StateEnum.CREATE_CATEGORY_SELECT:
                    self._get_selected_category(message, telegram_user)
                case _:
                    logger.warning(f'Неизвестное состояние: {state}')

        elif message.text.startswith('/'):
            self.tg_client.send_message(chat_id=message.chat.id, text='Неизвестная команда')

    def handle_message(self, message: Message):
        # Находим пользователя, если его нет, то создаем
        user_object, created = TgUser.objects.select_related('user').get_or_create(
                                                            chat_id=message.chat.id,
                                                            defaults={'username': message.from_.username}
                                                            )
        if user_object.user:
            self.handle_verified_user(message, telegram_user=user_object)
        # Авторизуем пользователя
        else:
            self._get_and_send_verification_code(message, telegram_user=user_object)



