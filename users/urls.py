from django.urls import path
from .serializers import SignUpSerializers
from .views import CreateApiView, VerifyApiView, GetNewVerification, ChangeUserInformationView, \
    ChangePhotoUserView, LoginVieW, LoginRefreshView, LogoutView, ResetPasswordView, ForgotPasswordView, \
    UserSearchView, UserDetailView, FollowToggleView, FollowersListView, FollowingListView, DeleteAccountView

urlpatterns=[
    path('login/',LoginVieW.as_view()),
    path('login/refresh/',LoginRefreshView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('signup/',CreateApiView.as_view()),
    path('verify/',VerifyApiView.as_view()),
    path('new-verify/',GetNewVerification.as_view()),
    path("change-user/",ChangeUserInformationView.as_view()),
    path("change-photo-user/",ChangePhotoUserView.as_view()),
    path("forgot-password/",ForgotPasswordView.as_view()),
    path("reset-password/",ResetPasswordView.as_view()),
    path("delete-account/",DeleteAccountView.as_view()),

    path('search/', UserSearchView.as_view()),
    path('<uuid:pk>/', UserDetailView.as_view()),
    path('<uuid:pk>/follow/', FollowToggleView.as_view()),
    path('<uuid:pk>/followers/', FollowersListView.as_view()),
    path('<uuid:pk>/following/', FollowingListView.as_view()),
]
