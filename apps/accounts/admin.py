from django.contrib import admin
from .models import projectGroup , studentProfile, Project, StudentRepository
# Register your models here.

admin.site.register(projectGroup)
admin.site.register(studentProfile)
admin.site.register(Project)
admin.site.register(StudentRepository)