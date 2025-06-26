from django.db import models
import shortuuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager



def generate_shortuuid():
    return shortuuid.uuid()[:11]

def random_file_path(instance, filename):
    ext = filename.split('.')[-1]
    random_name = generate_shortuuid()
    username = instance.username
    return f'uploads/users/{username}/avatar/{random_name}.{ext}'


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    phone = models.CharField(max_length=13, unique=True)
    fullname = models.CharField(max_length=150)
    bio = models.CharField(max_length=150, null=True, blank=True)
    photo = models.ImageField(verbose_name="profile_picture", upload_to=random_file_path, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'  # bu ishlatiladi lekin custom backendda override qilinadi
    REQUIRED_FIELDS = ['email', 'phone']

    def __str__(self):
        return self.username