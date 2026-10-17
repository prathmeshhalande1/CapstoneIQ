from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
import uuid

#mycreated
from .models import projectGroup , studentProfile
from .services.qrGenerator import generate_group_qr

# Create your views here.
def signupView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken!")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)  # Auto-login after signup
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'accounts/signup.html')

def loginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('login')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'accounts/login.html')
def doneView(req):
    return render('account/test.html')

