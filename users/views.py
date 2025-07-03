from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .serializers import SignUpSerializers
from .models import Users

class CreateApiView(CreateAPIView):
    queryset = Users.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializers

