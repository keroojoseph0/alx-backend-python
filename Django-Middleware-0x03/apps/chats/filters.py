import django_filters
from django.db import models
from .models import Message, Conversation
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageFilter(django_filters.FilterSet):
    # Filter by specific user (participant in conversation)
    participant = django_filters.ModelChoiceFilter(
        field_name='conversation__participants',
        queryset=User.objects.all(),
        label='Participant User'
    )
    
    # Filter by conversation with specific user
    with_user = django_filters.ModelChoiceFilter(
        method='filter_with_user',
        queryset=User.objects.all(),
        label='Messages with user'
    )
    
    # Search in message content
    search = django_filters.CharFilter(
        field_name='content',
        lookup_expr='icontains',
        label='Search in messages'
    )
    
    class Meta:
        model = Message
        fields = {
            'conversation': ['exact'],
            'sender_id': ['exact'],
        }
    
    def filter_with_user(self, queryset, name, value):
        """
        Filter messages from conversations where the specified user is a participant
        """
        if value:
            return queryset.filter(
                conversation__participants=value
            ).distinct()
        return queryset
    
    @property
    def qs(self):
        """
        Override to add default ordering and optimizations
        """
        queryset = super().qs
        return queryset.select_related('sender_id', 'conversation')

# Optional: Conversation filter if you need to filter conversations
class ConversationFilter(django_filters.FilterSet):
    has_unread_messages = django_filters.BooleanFilter(
        method='filter_has_unread_messages',
        label='Has unread messages'
    )
    
    participant = django_filters.ModelChoiceFilter(
        field_name='participants',
        queryset=User.objects.all(),
        label='Participant'
    )
    

    
    class Meta:
        model = Conversation
        fields = ['conversation_id']
    
    def filter_has_unread_messa_ges(self, queryset, name, value):
        """
        Filter conversations that have unread messages for current user
        """
        if value and hasattr(self.request, 'user'):
            return queryset.filter(
                messages__receiver=self.request.user # type: ignore
            ).distinct()
        return queryset

