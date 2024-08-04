from django.urls import path
from .views import getRoutes, user_register, user_logout, MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import create_profile, update_profile, get_profile, delete_profile

urlpatterns = [
    path('', getRoutes, name='api_root'),
    path('register/', user_register, name='register'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', user_logout, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/<str:identifier>/', get_profile, name='get_profile_by_identifier'),
    path('profile/create/', create_profile, name='create_profile'),
    path('profile/update/<str:identifier>/', update_profile, name='update_profile'),
  path('profile/delete/<str:identifier>/', delete_profile, name='delete_profile_by_identifier'),
]
