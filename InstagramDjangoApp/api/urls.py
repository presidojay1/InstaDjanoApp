from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

urlpatterns = [
 
    # path('register/', user_register, name='register'),
    # path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('logout/', user_logout, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  #   path('profile/<str:identifier>/', get_profile, name='get_profile_by_identifier'),
  #   path('profile/create/', create_profile, name='create_profile'),
  #   path('profile/update/<str:identifier>/', update_profile, name='update_profile'),
  # path('profile/delete/<str:identifier>/', delete_profile, name='delete_profile_by_identifier'),
   path('subscribe/', subscribe_to_plan, name='subscribe_to_plan'),
   path('subscribeTest/', subscribe_to_plan_Test, name='subscribe_to_plan_Test'),
    path('payment_history/<str:identifier>/', payments_history, name='payment_history_by_identifier'),
    path('instagram-accounts/', InstagramAccountListView.as_view(), name='instagram-account-list'),
    path('instagram-accounts/create/', InstagramAccountCreateView.as_view(), name='instagram-account-create'),
    path('instagram-accounts/<int:pk>/', InstagramAccountDetailView.as_view(), name='instagram-account-detail'),
    path('instagram-accounts/<int:pk>/delete/', InstagramAccountDeleteView.as_view(), name='instagram-account-delete'),
    path('payment_history/by_ref/<str:reference>/', payment_history_by_reference, name='payment_history_by_reference'),
    path('manage-instagram-accounts/', manage_instagram_accounts, name='manage_instagram_accounts'),
]
