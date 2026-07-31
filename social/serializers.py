from rest_framework import serializers
from django.utils import timezone
from social.models import Follow, Hashtag, Comment, Post, Like


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Follow
        fields = ("follower", "following",)


    def validate(self, attrs):
        request = self.context["request"]
        qs = Follow.objects.filter(
            following=attrs["following"],
            follower=request.user
        )

        if request.user == attrs["following"]:
            raise serializers.ValidationError("You can't follow yourself")
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "You are already following this user"
            )
        return attrs


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name",)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(),
    )
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S",
        read_only=True
    )
    class Meta:
        model = Comment
        fields = ("id", "content", "author", "post", "created_at")


class LikeSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(),
    )
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Like
        fields = ("id", "user", "post")

    def validate(self, attrs):
        request = self.context["request"]
        qs = Like.objects.filter(
            post=attrs["post"],
            user=request.user
        )

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "You already liked this post"
            )
        return attrs


class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S",
        read_only=True
    )
    hashtags = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        read_only=True,
    )
    hashtags_input = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
    )
    comments = CommentSerializer(many=True, read_only=True)
    likes = serializers.IntegerField(
        source="likes.count",
        read_only=True,
    )
    is_published = serializers.BooleanField(
        read_only=True,
    )
    class Meta:
        model = Post
        fields = (
            "id",
            "content",
            "author",
            "created_at",
            "image",
            "hashtags",
            "hashtags_input",
            "comments",
            "likes",
            "publish_at",
            "is_published"
        )

    def create(self, validated_data):
        hashtags_data = validated_data.pop("hashtags_input", [])
        publish_at = validated_data.get("publish_at")
        now = timezone.now()
        if publish_at:
            if now < publish_at:
                validated_data["is_published"] = False
        post = Post.objects.create(**validated_data)
        for hashtag in hashtags_data:
            data, _ = Hashtag.objects.get_or_create(name=hashtag)
            post.hashtags.add(data)
        return post

    def update(self, instance, validated_data):
        hashtags_data = validated_data.pop("hashtags_input", [])
        post = super().update(instance, validated_data)
        hashtags = []
        if hashtags_data:
            for hashtag in hashtags_data:
                data, _ = Hashtag.objects.get_or_create(name=hashtag)
                hashtags.append(data)
            post.hashtags.set(hashtags)
        return post
