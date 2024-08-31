# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('profile/create/', views.ProfileCreateAPIView.as_view(), name='profile-create'),
    path('profile/', views.ProfileRetrieveUpdateAPIView.as_view(), name='profile-detail'),
    path('profiles/', views.ProfileListAPIView.as_view(), name='profile-list'),
    path('profiles/<int:user__id>/', views.AdminProfileRetrieveUpdateAPIView.as_view(), name='admin-profile-detail'),
    path('profiles/<int:user__id>/update-subscription/', views.AdminProfileRetrieveUpdateAPIView.as_view(), name='admin-update-subscription'),

    path('bot/run-bot-task/<int:profile_id>/', views.InstagramBotTaskView.as_view(), name='run-bot-task'),
    path('profiles/referred-users/', views.list_referred_users, name='referred-users'),
]