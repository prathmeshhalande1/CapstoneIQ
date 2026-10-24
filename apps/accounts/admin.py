from django.contrib import admin
from .models import projectGroup , userProfile, Project
# Register your models here.

admin.site.register(projectGroup)
admin.site.register(userProfile)
admin.site.register(Project)