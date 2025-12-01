"""
Custom permissions for the messaging app.
"""
from rest_framework import permissions

class IsAuthenticated(permissions.BasePermission):
    """
    Custom permission to ensure only authenticated users can access the API.
    This explicitly checks user.is_authenticated as required.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        return bool(request.user and request.user.is_authenticated)

class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to:
    - Send messages (POST)
    - View messages (GET) 
    - Update messages (PUT, PATCH)
    - Delete messages (DELETE)
    """
    
    def has_permission(self, request, view):
        # First, ensure user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # For creating messages (POST), check if user is participant in the conversation
        if request.method == 'POST':
            conversation_id = request.data.get('conversation')
            if conversation_id:
                from .models import Conversation
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                    return request.user in conversation.participants.all()
                except Conversation.DoesNotExist:
                    return False
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions for GET, PUT, PATCH, DELETE methods.
        Explicitly check for PUT, PATCH, DELETE as required.
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # For messages, check if user is a participant in the conversation
        if hasattr(obj, 'conversation'):
            conversation = obj.conversation
            is_participant = request.user in conversation.participants.all()
            
            # For safe methods (GET, HEAD, OPTIONS), allow if participant
            if request.method in permissions.SAFE_METHODS:
                return is_participant
            
            # Explicitly check for PUT, PATCH, DELETE methods as required
            elif request.method in ['PUT', 'PATCH', 'DELETE']:
                return is_participant
            
        return False

class IsMessageOwnerOrParticipant(permissions.BasePermission):
    """
    Custom permission to only allow message sender or conversation participants 
    to access messages. Includes explicit checks for PUT, PATCH, DELETE.
    """
    
    def has_permission(self, request, view):
        # Ensure user is authenticated for all operations
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions with explicit PUT, PATCH, DELETE checks.
        """
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # If user is the sender, allow all operations
        if hasattr(obj, 'sender') and obj.sender == request.user:
            # Allow GET, PUT, PATCH, DELETE for message owner
            return request.method in ['GET', 'PUT', 'PATCH', 'DELETE']
        
        # If message belongs to a conversation, check if user is a participant
        if hasattr(obj, 'conversation'):
            conversation = obj.conversation
            if hasattr(conversation, 'participants'):
                is_participant = request.user in conversation.participants.all()
                
                # Participants can view messages (GET) but not modify (PUT, PATCH, DELETE)
                if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
                    return is_participant
                elif request.method in ['PUT', 'PATCH', 'DELETE']:
                    # Only message owner can modify, not other participants
                    return False
        
        return False

class CanSendMessage(permissions.BasePermission):
    """
    Custom permission to check if user can send messages to a conversation.
    Explicitly checks for POST method and conversation participation.
    """
    
    def has_permission(self, request, view):
        # First, ensure user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # For POST requests (sending messages), check conversation participation
        if request.method == 'POST':
            conversation_id = request.data.get('conversation')
            if conversation_id:
                from .models import Conversation
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                    return request.user in conversation.participants.all()
                except Conversation.DoesNotExist:
                    return False
        
        return True