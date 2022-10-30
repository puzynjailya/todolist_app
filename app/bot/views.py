from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from ToDoList import settings
from bot.models import TgUser
from bot.serializers import VerificationBotSerializer
from bot.tg.clients import TgClient


class VerificationBotView(generics.UpdateAPIView):
    model = TgUser
    serializer_class = VerificationBotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)

        tg_user = serialized_data.validated_data['tg_user']
        tg_user.user = self.request.user
        tg_user.save(update_fields=('user',))

        tg_data = self.get_serializer(tg_user)
        TgClient(settings.TG_TOKEN).send_message(chat_id=tg_user.chat_id, text='Ура, верификация прошла успешно!')
        return Response(tg_data.data, status=HTTP_200_OK)




