from django.shortcuts import render
from rest_framework import viewsets
from .models import Message, Notification, MessageHistory
from .serializers import MessageSerializer, NotificationSerializer, MessageHistorySerializer, UserSerializer
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

class SendMessageView(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    
    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(sender = self.request.user)
            
            
    
    
class NotificationViewset(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class MessageHistoryListView(ListAPIView):
    queryset = MessageHistory.objects.all()
    serializer_class = MessageHistorySerializer
    
@api_view(['GET', 'DELETE'])
def delete_user(request, pk):
    try:
        user = get_object_or_404(User, pk=pk)
    except ValueError:
        return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'GET':
        # For GET requests, return user information (optional)
        serializer = UserSerializer(instance = user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        user.delete() 
        return Response(
            {'message': 'User deleted successfully'}, 
            status=status.HTTP_204_NO_CONTENT
        )