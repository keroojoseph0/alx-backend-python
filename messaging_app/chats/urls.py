from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('message', views.MessageiewSet, basename='message')
router.register('conversation', views.ConversationViewSet, basename='conversation')

app_name = 'chats'

urlpatterns = [
    path('', include(router.urls)),
]
