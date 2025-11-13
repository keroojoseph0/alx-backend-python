import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

USER_ROLES = [
    ('Guest', 'Guest'),
    ('Host', 'Host'),
    ('Admin', 'Admin')
]

class User(AbstractUser):
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
        )
    first_name = models.CharField(max_length=100, null = False)
    last_name = models.CharField(max_length=100, null = False)
    email = models.EmailField(unique=True, null = False)
    password_hash = models.CharField(max_length=255, null = False)
    phone_number = models.CharField(max_length=20, null= True, blank=True)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='Guest', null = False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'password_hash']
    
    class Meta:
        indexes = [
            models.Index(fields=['email'], name = 'idx_email_user')
        ]
        
    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
class Conversation(models.Model):
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    participants_id = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    
class Message(models.Model):
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    sender_id = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField(null = False)
    sent_at = models.DateTimeField(auto_now_add=True)