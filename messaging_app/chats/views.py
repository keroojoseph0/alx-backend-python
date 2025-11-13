from django.shortcuts import render
from rest_framework import viewsets
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework.response import Response
from rest_framework import status, filters

# Create your views here.

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().prefetch_related('participants', 'messages')
    serializer_class = ConversationSerializer
    
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().select_related('sender', 'conversation')
    serializer_class = MessageSerializer
    
    
    
    def create(self, request, *args, **kwargs):
        data = request.data

        # Simple validation
        if 'message_body' not in data or not data['message_body'].strip():
            return Response(
                {"error": "Message body is required."},
                status=status.HTTP_400_BAD_REQUEST  # Bad request
            )

        # Create message logic
        message = Message.objects.create(
            sender_id=data['sender_id'],
            conversation_id=data['conversation_id'],
            message_body=data['message_body']
        )
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
