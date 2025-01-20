from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import Comment, CommentReaction
from .serializers import CommentSerializer


class CommentAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, anime_id, comment_id=None):
        comments = Comment.objects.filter(
            anime_id=anime_id,
            reply_to=comment_id,
        )

        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get("page_size", 20)
        paginated_comments = paginator.paginate_queryset(comments, request)

        serializer = CommentSerializer(paginated_comments, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, anime_id, comment_id=None):
        text = request.data.get("text", "")
        if not text:
            return Response(
                {"error": "text is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        parent_comment = get_object_or_404(Comment, pk=comment_id) if comment_id else None

        comment = Comment.objects.create(anime_id=anime_id, user=request.user, content=text, reply_to=parent_comment)

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, anime_id, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)

        if request.user.id != comment.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)

        if comment.replies.exists():
            comment.content = None
            comment.save()
            return Response(
                {"message": "Comment content has been deleted, but replies are kept."},
                status=status.HTTP_200_OK,
            )

        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentLikeAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, anime_id, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        reaction, created = CommentReaction.objects.get_or_create(user=request.user, comment=comment)
        if not created and reaction.reaction == True:
            reaction.delete()
        else:
            reaction.reaction = True
            reaction.save()
        return Response({'status': 'success'})


class CommentDislikeAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, anime_id, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        reaction, created = CommentReaction.objects.get_or_create(user=request.user, comment=comment)
        if not created and reaction.reaction == False:
            reaction.delete()
        else:
            reaction.reaction = False
            reaction.save()
        return Response({'status': 'success'})
