from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class projectGroup(models.Model):
    
    groupCode = models.CharField(max_length=20,unique=True)
    groupName = models.CharField(max_length=200)
    createdBy = models.ForeignKey(User,on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.groupName} ({self.groupCode})"

class studentProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    rollNumber = models.CharField(max_length=20)
    githubUrl = models.URLField()
    group = models.ForeignKey(projectGroup,on_delete=models.SET_NULL,null=True,related_name='students')

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.roll_number}"
    
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