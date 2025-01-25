from rest_framework import serializers
from .models import Comment, WatchedHistory, AnimeStatus, Review


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    replies_n = serializers.SerializerMethodField()
    reply_to = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(), required=False, allow_null=True
    )
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "anime_id",
            "reply_to",
            "user",
            "content",
            "created_at",
            "replies_n",
            "replies",
            "like_count",
            "dislike_count",
            "user_reaction",
        ]

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all()[:3], many=True).data
        return []

    def get_replies_n(self, obj):
        if obj.replies.exists():
            return obj.replies.count()
        return 0

    def get_like_count(self, obj):
        return obj.reactions.filter(reaction=True).count()

    def get_dislike_count(self, obj):
        return obj.reactions.filter(reaction=False).count()

    def get_user_reaction(self, obj):
        # Проверяем, что контекст не пустой и содержит ключ "request"
        if not self.context or "request" not in self.context:
            return None

        user = self.context["request"].user
        if user.is_authenticated:
            reaction = obj.reactions.filter(user=user).first()
            if reaction:
                return reaction.reaction
        return None

    def create(self, validated_data):
        """
        Переопределяем метод создания комментария, чтобы при создании ответа на комментарий
        корректно обрабатывался `reply_to`.
        """
        reply_to = validated_data.get("reply_to", None)
        if reply_to:
            validated_data["reply_to"] = reply_to

        # Создание нового комментария
        comment = Comment.objects.create(**validated_data)
        return comment


class WatchedHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchedHistory
        fields = ["id", "anime_id", "season", "episode", "timestamp", "user"]


class AnimeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimeStatus
        fields = ["id", "anime_id", "status", "user"]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "anime_id", "content", "user", "created_at"]
