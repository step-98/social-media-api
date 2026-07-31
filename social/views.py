from rest_framework import viewsets, mixins, status
from rest_framework. permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from social.filters import HashtagFilter, PostFilter
from social.models import Comment, Like, Hashtag, Post, Follow
from social.serializers import CommentSerializer, LikeSerializer, HashtagSerializer, PostSerializer
from social.permissions import IsAuthorOrIfAuthenticatedReadOnly, IsOwnerOrReadOnly
from rest_framework.pagination import PageNumberPagination


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrIfAuthenticatedReadOnly, ]

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = Comment.objects.select_related(
            "author",
            "post",
        )
        post = self.request.query_params.get("post", None)
        if post:
            post_ids = self._params_to_ints(post)
            queryset = queryset.filter(post_id__in=post_ids)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class LikeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]

    def get_queryset(self):
        return Like.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HashtagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = HashtagFilter


class PostPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 50


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrIfAuthenticatedReadOnly, ]
    pagination_class = PostPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PostFilter

    def get_queryset(self):
        following = list(
            Follow.objects.filter(follower=self.request.user).values_list(
                "following_id",
                flat=True
            )
        )
        following.append(self.request.user.id)
        queryset = Post.objects.filter(
            author__in=(following)
        ).select_related(
            "author"
        ).prefetch_related(
            "hashtags"
        ).filter(
            Q(is_published=True)
            | Q(author=self.request.user)
        )

        return queryset

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path="liked",
    )
    def liked(self, request):
        likes = Post.objects.filter(
            likes__user=self.request.user
        )
        serializer = self.get_serializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
