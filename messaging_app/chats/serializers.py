from rest_framework import serializers
from .models import User, Message, Conversation


class SignUpSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['email','first_name', 'last_name', 'password']
        
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False, 'write_only': True},
        }

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


# serializers.py
class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    
    # Write-only fields for input
    sender_id = serializers.UUIDField(write_only=True)
    conversation_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Message
        fields = [
            'message_id', 'sender_name', 'conversation', 
            'message_body', 'sent_at', 'sender_id', 'conversation_id'
        ]
        read_only_fields = ['message_id', 'sent_at', 'conversation']
            
    def get_sender_name(self, obj):
        # Use sender_id (the ForeignKey field) not sender
        if obj.sender_id:
            return f"{obj.sender_id.first_name} {obj.sender_id.last_name}".strip()
        return "Unknown Sender"
    
    def create(self, validated_data):
        # Extract UUIDs
        sender_uuid = validated_data.pop('sender_id')
        conversation_uuid = validated_data.pop('conversation_id')
        
        try:
            # Get instances
            sender = User.objects.get(user_id=sender_uuid)
            conversation = Conversation.objects.get(pk=conversation_uuid)
            
            # Create message
            message = Message.objects.create(
                sender_id=sender,
                conversation=conversation,
                message_body=validated_data['message_body']
            )
            return message
            
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "sender_id": f"User with ID {sender_uuid} not found"
            })
        except Conversation.DoesNotExist:
            raise serializers.ValidationError({
                "conversation_id": f"Conversation with ID {conversation_uuid} not found"
            })
        
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants_id', 'participants', 'messages', 'created_at']
        