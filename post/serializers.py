from rest_framework import serializers

from post.models import Post, PostLike, PostComment, CommentLike
from users.models import Users


class UserSerializers(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    class Meta:
        model=Users
        fields=['id',
                'username',
                'photo',
                ]


class PostSerializers(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    author=UserSerializers(read_only=True)
    post_like_count=serializers.SerializerMethodField("get_like_count")
    post_comment_count=serializers.SerializerMethodField("get_comment_count")
    liked_me=serializers.SerializerMethodField("get_liked_me")
    is_video=serializers.SerializerMethodField("get_is_video")
    class Meta:
        model=Post
        fields=['id',
                'author',
                'image',
                'video',
                'is_video',
                'caption',
                'post_like_count',
                'post_comment_count',
                'liked_me',
                'created_time',
                ]
        extra_kwargs={
            'image':{'required':False},
            'video':{'required':False},
        }
    def validate(self, attrs):
        if not attrs.get('image') and not attrs.get('video') and not self.instance:
            raise serializers.ValidationError({"media": "Rasm yoki video yuklash majburiy"})
        return attrs
    @staticmethod
    def get_like_count(obj):
        return obj.likes.count()
    @staticmethod
    def get_comment_count(obj):
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
    @staticmethod
    def get_is_video(obj):
        return bool(obj.video)

class PostCommentSerializers(serializers.ModelSerializer):
    id= serializers.UUIDField(read_only=True)
    author=UserSerializers(read_only=True)
    replies=serializers.SerializerMethodField("get_replies")
    like_count=serializers.SerializerMethodField("get_like_count")
    liked_me=serializers.SerializerMethodField("get_liked_me")
    class Meta:
        model=PostComment
        fields=('id',
                'author',
                "post",
                'comment',
                'parent',
                'created_time',
                'liked_me',
                'like_count',
                'replies'
                )


    def get_replies(self,obj):
        if obj.child.exists():
            serializers=self.__class__(obj.child.all(),many=True,context=self.context)
            return serializers.data
        else:
            return None
    @staticmethod
    def get_like_count(obj):
        return obj.likes.count()
    def get_liked_me(self,obj):
        user=self.context.get('request').user
        if user.is_authenticated:
            return obj.likes.filter(author=user).exists()
        else:
            return False

class CommentLikeSerializers(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    author=UserSerializers(read_only=True)
    class Meta:
        model=CommentLike
        fields=['id','author','comment']

class PostLikeSerializers(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    author=UserSerializers(read_only=True)
    class Meta:
        model=PostLike
        fields=['id','author','post']