from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory
from django.utils.timezone import now
from django.contrib.auth.models import User

@receiver(post_save, sender = Message)
def send_notification(sender, instance, created, **kwargs):
    if created:
        try:
            Notification.objects.create(
                sender=instance.sender,
                receiver = instance.receiver,
                title = f"New message from {instance.sender.username}",
                content = f"You have received a new message: {instance.content[:100]}..." 
                    if len(instance.content) > 100 else instance.content,
                message=instance,
            )
            print(f"Notification created for message: {instance.id}")  # Debug
        except Exception as e:
            print(f"Error creating notification: {e}")

@receiver(post_delete, sender = Message)
def cleanup_notifications_on_message_delete(sender, instance, created, **kwargs):
    instance.notifications.all().delete()
    
    
@receiver(post_save, sender=User)
def create_welcome_notification(sender, instance, created, **kwargs):
    """
    Create a welcome notification for new users
    """
    if created:
        Notification.objects.create(
            user=instance,
            notification_type='system',
            title="Welcome to our messaging system!",
            content="Thank you for joining. You can now send and receive messages."
        )
        print(f"Welcome notification created for new user: {instance.username}")
        
@receiver(pre_save, sender = Message)
def log_message_history(sender, instance, **kwargs):
    if instance.pk:
        MessageHistory.objects.create(
            sender=instance.sender,
            receiver = instance.receiver,
            content = f"You have received a new message: {instance.content[:100]}..." 
                if len(instance.content) > 100 else instance.content,
            is_read = instance.is_read
        )

@receiver(post_save, sender = Message)
def one_time_message_history_save(sender, instance, created, **kwargs):
    if created:
        try:
            MessageHistory.objects.create(
            sender=instance.sender,
            receiver = instance.receiver,
            content = f"You have received a new message: {instance.content[:100]}..." 
                if len(instance.content) > 100 else instance.content,
            is_read = instance.is_read
        )
        except Exception as e:
            print(f"Error creating notification: {e}")
        post_save.disconnect(one_time_message_history_save, sender = Message)