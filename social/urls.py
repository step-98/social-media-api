from django.urls import path, include
from rest_framework import routers

from social.views import CommentViewSet, HashtagViewSet, LikeViewSet, PostViewSet

app_name = "social"

router = routers.DefaultRouter()
router.register("comments", CommentViewSet)
router.register("hashtags", HashtagViewSet)
router.register("likes", LikeViewSet)
router.register("posts", PostViewSet)

urlpatterns = [path("", include(router.urls))]
