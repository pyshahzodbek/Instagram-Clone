from gc import get_objects

from rest_framework import generics
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.views import APIView

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
class PostCommentRetrivApiView(generics.RetrieveAPIView):
    serializer_class = PostCommentSerializers
    permission_classes = [AllowAny,]
    queryset=PostComment.objects.all()

class CommentListCreateApiView(generics.ListCreateAPIView):
    serializer_class = PostCommentSerializers
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    queryset = PostComment.objects.all()
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentLikeListView(generics.ListAPIView):
    serializer_class = CommentLikeSerializers
    permission_classes = [AllowAny,]

    def get_queryset(self):
        comment_id = self.kwargs['pk']
        return CommentLike.objects.filter(comment_id=comment_id)

class LikesApiView(generics.ListAPIView):
    serializer_class =PostLikeSerializers
    permission_classes = [AllowAny,]
    queryset = PostLike.objects.all()
    pagination_class = CustomPagination

class PostLIkeApiView(APIView):

    def post(self,request,pk):

        try:
            post_like=PostLike.objects.create(
                author=self.request.user,
                post_id=pk
            )
            serializer = PostLikeSerializers(post_like)
            data=\
                {
                    "success": True,
                    "message": "Like muvafaqiyatli bosildi!",
                    "data": serializer.data,
                }


            return Response(data)


        except Exception as e:
            data={
                "success":False,
                "message":f"{str(e)}"
            }
            return Response(data,status=400)


    def delete(self,request,pk):

        try:
            post_like=PostLike.objects.get(
                author=self.request.user,
                post_id=pk
            )
            post_like.delete()
            data={
                "success":True,
                "message":"Like muvafaqiyatli uchirildi!",
                "data":None
            }
            return Response(data,status=204)
        except Exception as e:
            data = {
                "success": False,
                "message": f"{str(e)}"
            }
            return Response(data,status=400)



