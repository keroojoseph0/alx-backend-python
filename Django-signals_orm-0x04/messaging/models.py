from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='messaes', on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields = ['receiver', 'is_read']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"
    
    def get_absolute_url(self):
        return reverse("message", kwargs={"pk": self.pk})
    
    def mark_as_read(self):
        self.is_read = True
        self.save()

    
class Notification(models.Model):
    NOTIFICATIONS_TYPE = [
        ('message', 'New Message'),
        ('system', 'System Notification'),
        ('alert', 'Alert'),
    ]
    
    sender = models.ForeignKey(User, related_name='notifications_sender', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='notifications_receiver', on_delete=models.CASCADE)
    received_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATIONS_TYPE, default='message')
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields = ['sender', 'is_read']),
            models.Index(fields = ['received_at'])
        ]
    
    def __str__(self):
        return f"Notification for {self.sender}: {self.title}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
        
    @property
    def related_message(self):
        return self.message
    
    
class MessageHistory(models.Model):
    sender = models.ForeignKey(User, related_name='messages_history_sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='messaes_history_receiver', on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField()
    
    class Meta:
        indexes = [
            models.Index(fields = ['receiver', 'is_read']),
        ]
    
    def __str__(self):
        return f"Message History from {self.sender.username} to {self.receiver.username}"