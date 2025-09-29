from gc import get_objects

from rest_framework import generics
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

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
    queryset=Post.objects.all()

    def put(self,request,*args,**kwargs):
        post=self.get_object()
        serializer=self.serializer_class(post,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "success":True,
                "code":HTTP_200_OK,
                "message":"Post succesfully updated",
                "data":serializer.data
            }

        )
    def delete(self, request, *args, **kwargs):
        post=self.get_object()
        post.delete()
        return Response(
            {
                "success":True,
                "code":HTTP_204_NO_CONTENT,
                "message":"Post succesfully deleted",
                "data":None
            }

        )

class PostCommentListApiView(generics.ListAPIView):
    serializer_class = PostCommentSerializers
    permission_classes = [AllowAny,]


    def get_queryset(self):
       post_id=self.kwargs["pk"]
       queryset=PostComment.objects.filter(post__id=post_id)
       return queryset
class PostCommentCreateApiView(generics.CreateAPIView):
    serializer_class = PostCommentSerializers
    permission_classes = [IsAuthenticated,]

    def perform_create(self, serializer):
        post_id=self.kwargs['pk']
        serializer.save(user=self.request.user,post_id=post_id)
