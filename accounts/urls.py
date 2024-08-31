from django.urls import path 
from . import views 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



urlpatterns = [
    
    path('register/', views.UserRegisteration.as_view(),name='register'),
    # path('register?ref=<str:referrer_id>', views.UserRegisteration.as_view(),name='register'),
    path('user/update/', views.UserUpdateView.as_view(), name='user-update'),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('login',views.LoginView.as_view(), name='login' ),
    path('change-password',views.ChangePasswordView.as_view(), name='change-password' ),
    path('verify/<str:uid>/<str:token>/', views.verify_email, name='verify_email'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('logged-in-user/', views.CurrentUserView.as_view(), name='current-user'),
    path('api/get-referral-link/', views.get_referral_link, name='get-referral-link'),
    
]
