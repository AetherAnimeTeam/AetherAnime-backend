from rest_framework import serializers
from .models import Comment, WatchedHistory, AnimeStatus, Review


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'anime_id', 'reply_to', 'user', 'content', 'created_at', 'replies']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class WatchedHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchedHistory
        fields = ['id', 'anime_id', 'season', 'episode', 'timestamp', 'user']


class AnimeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimeStatus
        fields = ['id', 'anime_id', 'status', 'user']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'anime_id', 'content', 'user', 'created_at']
