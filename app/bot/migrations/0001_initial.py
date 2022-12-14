# Generated by Django 4.1 on 2022-10-26 21:21

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TgUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "chat_id",
                    models.BigIntegerField(unique=True, verbose_name="Chat Id"),
                ),
                (
                    "username",
                    models.CharField(
                        blank=True,
                        default=None,
                        max_length=150,
                        null=True,
                        validators=[django.core.validators.MinLengthValidator(1)],
                        verbose_name="Tg username",
                    ),
                ),
                (
                    "verification_code",
                    models.CharField(
                        blank=True,
                        default=None,
                        max_length=64,
                        null=True,
                        validators=[django.core.validators.MinLengthValidator(1)],
                        verbose_name="Verification code",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "??????",
                "verbose_name_plural": "????????",
            },
        ),
    ]
