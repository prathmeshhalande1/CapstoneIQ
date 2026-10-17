from django.urls import path
from . import views
urlpatterns = [
    path('signup/', views.signupView, name='signup'),
    path('login/', views.loginView, name='login'),
    path('done/', views.doneView, name='done')
]
