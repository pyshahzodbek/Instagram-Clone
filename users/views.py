from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.unitily import send_email, check_email_or_phone
from .serializers import SignUpSerializers, ChangeUserInformation, ChangePhotoSerializers, LoginSerializers, \
    LoginRefreshSerializers, LogoutSerializers, ForgotPasswordSerializer, ResetPasswordSerializers
from .models import Users, NEWS, CODE_VEFIRED, VIA_EMAIL,VIA_PHONE


class CreateApiView(CreateAPIView):
    queryset = Users.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignUpSerializers

class VerifyApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user=request.user
        code=request.data.get('code')

        self.check_verify(user,code)
        return Response(
            data={
                "success":True,
                'auth_status':user.auth_status,
                'access':user.token()['access'],
                'refresh_token':user.token()['refresh_token']
             }
        )
    @staticmethod
    def check_verify(user,code):
        verifies=user.verify_code.filter(expiration_time__gte=datetime.now(),code=code,is_confirmed=False)
        if not verifies.exists():
            data={
                "success":False,
                'message':'Kod xato yoki muddati tugagan!'
            }
            raise ValidationError(data)
        else:
            verifies.update(is_confirmed=True)

        if user.auth_status==NEWS:
            user.auth_status=CODE_VEFIRED

            user.save()
        return True


class GetNewVerification(APIView):

    def get(self,request,*args,**kwargs):
        user=request.user

        self.check_verification(user)

        if user.auth_type==VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type==VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
        else:
            data={
                'message':"Sizning tasdiqlash kodingiz hali yaroqli."
            }
            raise ValidationError(data)

        return Response(
            data={
                'success':True,
                'message':"Siznig tasdiqlash kodingiz qayta junatildi"
            }
        )


    @staticmethod
    def check_verification(user):
        verifies=user.verify_code.filter(expiration_time__gte=datetime.now(),is_confirmed=False)
        if verifies.exists():
                data={
                    'message':"Sizning tasdiqlash kodingiz hali yaroqli."
                }
                raise ValidationError(data)


class ChangeUserInformationView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangeUserInformation
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user
    def update(self, request,*args,**kwargs):
        super(ChangeUserInformationView,self).update(request,*args,**kwargs)
        data={
                "success":True,
                "message":"Malumotlar muvaffaqiyatli o'zgartirildi",
                "auth_status":self.request.user.auth_status
            }
        return Response(data,status=200)

    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).partial_update(request, *args, **kwargs)
        data = {
            "success": True,
            "message": "Malumotlar muvaffaqiyatli o'zgartirildi",
            "auth_status": self.request.user.auth_status        }
        return Response(data, status=200)

class ChangePhotoUserView(APIView):
    permission_classes = [IsAuthenticated,]


    def put(self,request,*args,**kwargs):
        serializer=ChangePhotoSerializers(data=request.data)
        if serializer.is_valid():
            user=request.user
            serializer.update(user,serializer.validated_data)
            return Response({
                "message":"Rasm muvafaqiyatli uzgartirildi"
            } ,status=200)
        return Response(
            serializer.errors,status=400
        )

class LoginVieW(TokenObtainPairView):
    serializer_class=LoginSerializers

class LoginRefreshView(TokenRefreshView):
    serializer_class = LoginRefreshSerializers


class LogoutView(APIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = LogoutSerializers
    def post(self,request,*args,**kwargs):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token=self.request.data["refresh"]
            token=RefreshToken(refresh_token)
            token.blacklist()
            data={
                "success":True,
                "message":"You are logged out"
            }
            return Response(data,status=200)
        except TokenError:
            return Response(status=400)
#
# class ForgotPasswordView(APIView):
#     permission_classes = [AllowAny,]
#     serializers_class = ForgotPasswordSerializers
#     def post(self,request,*args,**kwargs):
#         serializer=self.serializers_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         email_or_phone=serializer.validated_data.get('email_or_phone')
#         user=serializer.validated_data.get('user')
#         if check_email_or_phone(email_or_phone)=="email":
#             code=user.create_verify_code(VIA_EMAIL)
#             send_email(email_or_phone,code)
#         elif check_email_or_phone(email_or_phone)=="phone":
#             code=user.create_verify_code(VIA_PHONE)
#             send_email(email_or_phone,code)
#         return Response({
#             "message":"Tasdiqlash parolingiz muvafaqiyatli yuborildi!"
#         },status=200)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny, ]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data.get('email_or_phone')
        user = serializer.validated_data.get('user')
        if check_email_or_phone(email_or_phone) == 'via_phone':
            code = user.create_verify_code(VIA_PHONE)
            print("tasdiqlash " + code)
            send_email(email_or_phone, code)
        elif check_email_or_phone(email_or_phone) == 'via_email':
            code = user.create_verify_code(VIA_EMAIL)
            print("tasdiqlash "+code)
            send_email(email_or_phone, code)

        return Response(
            {
                "success": True,
                'message': "Tasdiqlash kodi muvaffaqiyatli yuborildi",
                "access": user.token()['access'],
                "refresh": user.token()['refresh_token'],
                "user_status": user.auth_status,

            }, status=200
        )


class ResetPasswordView(UpdateAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = ResetPasswordSerializers
    http_method_names = ['put', 'patch']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response=super(ResetPasswordView,self).update(request,*args,**kwargs)
        try:
            user=Users.objects.get(id=response.data.get("id"))
        except ObjectDoesNotExist as e:
            raise NotFound(detail="User not found")
        return Response(
            {
                "success":True,
                "message":"Parolingiz muvafaqiyatli uzgartirildi!",
                "access":user.token()["access"],
                "refresh_token":user.token()["refresh_token"]
            }
        )




