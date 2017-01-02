from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['username']


admin.site.register(UserProfile, UserProfileAdmin)
