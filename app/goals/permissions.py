from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAnAuthor(BasePermission):
    message = 'Редактирование доступно только для владельца'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.id == obj.user_id:
            return True
        return False
