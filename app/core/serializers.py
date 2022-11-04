from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True,
                                     write_only=True,
                                     style={'input_type': 'password', 'placeholder': 'Password'},
                                     validators=[validate_password])
    password_repeat = serializers.CharField(required=True,
                                            write_only=True,
                                            style={'input_type': 'password', 'placeholder': 'Confirm Password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_repeat']

    def validate(self, data):
        if not data.get('password') or not data.get('password_repeat'):
            raise serializers.ValidationError("Пожалуйста введите пароль в оба поля.")
        elif data.get('password') != data.get('password_repeat'):
            raise ValidationError('Введенные пароли не совпадают! Пожалуйста, попробуйте еще раз.')
        return data

    def create(self, validated_data):
        validated_data['password'] = make_password(password=validated_data['password'])
        del validated_data['password_repeat']
        return super().create(validated_data)


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True,
                                     write_only=True,
                                     style={'input_type': 'password', 'placeholder': 'Password'})

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data) -> User:
        username = validated_data.get('username')
        password = validated_data.get('password')
        if not (username and password):
            msg = 'Введите имя пользователя и пароль'
            raise AuthenticationFailed(msg, code='authorization')
        else:
            if not (user := authenticate(username=username, password=password)):
                msg = 'Возможно вы ввели данные неверно. Пожалуйста введите данные еще раз'
                raise AuthenticationFailed(msg, code='authorization')
            return user



class GetAndUpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class UpdatePasswordSerializer(serializers.ModelSerializer):
    #user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    new_password = serializers.CharField(required=True,
                                         write_only=True,
                                         style={'input_type': 'password', 'placeholder': 'New Password'},
                                         validators=[validate_password])
    old_password = serializers.CharField(required=True,
                                         write_only=True,
                                         style={'input_type': 'password', 'placeholder': 'Old Password'})

    class Meta:
        model = User
        fields = ['old_password', 'new_password']

    def validate(self, attrs: dict) -> dict:
        #user = attrs.get('user')
        #if not user:
            #raise NotAuthenticated({"authentication error": "user is not authenticated"})
        if not self.instance.check_password(attrs.get('old_password')):
            raise ValidationError({"old_password": "Неверный пароль"})
        if attrs.get('old_password') == attrs.get('new_password'):
            raise ValidationError({'password match': 'Пароли не могут совпадать'})
        return attrs

    # Комментарий для себя
    # Переопределяем данный метод с ошибкой, т.к. изначально ModelSerializer уже имеет этот метод под капотом
    def create(self, validated_data):
        raise RuntimeError('Создание данных не предусмотрено!')

    def update(self, instance: User, validated_data: dict) -> User:
        instance.password = make_password(validated_data['new_password'])
        instance.save(update_fields=('password',))
        return instance
