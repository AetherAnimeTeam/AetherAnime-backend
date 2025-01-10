from rest_framework import serializers
from .models import Comment, WatchedHistory, AnimeStatus, Review


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    replies_n = serializers.SerializerMethodField()
    reply_to = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)

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
        ]
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all()[:3], many=True).data
        return []

    def get_replies_n(self, obj):
        if obj.replies.exists():
            return obj.replies.count()
        return 0

    def create(self, validated_data):
        """
        Переопределяем метод создания комментария, чтобы при создании ответа на комментарий
        корректно обрабатывался `reply_to`.
        """
        reply_to = validated_data.get('reply_to', None)
        if reply_to:
            validated_data['reply_to'] = reply_to
        
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
