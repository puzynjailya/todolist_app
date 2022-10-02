from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import permissions, generics
from rest_framework.pagination import LimitOffsetPagination

from goals.models import GoalCategory
from goals.serializers import CreateGoalCategorySerializer, ListGoalCategorySerializer


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CreateGoalCategoryView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = GoalCategory
    serializer_class = CreateGoalCategorySerializer


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ListGoalCategoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = GoalCategory
    serializer_class = ListGoalCategorySerializer
    pagination_class = LimitOffsetPagination
    ordering_fields = ['title', 'created_date']
    ordering = 'title'
    search_field = ['title']

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user,
                                           is_deleted=False)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class RUDGoalCategoryView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = GoalCategory
    serializer_class = ListGoalCategorySerializer

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user,
                                           is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        return instance



