from django.urls import path

from goals import views

urlpatterns = [
    path('goal_category/create', views.CreateGoalCategoryView.as_view(), name='create category'),
    path('goal_category/list', views.ListGoalCategoryView.as_view(), name='list category'),
    path('goal_category/<pk>', views.RUDGoalCategoryView.as_view(), name='retrieve/update/delete category'),
]