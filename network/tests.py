from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from .models import Post, Like, Follow



class NetworkTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="testpassword")
        self.user2 = get_user_model().objects.create_user(username="testuser2", password="testpassword")
        self.post = Post.objects.create(user=self.user, content="Test content")
        self.like = Like.objects.create(user=self.user, post=self.post)
        self.follow = Follow.objects.create(user=self.user, user_follower=self.user2)
        # Set up the client
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

    def test_post(self):
        self.assertEqual(self.post.content, "Test content")
        self.assertEqual(self.post.user, self.user)

    def test_like(self):
        self.assertEqual(self.like.user, self.user)
        self.assertEqual(self.like.post, self.post)

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "network/index.html")

    def test_remove_like(self):
        self.client.force_login(self.user)
        response = self.client.post(f"/remove_like/{self.post.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Like removed.")

    def test_add_like(self):
        self.client.force_login(self.user)
        response = self.client.post(f"/add_like/{self.post.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Like added.")

    def test_new_post(self):
        self.client.force_login(self.user)
        response = self.client.post("/new_post", {"content": "New content"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.last().content, "New content")

