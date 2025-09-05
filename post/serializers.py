from rest_framework import serializers

from post.models import Post, PostLike
from users.models import Users


class UserSerializers(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    class Meta:
        model=Users
        fields=['id','username','photo',]


class PostSerializers(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    author=UserSerializers(read_only=True)
    post_like_count=serializers.SerializerMethodField("get_like_count")
    post_comment_count=serializers.SerializerMethodField("get_comment_count")
    liked_me=serializers.SerializerMethodField("liked_me")
    class Meta:
        model=Post
        fields=['id','author','image','caption','post_like','post_comment_count','liked_me']

    def get_like_count(self,obj):
        return obj.likes.count()
    def get_comment_count(self,obj):
        return obj.comments.count()
    def get_liked_me(self,obj):
        request=self.context.get('request',None)
        if request and request.user.is_authenticated:
            try:
                like=PostLike.objects.get(post=obj, author=request.user)
                return True
            except PostLike.DoesNotExist:
                return False
        return False

