from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from user_auth.models import Status


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected resource"})


@api_view(["GET"])
def user_status(request, user_id):
    statuses = (
        Status.objects.filter(user_id=user_id)
        .values("status")
        .annotate(count=Count("status"))
    )
    data = {status["status"]: status["count"] for status in statuses}
    return Response(data)
