from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone', 'created_at']
    search_fields = ['username', 'email', 'phone']
    list_filter = ['created_at']
