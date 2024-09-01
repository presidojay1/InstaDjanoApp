from django.contrib import admin
from .models import Profile, InstagramAccount, PaymentHistory
# Register your models here.
admin.site.register(Profile)
admin.site.register(InstagramAccount)
admin.site.register(PaymentHistory)