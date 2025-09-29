from django.urls import path
from .views import PostList,PostCreateView,PostRetrieveUpdateDestroyView,\
    PostCommentListApiView,PostCommentCreateApiView
urlpatterns=[
    path('posts/',PostList.as_view()),
    path("posts/create/",PostCreateView.as_view()),
    path("posts/<uuid:pk>/",PostRetrieveUpdateDestroyView.as_view()),
    path('posts/<uuid:pk>/comments/',PostCommentListApiView.as_view()),
    path('posts/<uuid:pk>/comments/create/',PostCommentCreateApiView.as_view()),
]