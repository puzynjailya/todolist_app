from django.core.validators import MinLengthValidator
from django.db import models

from core.admin import User


class TgUser(models.Model):
    chat_id = models.BigIntegerField(verbose_name='Chat Id', unique=True, )
    username = models.CharField(max_length=150,
                                validators=[MinLengthValidator(1)],
                                null=True,
                                blank=True,
                                verbose_name='Tg username',
                                default=None)
    verification_code = models.CharField(verbose_name='Verification code',
                                         max_length=64,
                                         validators=[MinLengthValidator(1)],
                                         null=True,
                                         blank=True,
                                         default=None,)
    user = models.ForeignKey(to=User,
                             verbose_name='User',
                             on_delete=models.RESTRICT,
                             null=True,
                             default=None)

    class Meta:
        verbose_name = 'Телеграм пользователь'
        verbose_name_plural = 'Телеграм пользователи'
