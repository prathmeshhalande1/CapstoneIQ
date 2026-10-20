from django.db import models
from django.contrib.auth.models import User
import random
import string
# Create your models here.
class projectGroup(models.Model):
    
    groupCode = models.CharField(max_length=20,unique=True)
    groupName = models.CharField(max_length=200)
    createdBy = models.ForeignKey(User,on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.groupCode:
         self.groupCode = (
            "".join(random.choices(string.ascii_uppercase, k=4))
            + "-"
             + "".join(random.choices(string.digits, k=4))
          )
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.groupName} ({self.groupCode})"

class studentProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    rollNumber = models.CharField(max_length=20)
    githubUrl = models.URLField()
    group = models.ForeignKey(projectGroup,on_delete=models.SET_NULL,null=True,related_name='students')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.roll_number}"

class StudentRepository(models.Model):
  student = models.ForeignKey( User, on_delete=models.CASCADE, related_name="repositories")
  group = models.ForeignKey(projectGroup, on_delete=models.CASCADE, related_name="repositories")
  project_title = models.CharField(max_length=200)
  repository_url = models.URLField()
  commit_count = models.IntegerField(default=0)  # Telemetry tracker
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"{self.student.username} - {self.project_title}"
    
class Project(models.Model):
    student = models.ForeignKey(studentProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    projetUrl = models.URLField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=50, default="Active / On Track")
    build_health = models.CharField(max_length=50, default="Passing (98%)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.student.user.username})"
    
class UserOTP(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  otp = models.CharField(max_length=6)