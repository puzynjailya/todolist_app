from django.urls import path

from goals import views

urlpatterns = [
    path('goal_category/create', views.CreateGoalCategoryView.as_view(), name='create category'),
    path('goal_category/list', views.ListGoalCategoryView.as_view(), name='list category'),
    path('goal_category/<pk>', views.RUDGoalCategoryView.as_view(), name='retrieve/update/delete category'),
    path('goal/create', views.CreateGoalView.as_view(), name='create goal'),
    path('goal/list', views.ListGoalView.as_view(), name='list goal'),
    path('goal/<pk>', views.RUDGoalView.as_view(), name='retrieve/update/delete goal'),
    path('goal_comment/create', views.CreateGoalCommentView.as_view(), name='create comment'),
    path('goal_comment/list', views.ListGoalCommentView.as_view(), name='list comment'),
    path('goal_comment/<pk>', views.RUDGoalCommentView.as_view(), name='retrieve/update/delete comment'),
]
