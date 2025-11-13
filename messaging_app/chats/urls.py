from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('message', views.MessageViewSet, basename='message')
router.register('conversation', views.ConversationViewSet, basename='conversation')
messages_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')


app_name = 'chats'

urlpatterns = [
    path('', include(router.urls)),
]
