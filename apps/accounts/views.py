from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
import random,datetime
import uuid

# mycreated models & services
from .models import projectGroup, userProfile,Project, UserOTP ,GroupMembership

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

        otpCode = str(random.randint(100000, 999999))
        
        request.session['signup_data'] = {
            'username': username,
            'email': email,
            'password': password,
            'otp': otpCode
        }

        sender_email = getattr(settings, 'EMAIL_HOST_USER', 'from@capstoneiq.com')
        send_mail(
            'Your CapstoneIQ OTP Verification Code',
            f'Your verification code is: {otpCode}',
            sender_email,
            [email],
            fail_silently=False,
        )
        messages.success(request, 'OTP sent to your email address.')
        return redirect('otpVerify')

    return render(request, 'accounts/signup.html')


def verifyOTPView(request):
    signupData = request.session.get('signup_data')
    if not signupData:
        messages.error(request, 'Session expired. Please sign up again.')
        return redirect('signup')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == signupData['otp']:
            user = User.objects.create_user(
                username=signupData['username'], 
                email=signupData['email'], 
                password=signupData['password']
            )
            request.session.pop('signup_data', None)
            login(request, user)
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

@login_required
def homeView(request):
    profile, _ = userProfile.objects.get_or_create(user=request.user)
    user_groups = projectGroup.objects.filter(
        Q(createdBy=request.user) | Q(group_members__User=profile)
    ).select_related('createdBy').prefetch_related(
        'group_members__User__user'
    ).distinct()
    for group in user_groups:
        participants = [group.createdBy]
        participants.extend(
            membership.User.user
            for membership in group.group_members.all()
            if membership.User.user_id != group.createdBy_id
        )
        group.chat_participants = participants
        group.participant_count = len(participants)

    user_projects = profile.projects.all()

    context = {
        'user_groups': user_groups,
        'user_profile': profile,
        'user_projects': user_projects,
    }
    return render(request, 'accounts/index.html', context)

@login_required
def create_group_view(request):
  if request.method == 'POST':
    group_name = request.POST.get('group_name')
    if group_name:
        group = projectGroup.objects.create(groupName=group_name, createdBy=request.user)
        profile, _ = userProfile.objects.get_or_create(user=request.user)
        GroupMembership.objects.get_or_create(student=profile, group=group)
  return redirect('home')

@login_required
def join_group_view(request):
  if request.method == 'POST':
    invite_code = request.POST.get('invite_code', '').strip().upper()
    if invite_code:
      group = get_object_or_404(projectGroup, groupCode=invite_code)
      profile, _ = userProfile.objects.get_or_create(user=request.user)
      GroupMembership.objects.get_or_create(student=profile, group=group)
  return redirect('home')

@login_required
def save_repository_view(request):
  if request.method == 'POST':
    group_name = request.POST.get('group_name')
    project_title = request.POST.get('project_title')
    repository_url = request.POST.get('repository_url')
    group = get_object_or_404(projectGroup, groupName=group_name)
    profile, _ = userProfile.objects.get_or_create(user=request.user)
    GroupMembership.objects.get_or_create(user_profile=profile, group=group)
    Project.objects.create(
            user_profile=profile,
            group=group,
            title=project_title,
            projetUrl=repository_url
        )
  return redirect('home')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)
            request.session['reset_otp'] = str(otp)
            request.session['reset_email'] = email
            send_mail(
                subject='Your CapstoneIQ Password Reset OTP',
                message=f'Your OTP code is {otp}. It is valid for 10 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            messages.success(request, 'OTP has been sent to your email.')
            return redirect('verifyAccountOtp')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            
    return render(request, 'accounts/forgetPassword.html')


def verify_otp_view(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        session_otp = request.session.get('reset_otp')
        email = request.session.get('reset_email')

        if not session_otp or not email:
            messages.error(request, 'Session expired. Please request OTP again.')
            return redirect('forgotPassword')

        if otp_input != session_otp:
            messages.error(request, 'Invalid OTP code.')
            return render(request, 'accounts/verifyAccountOtp.htmll')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/verifyAccountOtp.html')

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        del request.session['reset_otp']
        del request.session['reset_email']

        messages.success(request, 'Password reset successful! Please log in.')
        return redirect('login')

    return render(request, 'accounts/verifyAccountOtp.html')
def createProfileview(req):
    if req.method == 'POST':
        avatarInput = req.FILES.get('avatar')


        rollNumberInput = req.POST.get('rollNumber')
        phoneNumberInput = req.POST.get('phoneNumber')
        liveInput = req.POST.get('live')
        birthDayInput = req.POST.get('birthDay')
        fname = req.POST.get('firstName')
        lname = req.POST.get('lastName')

        profile, _ = userProfile.objects.get_or_create(user=req.user)

        if avatarInput:
            profile.avatar = avatarInput

        if birthDayInput:
            profile.birthDay = birthDayInput

        profile.rollNumber = rollNumberInput
        profile.phoneNumber = phoneNumberInput
        profile.live = liveInput
        profile.isProfileCreated =True
        req.user.first_name = fname
        req.user.last_name = lname

        req.user.save()
        profile.save()
        return redirect('home')
    return redirect('home')
def createProjectView(req):
    if req.method == 'POST':
        profile = userProfile.objects.get(user=req.user)

        titleInput=req.POST.get('title')
        projetUrlInput=req.POST.get('projetUrl')
        descriptionInput=req.POST.get('description')
        statusInput=req.POST.get('status')
        buildHealthInput = req.POST.get('build_health')

        isPrivateInput = req.POST.get('isPrivate') == 'True'
        
        Project.objects.create(
            user=profile,
            title=titleInput,
            projetUrl=projetUrlInput,
            description=descriptionInput,
            status=statusInput,
            build_health=buildHealthInput,
            isPrivate=isPrivateInput
        )
    return redirect("home")

@login_required
def deleteProject(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id, user__user=request.user)
        project.delete()
        
    return redirect("home")

@login_required
def editProject(request, project_id):
    project = get_object_or_404(Project, id=project_id, user__user=request.user)
    
    if request.method == 'POST':
        project.title = request.POST.get('title')
        project.projetUrl = request.POST.get('projetUrl')
        project.description = request.POST.get('description')
        project.status = request.POST.get('status')
        project.build_health = request.POST.get('build_health')
        project.isPrivate = request.POST.get('isPrivate') == 'True'
        project.save()
        return redirect("home") 
    return render(request, "accounts/editProject.html", {"project": project})

def CreateProjectView(req):
    return render(req, 'accounts/createProject.html')

