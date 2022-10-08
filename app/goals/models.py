from django.db import models
from django.utils import timezone

from core.models import User


class DatesModelMixin(models.Model):
    class Meta:
        abstract = True  # Помечаем класс как абстрактный – для него не будет таблички в БД

    created = models.DateTimeField(verbose_name="Дата создания")
    updated = models.DateTimeField(verbose_name="Дата последнего обновления")

    # Комментарий для себя
    # ----------------------------------------------------------------------------------------------------------------
    # Изменяем поведение модели при сохранении
    # Обязательно Важно не забывать вызывать метод суперкласса - super().save(*args, **kwargs) - чтобы гарантировать,
    # что объект все еще сохраняется в базе данных. Если вы забудете вызвать метод суперкласса,
    # поведение по умолчанию не произойдет, и база данных не будет затронута.
    # Также важно, чтобы вы передавали аргументы, которые можно передать методу модели -
    # это то, что делает часть *args, **kwargs.
    def save(self, *args, **kwargs):
        if not self.id:  # Когда модель только создается – у нее нет id
            self.created = timezone.now()
        self.updated = timezone.now()  # Каждый раз, когда вызывается save, проставляем свежую дату обновления
        return super().save(*args, **kwargs)


class GoalCategory(DatesModelMixin):
    user = models.ForeignKey(User, verbose_name='Автор', on_delete=models.RESTRICT)
    title = models.CharField(verbose_name='Название', max_length=255)
    is_deleted = models.BooleanField(verbose_name='В архиве', default=False)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Goal(DatesModelMixin):

    # Комментарий для себя
    # Для создания статуса и приоритета будем использовать классы Choises
    class Status(models.IntegerChoices):
        to_do = 1, 'К выполнению'
        in_progress = 2, 'В процессе'
        done = 3, 'Выполнено'
        archived = 4, 'Архив'

    class Priority(models.IntegerChoices):
        low = 1, 'Низкий'
        medium = 2, 'Средний'
        high = 3, 'Высокий'
        critical = 4, 'Критический'

    user = models.ForeignKey(User, verbose_name='Автор', on_delete=models.RESTRICT)
    title = models.CharField(verbose_name='Название', max_length=255)
    description = models.TextField(max_length=2000, verbose_name='Описание', null=True, blank=True)
    category = models.ForeignKey(to=GoalCategory,
                                 on_delete=models.CASCADE,
                                 verbose_name='Категория',
                                 related_name='goals')
    status = models.PositiveSmallIntegerField(verbose_name="Статус",
                                              choices=Status.choices,
                                              default=Status.to_do
                                              )
    priority = models.PositiveSmallIntegerField(verbose_name="Приоритет",
                                                choices=Priority.choices,
                                                default=Priority.medium
                                                )

    due_date = models.DateTimeField(verbose_name='Дата дедлайна')

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'

    def __str__(self):
        return self.title


class GoalComment(DatesModelMixin):
    goal = models.ForeignKey(to=Goal, verbose_name='цель', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(to=User, verbose_name='Автор', on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=255, verbose_name='Текст')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text



