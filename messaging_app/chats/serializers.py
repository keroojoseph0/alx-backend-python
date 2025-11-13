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
        
    def validate_email(self, value):
        if '@' not in value:
            raise serializers.ValidationError('Not Valid Email')
        return value


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only = True)
    message_body = serializers.CharField()
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'sender_name', 'conversation', 'message_body', 'send_at']
        
        read_only_fields = ['message_id', 'sent_at']
            
    def get_sender_name(self, obj):
        return f"{obj.sender.first_name} {obj.sender.last_name}".strip()
        
        
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants_id', 'created_at']
        