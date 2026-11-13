from django.db import models
from apps.accounts.models import userProfile
# Create your models here.

class commitLog(models.Model):
    user = models.ForeignKey(userProfile,on_delete=models.CASCADE,related_name="commit")
    commitSha = models.CharField(max_length=40,unique=True)

    repository = models.CharField(max_length=255,null=True,blank=True)
    commitdata = models.DateField()
    autherName =models.CharField(max_length=100)
    authorEmail = models.EmailField(null=True, blank=True)
    
    message = models.TextField()
    addline =models.IntegerField(default=0)
    deletline = models.IntegerField(default=0)
    totalChanges = models.IntegerField(default=0)
    html_url = models.URLField(max_length=500, null=True, blank=True)

    syncedAt = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "repository", "commitSha"],
                name="unique_student_repo_commit"
            )
        ]

    def __str__(self):
        return f"{self.commitSha[:7]} (+{self.addline}/-{self.deletline})"