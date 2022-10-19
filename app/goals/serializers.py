from typing import Type

from django.db import transaction
from rest_framework import serializers

from core.models import User
from core.serializers import UserSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


# Сериализаторы категорий
class CreateGoalCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')

    def validate_board(self, value: Board):
        if value.is_deleted:
            raise serializers.ValidationError('Нет прав для удаления категории')
        if not BoardParticipant.objects.filter(
                board=value,
                role__in=[BoardParticipant.Roles.owner,
                          BoardParticipant.Roles.writer],
                user=self.context['request'].user
        ).exists():
            raise serializers.ValidationError('Нет прав Владельца или Редактора')
        return value


class ListGoalCategorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted', 'board')


# Сериализаторы Целей
class CreateGoalSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = serializers.PrimaryKeyRelatedField(queryset=GoalCategory.objects.filter(is_deleted=False))

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    # Комментарий для будущего меня
    # Можно валидировать необходимые поля с помощью validate_{имя поля}
    def validate_category(self, value: GoalCategory):
        if value.is_deleted:
            raise serializers.ValidationError('Запрещено добавлять удаленную категорию')
        if value.user != self.context['request'].user:
            raise serializers.ValidationError('Запрещено работать не владельцам категории')
        if not BoardParticipant.objects.filter(
            board_id=value.board_id,
            role__in=[BoardParticipant.Roles.owner, BoardParticipant.Roles.writer],
            user=self.context['request'].user
        ).exists():
            raise serializers.ValidationError('Отсутствуют требуемые права')

        return value


class ListGoalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=GoalCategory.objects.filter(is_deleted=False))

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')


# Сериализаторы комментариев
class CreateCommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'goal')


# Сериализаторы досок
class BoardCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        read_only_fields = ("id", "created", "updated")
        fields = "__all__"

    def create(self, validated_data):
        user = validated_data.pop("user")
        board = Board.objects.create(**validated_data)
        BoardParticipant.objects.create(user=user, board=board, role=BoardParticipant.Roles.owner)
        return board


class BoardParticipantSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.Roles.choices[1:])
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')


class BoardSerializer(serializers.ModelSerializer):
    participants = BoardParticipantSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated')

    def update(self, instance, validated_data):
        # Достаем пользователя и участников
        user = validated_data.pop('user')
        new_participants = validated_data.pop('participants')
        new_participants_indices = {member['user'].id: member for member in new_participants}
        old_participants = instance.participants.exclude(user=user)

        # Применяем все изменения одной транзакцией:
        with transaction.atomic():
            for participant in old_participants:
                if participant.user_id not in new_participants_indices:
                    participant.delete()
                else:
                    if participant.role != new_participants_indices[participant.user_id]['role']:
                        participant.role = new_participants_indices[participant.user_id]['role']
                        participant.save()
                    new_participants_indices.pop(participant.user_id)
            for new_participant in new_participants_indices.values():
                BoardParticipant.objects.create(board=instance,
                                                user=new_participant['user'],
                                                role=new_participant['role'])
            instance.title = validated_data.get('title', instance.title)
            instance.save()

        return instance


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'
