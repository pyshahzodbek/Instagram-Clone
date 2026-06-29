from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from rest_framework import permissions, generics, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.unitily import send_email, check_email_or_phone
from .serializers import SignUpSerializers, ChangeUserInformation, ChangePhotoSerializers, LoginSerializers, \
    LoginRefreshSerializers, LogoutSerializers, ForgotPasswordSerializer, ResetPasswordSerializers, \
    UserSearchSerializer, FollowSerializer, DeleteAccountSerializer
from .models import Users, Follow, NEWS, CODE_VEFIRED, VIA_EMAIL,VIA_PHONE


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

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.user
                if user.is_staff:
                    from django.contrib.auth import login
                    login(request, user)
        return response

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


class UserSearchView(ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        q = self.request.query_params.get('q', '')
        if q:
            return Users.objects.filter(
                Q(username__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)
            ).filter(auth_status__in=['DONE', 'PHOTO_STEP'])[:20]
        return Users.objects.none()


class UserDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            user = Users.objects.get(id=pk, auth_status__in=['DONE', 'PHOTO_STEP'])
        except Users.DoesNotExist:
            raise NotFound("User not found")

        serializer = UserSearchSerializer(user, context={'request': request})
        from post.serializers import PostSerializers
        posts = user.posts.all().order_by('-created_time')
        post_serializer = PostSerializers(posts, many=True, context={'request': request})

        is_following = False
        if request.user.is_authenticated:
            is_following = Follow.objects.filter(follower=request.user, following=user).exists()

        return Response({
            "user": serializer.data,
            "posts": post_serializer.data,
            "is_following": is_following
        })


class FollowToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            user_to_follow = Users.objects.get(id=pk)
        except Users.DoesNotExist:
            raise NotFound("User not found")

        if request.user == user_to_follow:
            raise ValidationError("O'zingizni kuzata olmaysiz")

        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )

        if not created:
            follow.delete()
            return Response({"following": False}, status=200)

        return Response({"following": True}, status=201)


class FollowersListView(ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        try:
            user = Users.objects.get(id=self.kwargs['pk'])
        except Users.DoesNotExist:
            raise NotFound("User not found")
        return Users.objects.filter(following__following=user).distinct()


class FollowingListView(ListAPIView):
    serializer_class = UserSearchSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        try:
            user = Users.objects.get(id=self.kwargs['pk'])
        except Users.DoesNotExist:
            raise NotFound("User not found")
        return Users.objects.filter(followers__follower=user).distinct()


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeleteAccountSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.is_active = False
        user.save()
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return Response(
            {"success": True, "message": "Hisob muvaffaqiyatli o'chirildi"},
            status=status.HTTP_200_OK
        )