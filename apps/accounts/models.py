from django.db import models
from django.contrib.auth.models import User
import random
import string

class projectGroup(models.Model):
    
    groupCode = models.CharField(max_length=20,unique=True)
    groupName = models.CharField(max_length=200)
    createdBy = models.ForeignKey(User,on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)

    category_badge = models.CharField(
      max_length=50, default="Academic Batch"
  )
    members = models.ManyToManyField(
      User, related_name="project_groups", blank=True
  )
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

class userProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    rollNumber = models.CharField(max_length=20,blank=True,null=True)
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.rollNumber}"
    
class GroupMembership(models.Model):
  student = models.ForeignKey(
      userProfile, on_delete=models.CASCADE, related_name='memberships'
  )
  group = models.ForeignKey(
      projectGroup, on_delete=models.CASCADE, related_name='group_members'
  )
  joined_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    unique_together = ('student', 'group')

  def __str__(self):
    return f"{self.student.user.username} in {self.group.groupName}"
  
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
    student = models.ForeignKey(userProfile, on_delete=models.CASCADE, related_name='projects')
    group = models.ForeignKey(
      projectGroup,
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      related_name='group_projects',
  )
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