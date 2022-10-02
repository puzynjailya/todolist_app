from django.contrib.auth.admin import *
from goals.models import GoalCategory


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_date', 'last_update_date')
    search_fields = ('title', 'user')

