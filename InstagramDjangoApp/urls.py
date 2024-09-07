# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('profile/create/', views.ProfileCreateAPIView.as_view(), name='profile-create'),
    path('profile/', views.ProfileRetrieveUpdateAPIView.as_view(), name='profile-detail'),
    path('profiles/', views.ProfileListAPIView.as_view(), name='profile-list'),
    path('profiles/<int:user__id>/', views.AdminProfileRetrieveUpdateAPIView.as_view(), name='admin-profile-detail'),
    path('profiles/<int:user__id>/update-subscription/', views.AdminProfileRetrieveUpdateAPIView.as_view(), name='admin-update-subscription'),
    path('bot/run-basic-bot-task/<int:user_id>/', views.InstagramBotTaskView.as_view(), name='run-basic-bot-task'),
    path('bot/run-bot-task/based-on-plan/<int:user_id>/', views.InstagramBotTaskView1.as_view(), name='run-bot-task-userplan'),
    path('bot/run-bot-task/<int:user_id>/', views.InstagramBotTaskView2.as_view(), name='run-bot-task-user-task'),
    path('profiles/referred-users/', views.list_referred_users, name='referred-users'),
]