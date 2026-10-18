from django.urls import path
from . import views
urlpatterns = [
    path('signup/', views.signupView, name='signup'),
    path('login/', views.loginView, name='login'),
    path('chat/', views.chatView, name='chat'),                  # Group Chat
    path('profile/', views.profileView, name='profile'),
    path('createGroup/', views.homeView, name='createGroup'),
    path('',views.homeView,name='home'),
]
