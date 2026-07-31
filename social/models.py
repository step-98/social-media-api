import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models


class Follow(models.Model):
    follower = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="followers")

    class Meta:
        unique_together = ("follower", "following")


class Comment(models.Model):
    content = models.CharField(max_length=255)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)


class Hashtag(models.Model):
    name = models.CharField(max_length=20, unique=True, )


def post_image(instance: "Post", filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return os.path.join(
        "uploads/posts/",
        f"{instance.pk}-{uuid.uuid4()}{ext}"
    )

class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=post_image, null=True, blank=True)
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name="posts")
    publish_at = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at", "author"]

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ("post", "user")
