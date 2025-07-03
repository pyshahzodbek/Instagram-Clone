from django.urls import path
from .serializers import SignUpSerializers
from .views import CreateApiView


urlpatterns=[
    path('signup/',CreateApiView.as_view())
]