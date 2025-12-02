from rest_framework import serializers
from .models import Message, Notification, MessageHistory
from django.contrib.auth.models import User

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source = 'sender.username', read_only = True)
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'edited_by', 'edited_at', 'is_read', 'edited']
        
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
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'edited_by', 'edited_at', 'is_read', 'edited']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        
        extra_kwargs = {
            "password": {'write_only': True}
        }