import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.utils.text import slugify

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
    conversation_name = models.CharField(max_length=100, blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def __str__(self):
        return f'{self.conversation_name}'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.conversation_name) if self.conversation_name else str(self.conversation_id)
        super().save(*args, **kwargs)
        
        
class Message(models.Model):
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField(null = False)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.message_body)