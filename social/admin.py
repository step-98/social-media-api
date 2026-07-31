from django.contrib import admin

from social.models import Post, Comment, Follow, Hashtag, Like

admin.site.register(Follow)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Hashtag)
