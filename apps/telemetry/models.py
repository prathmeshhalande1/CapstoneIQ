from django.db import models
from apps.accounts.models import userProfile
# Create your models here.

class commitLog(models.Model):
    student = models.ForeignKey(userProfile,on_delete=models.CASCADE,related_name="commit")
    commitSha = models.CharField(max_length=40,unique=True)
    commitdata = models.DateField()
    autherName =models.CharField(max_length=100)
    message = models.TextField()
    addline =models.IntegerField(default=0)
    deletline = models.IntegerField(default=0)
    syncedAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commit_sha[:7]} (+{self.additions}/-{self.deletions})"