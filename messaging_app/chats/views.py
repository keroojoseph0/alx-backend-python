from django.shortcuts import render
from rest_framework import viewsets
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, SignUpSerializer
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.decorators import api_view, permission_classes
from .models import User
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from .permissions import IsOwnerOrReadOnly

# Create your views here.

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().prefetch_related('participants', 'messages')
    serializer_class = ConversationSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().select_related('sender_id', 'conversation')
    serializer_class = MessageSerializer
    permission_classes = [IsOwnerOrReadOnly] 
    
    
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignUpSerializer(data = request.data)
    
    if serializer.is_valid():
        email = request.data['email']
        
        if User.objects.filter(email = email).exists():
            return Response({'message': 'The user email exist before'}, status=status.HTTP_400_BAD_REQUEST)
        else: 
            User.objects.create(
                email = email, 
                username = email.split('@')[0],
                password = make_password(request.data['password']),
                first_name = request.data['first_name'],
                last_name = request.data['last_name']
            )
            return Response({'message': 'User create successfuly'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)