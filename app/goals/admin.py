from django.contrib.auth.admin import *
from goals.models import GoalCategory, Goal, GoalComment, Board


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created', 'updated')
    search_fields = ('title', 'user')
    list_filter = ('is_deleted',)
    readonly_fields = ('created', 'updated')


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = (
                    'title', 'description', 'category', 'status', 'priority', 'due_date',
                    'user', 'created', 'updated')
    search_fields = ('title', 'description')
    list_filter = ('status', 'priority')
    readonly_fields = ('created', 'updated')


@admin.register(GoalComment)
class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ('goal','user', 'text')
    search_fields = ('text',)
    readonly_fields = ('created', 'updated')

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
    search_fields = ('title',)


