from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('message', views.SendMessageView, basename='message')
router.register('notification', views.NotificationViewset)

app_name = 'messaging'

urlpatterns = [
    path('', include(router.urls)),
    path('message_history/', views.MessageHistoryListView.as_view(), name = 'message_history'),
]
