from django.shortcuts import render
from rest_framework import viewsets
from .models import Message, Notification
from .serializers import MessageSerializer, NotificationSerializer
from django.views.generic import CreateView
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
