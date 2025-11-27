from django.contrib import admin
from .models import User, Conversation, Message
# Register your models here.

admin.site.register(Conversation)
admin.site.register(Message)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['username', 'email', 'user_id']
    readonly_fields = ['user_id', 'created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user_id','first_name', 'last_name', 'username', 'email', 'password')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )