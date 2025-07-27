from django.urls import path
from .serializers import SignUpSerializers
from .views import CreateApiView,VerifyApiView,GetNewVerification,ChangeUserInformationView,\
    ChangePhotoUserView,LoginVieW


urlpatterns=[
    path('login/',LoginVieW.as_view()),
    path('signup/',CreateApiView.as_view()),
    path('verify/',VerifyApiView.as_view()),
    path('new-verify/',GetNewVerification.as_view()),
    path("change-user/",ChangeUserInformationView.as_view()),
    path("change-photo-user/",ChangePhotoUserView.as_view()),
]