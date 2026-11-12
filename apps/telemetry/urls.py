from django.urls import path
from . import views
urlpatterns = [
    path('get-user-group-repositories/', views.get_user_group_repositories, name='get_user_group_repositories'),
]