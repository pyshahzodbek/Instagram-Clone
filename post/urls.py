from django.urls import path
from .views import PostList,PostCreateView,PostRetrieveUpdateDestroyView,\
    PostCommentListApiView,PostCommentCreateApiView,CommentListCreateApiView,\
    PostCommentRetrivApiView,CommentLikeListView,LikesApiView,PostLIkeApiView

urlpatterns=[
    path('list/',PostList.as_view()),
    path("create/",PostCreateView.as_view()),
    path("<uuid:pk>/",PostRetrieveUpdateDestroyView.as_view()),
    path('<uuid:pk>/comments/',PostCommentListApiView.as_view()),
    path('<uuid:pk>/comments/create/',PostCommentCreateApiView.as_view()),
    path("comments/",CommentListCreateApiView.as_view()),

    path("comments/<uuid:pk>/",PostCommentRetrivApiView.as_view()),
    path("comments/<uuid:pk>/likes/",CommentLikeListView.as_view()),

    path('likes/',LikesApiView.as_view()),

    path("<uuid:pk>/create-delete-like/",PostLIkeApiView.as_view()),


]
