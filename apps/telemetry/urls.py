from django.urls import path
from . import views
urlpatterns = [
    path('get-user-group-repositories/',views.get_user_group_repositories,name='sync_github_commits'),
    path('get-group-commits/',views.get_group_commits,name='get_group_commits'),
]