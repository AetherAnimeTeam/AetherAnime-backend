from locust import HttpUser, task, between
import random


class AnimeUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def view_anime(self):
        anime_id = random.randint(1, 1000)  # Предположим, что у вас есть 1000 аниме
        self.client.get(f"/api/anime/{anime_id}/", name="/api/anime/[id]/")

    @task(3)
    def add_comment(self):
        anime_id = random.randint(1, 1000)
        comment_data = {
            "text": "This is a test comment",
        }
        self.client.post(
            f"/api/comments/{anime_id}/", json=comment_data, name="/api/comments/[id]/"
        )

    @task(2)
    def register_user(self):
        user_data = {
            "username": f"user{random.randint(1, 100000)}",
            "email": f"user{random.randint(1, 100000)}@example.com",
            "password": "testpassword123",
        }
        self.client.post("/api/register/", json=user_data, name="/api/register/")

    @task
    def view_anime_list(self):
        self.client.get("/api/anime/", name="/api/anime/")
