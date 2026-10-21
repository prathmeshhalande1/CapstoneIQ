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
from .models import projectGroup, studentProfile,Project, UserOTP
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

def homeview(request):
  all_groups = projectGroup.objects.all()
  profile, created = studentProfile.objects.get_or_create(
      user=request.user, defaults={'rollNumber': 'PENDING'}
  )
  user_projects = profile.projects.all()
  context = {
      'user_groups': all_groups,
      'user_profile': profile,
      'user_projects': user_projects,
  }
  return render(request, 'accounts/index.html', context)

def create_group_view(request):
  if request.method == 'POST':
    group_name = request.POST.get('group_name')
    if group_name:
      projectGroup.objects.create(groupName=group_name, category_badge='Custom Squad',createdBy=request.user)
  return redirect('home')

def join_group_view(request):
  if request.method == 'POST':
    invite_code = request.POST.get('invite_code').strip().upper()
    group = get_object_or_404(projectGroup, groupCode=invite_code)
    group.members.add(request.user)
  return redirect('home')

def save_repository_view(request):
  if request.method == 'POST':
    group_name = request.POST.get('group_name')
    project_title = request.POST.get('project_title')
    repository_url = request.POST.get('repository_url')
    group = get_object_or_404(projectGroup, groupName=group_name)
    profile, _ = studentProfile.objects.get_or_create(
        user=request.user, defaults={'group': group}
    )
    profile.group = group
    profile.githubUrl = repository_url
    profile.save()
    Project.objects.update_or_create(
        student=profile,
        defaults={'title': project_title, 'projetUrl': repository_url},
    )
  return redirect('home')

def CreateProjectView(req):
    return render(req, 'accounts/createProject.html')
def addProjectView(req):
    return render(req, 'accounts/selfProjectinit.html')
def homeView(req):
    return render(req, 'accounts/index.html')
def chatView(req):
    return render(req, 'accounts/index.html')
def profileView(req):
    return render(req, 'accounts/index.html')