from django.urls import path
from bot.views import VerificationBotView

urlpatterns=[
    path('verify', VerificationBotView.as_view(), name='user verification'),
]