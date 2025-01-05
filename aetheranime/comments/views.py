from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import Comment
from .serializers import CommentSerializer


class GetCommentsAPIView(APIView):
    def get(self, request, anime_id, comment_id=None):
        if comment_id:
            comments = Comment.objects.filter(
                reply_to_id=comment_id,
            )
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


class AddCommentAPIView(APIView):
    def post(self, request, anime_id):
        text = request.data.get("text", "")
        if not text:
            return Response(
                {"error": "text is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Создаем новый комментарий
        comment = Comment.objects.create(
            anime_id=anime_id, user=request.user, content=text, reply_to=None
        )

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AddReplyAPIView(APIView):
    def post(self, request, anime_id, comment_id):
        text = request.data.get("text", "")
        if not text:
            return Response(
                {"error": "text is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        parent_comment = get_object_or_404(Comment, pk=comment_id)

        reply = Comment.objects.create(
            anime_id=anime_id,
            user=request.user,
            content=text,
            reply_to=parent_comment,
        )

        serializer = CommentSerializer(reply)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeleteCommentAPIView(APIView):
    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)

        if comment.replies.exists():
            comment.content = None
            comment.save()
            return Response(
                {"message": "Comment content has been deleted, but replies are kept."},
                status=status.HTTP_200_OK,
            )

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
