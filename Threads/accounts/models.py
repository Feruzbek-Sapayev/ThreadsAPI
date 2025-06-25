from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    phone = models.CharField(max_length=13, unique=True)
    fullname = models.CharField(max_length=150)
    bio = models.CharField(max_length=150, null=True, blank=True)
    photo = models.ImageField(verbose_name="profile_picture", upload_to='Images/Profile/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'  # bu ishlatiladi lekin custom backendda override qilinadi
    REQUIRED_FIELDS = ['email', 'phone']

    def __str__(self):
        return self.username