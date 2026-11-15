from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=('id','nickname','user','role')
    search_fields=('nickname','user__username')
    list_filter=('role',)
