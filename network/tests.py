from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Post, Like, Follow

# test the views
class NetworkTestCase(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(username="user1", password="password")
        self.user2 = get_user_model().objects.create_user(username="user2", password="password")
        self.post1 = Post.objects.create(user=self.user1, content="post1")
        self.post2 = Post.objects.create(user=self.user2, content="post2")
        self.like1 = Like.objects.create(user=self.user1, post=self.post2)
        self.follow1 = Follow.objects.create(user=self.user1, user_follower=self.user2)
        

