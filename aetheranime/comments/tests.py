from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Comment

User = get_user_model()


class CommentAPIViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )
        self.client.force_authenticate(user=self.user)
        self.comment = Comment.objects.create(
            anime_id=1,
            user=self.user,
            content="Test comment",
        )

    def test_get_comments(self):
        url = reverse("comments", kwargs={"anime_id": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["content"], "Test comment")

    def test_create_comment(self):
        url = reverse("comments", kwargs={"anime_id": 1})
        data = {"text": "New comment"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.last().content, "New comment")

    def test_create_reply(self):
        url = reverse("replies", kwargs={"anime_id": 1, "comment_id": self.comment.id})
        data = {"text": "Reply comment"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.last().reply_to, self.comment)

    def test_delete_comment(self):
        url = reverse("replies", kwargs={"anime_id": 1, "comment_id": self.comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_comment_with_replies(self):
        reply = Comment.objects.create(
            anime_id=1,
            user=self.user,
            content="Reply comment",
            reply_to=self.comment,
        )
        url = reverse("replies", kwargs={"anime_id": 1, "comment_id": self.comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertIsNone(self.comment.content)
        self.assertTrue(Comment.objects.filter(id=reply.id).exists())

    def test_delete_comment_unauthorized(self):
        another_user = User.objects.create_user(
            username="anotheruser",
            email="another@example.com",
            password="testpassword123",
        )
        self.client.force_authenticate(user=another_user)
        url = reverse("replies", kwargs={"anime_id": 1, "comment_id": self.comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
