from rest_framework import serializers
from .models import User, Message, Conversation
from .auth import UserSerializer




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
    participants_username = serializers.SerializerMethodField()
    participants_count = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'conversation_name', 'participants', 'participants_username', 'messages', 'created_at', 'participants_count']
        
    def get_participants_username(self, obj):
        # Return list of usernames
        return list(obj.participants.values_list('username', flat=True))
    
    def get_participants_count(self, obj):
        return obj.participants.count()
    