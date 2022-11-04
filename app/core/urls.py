from django.urls import path

from core import views

#app_name = 'core'
urlpatterns  = [
    path('signup', views.UserRegistrationView.as_view(), name='signup'),
    path('login', views.UserLoginView.as_view(), name='login'),
    path('profile', views.GetAndUpdateUserView.as_view(), name='profile'),
    path('update_password', views.UpdateUserPasswordView.as_view(), name='update-password')
]
