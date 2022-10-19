from rest_framework.permissions import BasePermission, SAFE_METHODS

from goals.models import BoardParticipant, GoalCategory, Board, Goal


class IsAnAuthor(BasePermission):
    message = 'Редактирование доступно только для владельца'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.id == obj.user_id:
            return True
        return False


class BoardPermission(BasePermission):
    message = 'Редактирование доски доступно только участникам доски'

    def has_object_permission(self, request, view, obj: Board):
        if not request.user.is_authenticated:
            return False
        # Если метод безопасный, то возвращаем состояние да\нет существует ли юзер в участниках
        if request.method in SAFE_METHODS:
            return BoardParticipant.objects.filter(user=request.user, board=obj).exists()
        # При попытке удаления\изменения выполняем запрос и проверяем владелец ли это
        return BoardParticipant.objects.filter(user=request.user, board=obj, role=BoardParticipant.Roles.owner).exists()


class GoalCategoryPermission(BasePermission):
    message = 'Редактирование категории доступно только участникам доски'

    def has_object_permission(self, request, view, obj: GoalCategory):
        if not request.user.is_authenticated:
            return False
        # Если метод безопасный, то возращаем состояние да\нет существует ли юзер в участниках
        if request.method in SAFE_METHODS:
            return BoardParticipant.objects.filter(user=request.user, board=obj.board).exists()
        # При попытке удаления\изменения выполняем запрос и проверяем владелец ли это
        return BoardParticipant.objects.filter(
                                                user=request.user,
                                                board=obj.board,
                                                role__in=[BoardParticipant.Roles.owner, BoardParticipant.Roles.writer],
                                               ).exists()


class GoalPermission(BasePermission):
    message = 'Редактирование целей доступно только участникам доски'

    def has_object_permission(self, request, view, obj: Goal):
        if not request.user.is_authenticated:
            return False
        # Если метод безопасный, то возращаем состояние да\нет существует ли юзер в участниках
        if request.method in SAFE_METHODS:
            return BoardParticipant.objects.filter(user=request.user, board=obj.category.board).exists()
        return BoardParticipant.objects.filter(
                                                user=request.user,
                                                board=obj.category.board,
                                                role__in=[BoardParticipant.Roles.owner, BoardParticipant.Roles.writer]
                                            ).exists()


class CommentPermission(BasePermission):
    message = 'Редактирование комментариев доступно только владельцам'

    def has_object_permission(self, request, view, obj: Goal):
        if not request.user.is_authenticated:
            return False
        # Если метод безопасный, то возращаем состояние да\нет существует ли юзер в участниках
        return any((request.method in SAFE_METHODS, obj.user_id == request.user.id,))
