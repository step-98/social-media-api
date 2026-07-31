from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from social.models import Follow
from social.serializers import FollowSerializer

from user.filters import UserFilter
from user.serializers import UserSerializer, UserListSerializer, UserDetailSerializer, LogoutSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserViewSet(ReadOnlyModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return UserDetailSerializer
        if self.action == "follow":
            return FollowSerializer
        return UserListSerializer

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="follow",
    )
    def follow(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data={
            "following": user.id
        })
        serializer.is_valid(raise_exception=True)
        serializer.save(follower=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=["DELETE"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="unfollow",
    )
    def unfollow(self, request, pk=None):
        user = self.get_object()
        qs = Follow.objects.filter(follower=request.user, following=user)
        if qs.exists():
            qs.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "You are not following this user"}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["GET"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="following",
    )
    def following(self, request, pk=None):
        user = self.get_object()
        follow_qs = user.following.select_related("following")
        followers = [follow_obj.following for follow_obj in follow_qs]
        serializer = self.get_serializer(
            followers,
            many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="followers",
    )
    def followers(self, request, pk=None):
        user = self.get_object()
        follow_qs = user.followers.select_related("follower")
        following = [follow_obj.follower for follow_obj in follow_qs]
        serializer = self.get_serializer(
            following,
            many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
            return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
