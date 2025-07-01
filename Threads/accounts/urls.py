from django.urls import path, re_path
from accounts.views import RegisterView, AuthCheckView, LoginView, LogoutView, ProfileView, check_username, check_email, check_phone

urlpatterns = [
    re_path(r'^register/?$', RegisterView.as_view(), name='register'),
    re_path(r'^login/?$', LoginView.as_view(), name='login'),
    re_path(r'^logout/?$', LogoutView.as_view(), name='logout'),
    re_path(r'^(?P<username>[\w-]+)/?$', ProfileView.as_view(), name='profile'),
    re_path(r'^check/username/?$', check_username, name='check-username'),
    re_path(r'^check/phone/?$', check_phone, name='check-phone'),
    re_path(r'^check/email/?$', check_email, name='check-email'),
    re_path(r'^auth/check/?$', AuthCheckView.as_view(), name='auth-check'),
]
