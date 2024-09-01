from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import CustomUserManager
from django.utils import timezone 
import uuid
from django.urls import reverse
# Create your models here.


class CustomUser(AbstractBaseUser,PermissionsMixin):

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100,null=True) 
    phone_no = models.CharField(max_length=100,null=True,blank=True)
    referrer_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateField(default=timezone.now)
    is_verified = models.BooleanField(default=False)         
  
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def referral_link(self):
        """
        Returns the referral link for the user.
        """
        return reverse('register') + f'?ref={self.referrer_id}'


    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.date_joined = timezone.now().date()
        super().save(*args, **kwargs)