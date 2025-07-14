from datetime import datetime

from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SignUpSerializers
from .models import Users, NEWS,CODE_VEFIRED


class CreateApiView(CreateAPIView):
    queryset = Users.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializers

class VerifyApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        print(f"user: {request.user}")
        print(f"code: {request.data.get('code')}")
        user=request.user
        code=request.data.get('code')

        self.check_verify(user,code)
        return Response(
            data={
                "success":True,
                'auth_status':user.auth_status,
                'access':user.token()['access'],
                'refresh_token':user.token()['refresh']
             }
        )
    @staticmethod
    def check_verify(user,code):
        verifies=user.verify_code.filter(expiration_time__gte=datetime.now(),code=code,is_confirned=False)
        if not verifies.exists():
            data={
                "success":False,
                'message':'Kod xato yoki muddati tugagan!'
            }
            raise ValidationError(data)
        else:
            verifies.update(is_confirned=True)

        if user.auth_status==NEWS:
            user.auth_status=CODE_VEFIRED

            user.save()
        return True

