from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import random
import uuid

# mycreated models & services
from .models import projectGroup, studentProfile, UserOTP
from .services.qrGenerator import generate_group_qr

def signupView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken!')
            return redirect('signup')

        # Create user as inactive until OTP is verified
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        user.is_active = False
        user.save()

        # Generate and save 6-digit OTP
        otpCode = str(random.randint(100000, 999999))
        UserOTP.objects.create(user=user, otp=otpCode)

        sender_email = getattr(settings, 'EMAIL_HOST_USER', 'from@capstoneiq.com')
        send_mail(
            'Your CapstoneIQ OTP Verification Code',
            f'Your verification code is: {otpCode}',
            sender_email,
            [email],
            fail_silently=False,
        )

        request.session['verifyUserId'] = user.id
        messages.success(request, 'OTP sent to your email address.')
        return redirect('otpVerify')

    return render(request, 'accounts/signup.html')


def verifyOTPView(request):
    userId = request.session.get('verifyUserId')
    if not userId:
        messages.error(request, 'Session expired. Please sign up again.')
        return redirect('signup')

    user = get_object_or_404(User, id=userId)
    userOtp = get_object_or_404(UserOTP, user=user)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == userOtp.otp:
            user.is_active = True
            user.save()
            userOtp.delete()
            login(request, user)
            del request.session['verifyUserId']
            messages.success(request, 'Account verified successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'accounts/otpverify.html')


def loginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'accounts/login.html')

def logoutView(req):
    logout(req)
    return render(req, 'accounts/index.html')
def doneView(req):
    return render(req, 'accounts/test.html')
def homeView(req):
    return render(req, 'accounts/index.html')
def chatView(req):
    return render(req, 'accounts/index.html')
def profileView(req):
    return render(req, 'accounts/index.html')