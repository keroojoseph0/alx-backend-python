from rest_framework import serializers
from .models import Message, Notification, MessageHistory

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source = 'sender.username', read_only = True)
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'is_read']
        
class NotificationSerializer(serializers.ModelSerializer):
    receiver = serializers.CharField(source = 'receiver.username', read_only = True)
    title = serializers.CharField(read_only = True)
    content = serializers.CharField(read_only = True)
    
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'receiver', 'message', 'notification_type', 'title', 'content', 'is_read', 'received_at']
        
class MessageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageHistory
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'is_read']