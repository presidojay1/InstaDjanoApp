from django.urls import path
from .views import user_register, user_logout, MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
 
    path('register/', user_register, name='register'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', user_logout, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/<str:identifier>/', get_profile, name='get_profile_by_identifier'),
    path('profile/create/', create_profile, name='create_profile'),
    path('profile/update/<str:identifier>/', update_profile, name='update_profile'),
  path('profile/delete/<str:identifier>/', delete_profile, name='delete_profile_by_identifier'),
   path('subscribe/', subscribe_to_plan, name='subscribe_to_plan'),
    path('payment_history/<str:identifier>/', payments_history, name='payment_history_by_identifier'),
    path('add_instagram/', add_instagram_account, name='add_instagram_account'),
    path('payment_history/<str:reference>/', payment_history_by_reference, name='payment_history_by_reference'),
    path('manage-instagram-accounts/', manage_instagram_accounts, name='manage_instagram_accounts'),
      path('centrish-listings/', get_centrish_listings),
        path('get-main-listing/', get_main_listing, name='get_main_listing'),
]