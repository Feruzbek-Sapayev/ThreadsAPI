from django.urls import path, re_path
from accounts.views import RegisterView, LoginView, LogoutView, ProfileView

urlpatterns = [
    re_path(r'^register/?$', RegisterView.as_view(), name='register'),
    re_path(r'^login/?$', LoginView.as_view(), name='login'),
    re_path(r'^logout/?$', LogoutView.as_view(), name='logout'),
    re_path(r'^(?P<username>[\w-]+)/?$', ProfileView.as_view(), name='profile'),

]
