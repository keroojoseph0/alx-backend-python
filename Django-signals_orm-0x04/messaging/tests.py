from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from .models import Message, Notification
from .signals import send_notification


class MessagingModelsTests(TestCase):
    """Test cases for Message and Notification models"""
    
    def setUp(self):
        """Set up test users"""
        self.sender = User.objects.create_user(
            username='sender', 
            email='sender@example.com', 
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver', 
            email='receiver@example.com', 
            password='testpass123'
        )
    
    def test_message_creation(self):
        """Test creating a message"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message!"
        )
        
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.receiver, self.receiver)
        self.assertEqual(message.content, "Hello, this is a test message!")
        self.assertFalse(message.is_read)
        self.assertIsNotNone(message.timestamp)
    
    def test_notification_creation(self):
        """Test creating a notification"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        
        notification = Notification.objects.create(
            user=self.receiver,
            message=message,
            notification_type='message',
            title="New message",
            content="You have a new message"
        )
        
        self.assertEqual(notification.sender, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, 'message')
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.received_at)
    
    def test_message_str_method(self):
        """Test Message __str__ method"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        expected_str = f"Message from {self.sender} to {self.receiver}"
        self.assertEqual(str(message), expected_str)
    
    def test_notification_str_method(self):
        """Test Notification __str__ method"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        notification = Notification.objects.create(
            user=self.receiver,
            message=message,
            title="New message"
        )
        expected_str = f"Notification for {self.receiver}: New message"
        self.assertEqual(str(notification), expected_str)


class MessagingSignalsTests(TestCase):
    """Test cases for messaging signals"""
    
    def setUp(self):
        """Set up test users"""
        self.sender = User.objects.create_user(
            username='sender', 
            email='sender@example.com', 
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver', 
            email='receiver@example.com', 
            password='testpass123'
        )
    
    def test_notification_created_on_new_message(self):
        """Test that a notification is automatically created when a new message is saved"""
        # Disconnect signal temporarily to count initial notifications
        post_save.disconnect(send_notification, sender=Message)
        
        # Count initial notifications for receiver
        initial_count = Notification.objects.filter(user=self.receiver).count()
        
        # Reconnect signal
        post_save.connect(send_notification, sender=Message)
        
        # Create a new message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message for signal testing"
        )
        
        # Check if notification was created
        final_count = Notification.objects.filter(user=self.receiver).count()
        self.assertEqual(final_count, initial_count + 1)
        
        # Verify notification details
        notification = Notification.objects.filter(user=self.receiver).latest('created_at')
        self.assertEqual(notification.sender, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.notification_type, 'message')
        self.assertIn(self.sender.username, notification.title)
        self.assertIn("Test message for signal testing", notification.content)
    
    def test_multiple_notifications_for_multiple_messages(self):
        """Test that multiple messages create multiple notifications"""
        # Create multiple messages
        for i in range(3):
            Message.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                content=f"Message {i+1}"
            )
        
        # Check that 3 notifications were created
        notifications_count = Notification.objects.filter(user=self.receiver).count()
        self.assertEqual(notifications_count, 3)
    
    def test_no_notification_on_message_update(self):
        """Test that notifications are not created when existing messages are updated"""
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Initial message"
        )
        
        # Count notifications after creation
        notifications_after_creation = Notification.objects.filter(user=self.receiver).count()
        
        # Update the message (should NOT create a new notification)
        message.content = "Updated message"
        message.save()
        
        # Count notifications after update
        notifications_after_update = Notification.objects.filter(user=self.receiver).count()
        
        # Number of notifications should remain the same
        self.assertEqual(notifications_after_creation, notifications_after_update)
    
    def test_notification_cleanup_on_message_delete(self):
        """Test that notifications are cleaned up when a message is deleted"""
        # Create a message (which creates a notification)
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Message to be deleted"
        )
        
        # Verify notification was created
        notification_exists = Notification.objects.filter(message=message).exists()
        self.assertTrue(notification_exists)
        
        # Delete the message
        message.delete()
        
        # Verify notification was also deleted
        notification_exists_after = Notification.objects.filter(message_id=message.pk).exists()
        self.assertFalse(notification_exists_after)


class NotificationActionsTests(TestCase):
    """Test notification actions and methods"""
    
    def setUp(self):
        """Set up test data"""
        self.sender = User.objects.create_user(
            username='sender', 
            email='sender@example.com', 
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver', 
            email='receiver@example.com', 
            password='testpass123'
        )
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        self.notification = Notification.objects.create(
            user=self.receiver,
            message=self.message,
            title="Test notification",
            content="Test content"
        )
    
    def test_mark_as_read(self):
        """Test marking a notification as read"""
        self.assertFalse(self.notification.is_read)
        
        self.notification.mark_as_read()
        self.notification.refresh_from_db()
        
        self.assertTrue(self.notification.is_read)
    
    def test_mark_message_as_read(self):
        """Test marking a message as read"""
        self.assertFalse(self.message.is_read)
        
        self.message.mark_as_read()
        self.message.refresh_from_db()
        
        self.assertTrue(self.message.is_read)
    
    def test_related_message_property(self):
        """Test the related_message property of Notification"""
        related_message = self.notification.related_message
        self.assertEqual(related_message, self.message)


class PerformanceTests(TestCase):
    """Test performance aspects"""
    
    def setUp(self):
        """Set up multiple users and messages"""
        self.sender = User.objects.create_user(
            username='sender', 
            email='sender@example.com', 
            password='testpass123'
        )
        # Create multiple receivers
        self.receivers = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'receiver{i}', 
                email=f'receiver{i}@example.com', 
                password='testpass123'
            )
            self.receivers.append(user)
    
    def test_bulk_message_creation_performance(self):
        """Test creating messages in bulk"""
        import time
        
        start_time = time.time()
        
        # Create 100 messages
        messages = []
        for i in range(100):
            receiver = self.receivers[i % len(self.receivers)]
            message = Message(
                sender=self.sender,
                receiver=receiver,
                content=f"Bulk message {i}"
            )
            messages.append(message)
        
        Message.objects.bulk_create(messages)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Verify all messages were created
        total_messages = Message.objects.count()
        self.assertEqual(total_messages, 100)
        
        # Verify notifications were created for each message
        total_notifications = Notification.objects.count()
        self.assertEqual(total_notifications, 100)
        
        print(f"\nCreated 100 messages and notifications in {creation_time:.2f} seconds")
