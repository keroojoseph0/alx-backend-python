from django.shortcuts import render
from rest_framework import viewsets
from .models import Message, Notification, MessageHistory
from .serializers import MessageSerializer, NotificationSerializer, MessageHistorySerializer
from rest_framework.generics import ListAPIView
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
    
