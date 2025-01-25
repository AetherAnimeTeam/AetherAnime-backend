from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Comment, CommentReaction


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

    def test_get_user_reaction_with_context(self):
        # Создаем пользователя
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass"
        )

        another_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="testpass"
        )

        comment = Comment.objects.create(anime_id=1, user=user, content="Test comment")

        CommentReaction.objects.create(user=user, comment=comment, reaction=True)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(f"/api/comments/1/")

        self.assertEqual(response.status_code, 200)
        data = response.json()["results"]

        returned_comment = next((item for item in data if item["id"] == comment.id), None)
        self.assertIsNotNone(returned_comment, "Комментарий с заданным ID не найден в ответе")
        self.assertEqual(returned_comment["user_reaction"], True)

        client.force_authenticate(user=another_user)
        response = client.get(f"/api/comments/1/")
        data = response.json()["results"]

        returned_comment = next((item for item in data if item["id"] == comment.id), None)
        self.assertIsNotNone(returned_comment, "Комментарий с заданным ID не найден в ответе")
        self.assertIsNone(returned_comment["user_reaction"])
