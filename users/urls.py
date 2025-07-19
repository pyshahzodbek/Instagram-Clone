from django.urls import path
from .serializers import SignUpSerializers
from .views import CreateApiView,VerifyApiView,GetNewVerification


urlpatterns=[
    path('signup/',CreateApiView.as_view()),
    path('verify/',VerifyApiView.as_view()),
    path('new-verify/',GetNewVerification.as_view()),
]