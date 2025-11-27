import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager

# Create your models here.

USER_ROLES = [
    ('Guest', 'Guest'),
    ('Host', 'Host'),
    ('Admin', 'Admin')
]

class User(AbstractUser):
    
    objects: UserManager = UserManager()
    
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
        )
    phone_number = models.CharField(max_length=20, null= True, blank=True)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='Guest', null = False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        indexes = [
            models.Index(fields=['email'], name = 'idx_email_user')
        ]
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email')
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
    
    def __str__(self):
        return f'{self.conversation_id}'
    
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