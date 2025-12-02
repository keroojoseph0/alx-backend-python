from django.db import models

class UnreadMessagesManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_read = False)
    
    def unread_for_user(self, receiver):
        return self.get_queryset().filter(receiver = receiver)