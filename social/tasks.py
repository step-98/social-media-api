from django.utils import timezone

from social.models import Post
from celery import shared_task


@shared_task
def publish_scheduled_post() -> int:
    posts = Post.objects.filter(is_published=False, publish_at__lte=timezone.now())
    updated_posts = posts.update(is_published=True)
    return updated_posts