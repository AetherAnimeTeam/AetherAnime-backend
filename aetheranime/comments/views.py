from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from .models import Comment, WatchedHistory, AnimeStatus, Review
from .serializers import (
    CommentSerializer,
    WatchedHistorySerializer,
    AnimeStatusSerializer,
)
from rest_framework.pagination import PageNumberPagination


class GetCommentsAPIView(APIView):
    def get(self, request, anime_id, comment_id=None):
        if comment_id:
            comments = Comment.objects.filter(reply_to_id=comment_id)
        else:
            comments = Comment.objects.filter(
                anime_id=anime_id,
                reply_to__isnull=True,
            )

        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get("page_size", 20)
        paginated_comments = paginator.paginate_queryset(comments, request)

        serializer = CommentSerializer(paginated_comments, many=True)
        return paginator.get_paginated_response(serializer.data)


class AddWatchedHistoryAPIView(APIView):
    def post(self, request):
        serializer = WatchedHistorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetStatusAPIView(APIView):
    def post(self, request):
        serializer = AnimeStatusSerializer(data=request.data)
        if serializer.is_valid():
            AnimeStatus.objects.update_or_create(
                user=request.user,
                anime_id=serializer.validated_data["anime_id"],
                defaults={"status": serializer.validated_data["status"]},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RemoveStatusAPIView(APIView):
    def delete(self, request, anime_id):
        status_obj = get_object_or_404(
            AnimeStatus, user=request.user, anime_id=anime_id,
        )
        status_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
