from rest_framework import serializers
from core.serializers import UserSerializer
from goals.models import GoalCategory, Goal, GoalComment


# Сериализаторы категорий
class CreateGoalCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')


class ListGoalCategorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')


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
    def validate_category(self, value):
        if value.is_deleted:
            raise serializers.ValidationError('Запрещено добавлять удаленную категорию')
        if value.user != self.context['request'].user:
            raise serializers.ValidationError('Запрещено работать не владельцам категории')
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

