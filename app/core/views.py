from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.models import User
from core.serializers import UserRegistrationSerializer, UserLoginSerializer, GetAndUpdateUserSerializer, \
    UpdatePasswordSerializer


@extend_schema(description='Страница регистрации',
               summary='Сервис регистрации нового пользователя')
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


@extend_schema(description='Страница логина',
               summary='Сервис входа пользователя')
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login(request=request, user=serializer.save())
        return Response(serializer.data)


@extend_schema_view(description='Страница обновления данных о пользователе',
                    summary='Сервис обновления данных о пользователе')
@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetAndUpdateUserView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GetAndUpdateUserSerializer

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(description='Страница Обновления пароля пользователя')
@method_decorator(ensure_csrf_cookie, name='dispatch')
class UpdateUserPasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdatePasswordSerializer

    def get_object(self):
        return self.request.user



