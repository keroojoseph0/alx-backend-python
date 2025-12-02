from django.shortcuts import render
from rest_framework import viewsets
from .models import Message, Notification, MessageHistory
from .serializers import MessageSerializer, NotificationSerializer, MessageHistorySerializer, UserSerializer, UnreadMessageSerializer
from rest_framework.generics import ListAPIView, CreateAPIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


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
 
@method_decorator(csrf_exempt, name='dispatch')      
class ReplyMessageView(CreateAPIView):
    serializer_class = MessageSerializer
    
    def perform_create(self, serializer):
        parent_id = self.kwargs['parent_id']
        parent = Message.objects.get(pk = parent_id)
        
        serializer.save(
            sender=self.request.user,
            receiver=parent.receiver,
            parent_message=parent
        )
        
# Recursive function to return message and replies
def get_threaded_messages(message):
    """Return a message and all its replies in a nested/threaded structure."""
    result = {
        'message': message,
        'replies': [get_threaded_messages(reply) for reply in message.replies.all()]
    }
    return result

@cache_page(60)
def conversation_view(request, message_id):
    root_message = get_object_or_404(Message.objects.select_related('sender', 'receiver')
                                     .prefetch_related('replies__sender', 'replies__receiver'),
                                     id=message_id,
                                     sender = request.user)

    # Fetch all replies recursively
    threaded_messages = get_threaded_messages(root_message)

    return render(request, 'messaging/conversation.html', {'threaded_messages': threaded_messages})

@api_view(['GET'])
def unread_message(request):
    try:
        receiver = request.user
        messages = Message.unread.unread_for_user(receiver).only('sender', 'content', 'replies', 'edited')
    except Message.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = UnreadMessageSerializer(messages, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)
