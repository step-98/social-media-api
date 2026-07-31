from django_filters import rest_framework as filters

from social.models import Hashtag, Post


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class HashtagFilter(filters.FilterSet):
    id = NumberInFilter(field_name="id", lookup_expr="in")
    class Meta:
        model = Hashtag
        fields = ["id", "name"]


class PostFilter(filters.FilterSet):
    id = NumberInFilter(field_name="id", lookup_expr="in")
    content = filters.CharFilter(field_name="content", lookup_expr="icontains")
    author = NumberInFilter(field_name="author", lookup_expr="in")
    created_at = filters.DateFromToRangeFilter(field_name="created_at")
    hashtags = filters.CharFilter(field_name="hashtags__name", lookup_expr="icontains")

    class Meta:
        model = Post
        fields = ["id", "content", "author", "created_at", "hashtags"]