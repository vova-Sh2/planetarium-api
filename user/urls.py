from django.contrib.auth.views import LogoutView
from django.urls import path

from user.views import UserCreateView, UserLoginView, ManageUserView

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("me/", ManageUserView.as_view(), name="manage"),
]

app_name = "user"