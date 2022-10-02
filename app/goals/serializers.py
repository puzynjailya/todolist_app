from rest_framework import serializers
from core.serializers import UserSerializer
from goals.models import GoalCategory

# Сериализаторы категорий
class CreateGoalCategorySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created_date', 'last_update_date', 'user', 'is_deleted')


class ListGoalCategorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created_date', 'last_update_date', 'user', 'is_deleted')

# Сериализаторы Целей
class GoalSerializer(serializers.ModelSerializer):
    category = serializers.RelatedField()