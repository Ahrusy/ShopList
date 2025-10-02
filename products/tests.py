from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Task, MoodTracking

User = get_user_model()

class TaskModelTest(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_task_creation(self):
        """Test that a task can be created successfully"""
        task = Task.objects.create(
            user=self.user,
            title='Test Task',
            description='This is a test task',
            priority='medium',
            status='pending'
        )
        
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.priority, 'medium')
        self.assertEqual(task.status, 'pending')
        self.assertIsNotNone(task.created_at)
        self.assertIsNotNone(task.updated_at)
    
    def test_task_string_representation(self):
        """Test that the task string representation is correct"""
        task = Task.objects.create(
            user=self.user,
            title='Test Task',
            description='This is a test task'
        )
        
        self.assertEqual(str(task), 'Test Task')


class MoodTrackingModelTest(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_mood_tracking_creation(self):
        """Test that a mood tracking entry can be created successfully"""
        mood = MoodTracking.objects.create(
            user=self.user,
            mood='happy',
            note='Feeling great today!'
        )
        
        self.assertEqual(mood.mood, 'happy')
        self.assertEqual(mood.user, self.user)
        self.assertEqual(mood.note, 'Feeling great today!')
        self.assertIsNotNone(mood.created_at)
    
    def test_mood_tracking_string_representation(self):
        """Test that the mood tracking string representation is correct"""
        mood = MoodTracking.objects.create(
            user=self.user,
            mood='very_happy',
            note='Amazing day!'
        )
        
        # The string representation includes the mood display and timestamp
        self.assertIn('Очень радостное', str(mood))