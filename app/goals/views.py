from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, generics, filters
from rest_framework.pagination import LimitOffsetPagination
from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment
from goals.permissions import IsAnAuthor
from goals.serializers import CreateGoalCategorySerializer, ListGoalCategorySerializer, CreateGoalSerializer, \
    ListGoalSerializer, CreateCommentSerializer, CommentSerializer


class CreateGoalCategoryView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = GoalCategory
    serializer_class = CreateGoalCategorySerializer


class ListGoalCategoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = GoalCategory
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    serializer_class = ListGoalCategorySerializer
    pagination_class = LimitOffsetPagination
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user,
                                           is_deleted=False)


class RUDGoalCategoryView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = GoalCategory
    serializer_class = ListGoalCategorySerializer

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user,
                                           is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields='is_deleted',)
        return instance


class CreateGoalView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Goal
    serializer_class = CreateGoalSerializer


class ListGoalView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Goal
    serializer_class = ListGoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ['priority', 'due_date']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return Goal.objects.filter(user_id=self.request.user.id).filter(~Q(status=Goal.Status.archived))


class RUDGoalView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAnAuthor]
    model = Goal
    serializer_class = ListGoalSerializer

    def get_queryset(self):
        return Goal.objects.filter(user_id=self.request.user.id).filter(~Q(status=Goal.Status.archived))

    def perform_destroy(self, instance):
        instance.status = Goal.Status.archived
        instance.save(update_fields=('status',))
        return instance


class CreateGoalCommentView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = GoalComment
    serializer_class = CreateCommentSerializer


class ListGoalCommentView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = GoalComment
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal', 'created']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComment.objects.filter(user_id=self.request.user.id)


class RUDGoalCommentView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAnAuthor]
    model = GoalComment
    serializer_class = CommentSerializer

    def get_queryset(self):
        return GoalComment.objects.filter(user_id=self.request.user.id)




