from rest_framework import serializers
from .models import User, Message, Conversation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'password_hash', 'phone_number', 'role', 'created_at']
        
        read_only_fields = ['user_id', 'created_at']
        
        extra_kwargs = {
            'passwoerd_hash': {'write_only': True, 'required': True},
        }


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only = True)

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 'message_body', 'send_at']
        
        read_only_fields = ['message_id', 'sent_at']
        
        
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants_id', 'created_at']
        