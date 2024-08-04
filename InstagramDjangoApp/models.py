from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from django.contrib.auth import get_user_model

UserModel = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True)
    has_confirmed_otp = models.BooleanField(default=False)
    number_of_ig_accounts = models.PositiveIntegerField(default=0)
    height = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'