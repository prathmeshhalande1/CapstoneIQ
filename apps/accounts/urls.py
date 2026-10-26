from django.urls import path
from . import views
urlpatterns = [
    path('signup/', views.signupView, name='signup'),
    path('verifyOtp/', views.verifyOTPView, name='otpVerify'),
    path('login/', views.loginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('group/create/', views.create_group_view, name='create_group'),
    path('group/join/', views.join_group_view, name='join_group'),
    path('repository/save/', views.save_repository_view, name='save_repository'),
    path('',views.homeView,name='home'),
    path('forgot-password/', views.forgot_password_view, name='forgotPassword'),
    path('verify-otp/', views.verify_otp_view, name='verifyAccountOtp'),
    path('createProfile/', views.createProfileview, name='createProfile'),
    path('createProject/', views.createProjectView, name='createProject'), 
]
