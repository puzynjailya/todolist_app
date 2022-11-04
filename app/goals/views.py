from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, generics, filters
from rest_framework.pagination import LimitOffsetPagination
from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment, Board
from goals.permissions import IsAnAuthor, BoardPermission, GoalCategoryPermission, GoalPermission, CommentPermission
from goals.serializers import CreateGoalCategorySerializer, ListGoalCategorySerializer, CreateGoalSerializer, \
    ListGoalSerializer, CreateCommentSerializer, CommentSerializer, BoardSerializer, BoardListSerializer, \
    BoardCreateSerializer


# Вьюшки досок
class BoardCreateView(generics.CreateAPIView):
    model = Board
    serializer_class = BoardCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class BoardListView(generics.ListAPIView):
    model = Board
    serializer_class = BoardListSerializer
    permission_classes = [permissions.IsAuthenticated, BoardPermission]
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering = ['title']

    def get_queryset(self):
        return Board.objects.prefetch_related('participants').filter(
            participants__user_id=self.request.user.id,
            is_deleted=False)


class BoardView(generics.RetrieveUpdateDestroyAPIView):
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermission]
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.prefetch_related('participants').filter(
            participants__user=self.request.user.id,
            is_deleted=False)

    def perform_destroy(self, instance):
        # При удалении доски ставим отметку is_deleted = True, обновляем статусы целей и удаляем категории
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)
        return instance


# Вьюшки категорий
class CreateGoalCategoryView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = GoalCategory
    serializer_class = CreateGoalCategorySerializer


class ListGoalCategoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermission]
    model = GoalCategory
    serializer_class = ListGoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['board']
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related('board__participants').filter(
                                is_deleted=False,
                                board__participants__user_id=self.request.user.id)


class RUDGoalCategoryView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = GoalCategory
    serializer_class = ListGoalCategorySerializer

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related('board__participants').filter(
                                is_deleted=False,
                                board__participants__user_id=self.request.user.id)

    def perform_destroy(self, instance: GoalCategory):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            Goal.objects.filter(category=instance).update(status=Goal.Status.archived)
        return instance


# Вьюшки целей
class CreateGoalView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, GoalPermission]
    model = Goal
    serializer_class = CreateGoalSerializer


class ListGoalView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, GoalPermission]
    model = Goal
    serializer_class = ListGoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalDateFilter
    ordering_fields = ['priority', 'due_date']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return Goal.objects.select_related('user', 'category__board').filter(Q(
            category__board__participants__user_id=self.request.user.id)).filter(~Q(status=Goal.Status.archived))


class RUDGoalView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAnAuthor, GoalPermission]
    model = Goal
    serializer_class = ListGoalSerializer

    def get_queryset(self):
        return Goal.objects.select_related('user', 'category__board').filter(Q(
            category__board__participants__user_id=self.request.user.id)).filter(~Q(status=Goal.Status.archived))

    def perform_destroy(self, instance):
        instance.status = Goal.Status.archived
        instance.save(update_fields=('status',))
        return instance


class CreateGoalCommentView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, CommentPermission]
    model = GoalComment
    serializer_class = CreateCommentSerializer


class ListGoalCommentView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, CommentPermission]
    model = GoalComment
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal', 'created']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComment.objects.select_related('goal__category__board', 'user').filter(
            goal__category__board__participants__user_id=self.request.user.id
        )


class RUDGoalCommentView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAnAuthor, CommentPermission]
    model = GoalComment
    serializer_class = CommentSerializer

    def get_queryset(self):
        return GoalComment.objects.select_related('goal__category__board', 'user').filter(
            goal__category__board__participants__user_id=self.request.user.id
        )







