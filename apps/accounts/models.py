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
