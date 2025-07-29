from django.urls import path
from .serializers import SignUpSerializers
from .views import CreateApiView, VerifyApiView, GetNewVerification, ChangeUserInformationView, \
    ChangePhotoUserView, LoginVieW, LoginRefreshView, LogoutView, ResetPasswordView, ForgotPasswordView

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
]