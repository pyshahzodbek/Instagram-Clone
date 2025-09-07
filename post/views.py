from gc import get_objects

from rest_framework import generics
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly,IsAuthenticated
from .models import Post, PostComment, PostLike, CommentLike
from .serializers import PostSerializers,PostLikeSerializers,PostCommentSerializers,CommentLikeSerializers
from shared.custom_pagination import CustomPagination


class PostList(generics.ListAPIView):

    serializer_class = PostSerializers
    permission_classes = [AllowAny,]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()



class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializers
    permission_classes = [IsAuthenticated,]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializers
    permission_classes = [IsAuthenticatedOrReadOnly,]
    queryset = Post.objects.all()

