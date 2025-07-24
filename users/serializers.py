from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework import  serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from shared.unitily import check_email_or_phone, send_email, send_phone_code, check_auth_type
from .models import UserConfirmation,Users,VIA_EMAIL,VIA_PHONE,CODE_VEFIRED,NEWS,DONE,PHOTO_STEP
from rest_framework import exceptions
from django.db.models import Q
from  rest_framework.exceptions import ValidationError



class SignUpSerializers(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    # auth_type=serializers.CharField(read_only=True,required=False)
    def __init__(self,*args,**kwargs):
        super(SignUpSerializers,self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model=Users
        fields=[
            'id',
            'auth_type',
            'auth_status'
        ]
        extra_kwargs={
            'auth_type':{'read_only':True,'required':False},
            'auth_status':{'read_only':True,'required':False}
        }

    def create(self, validated_data):
      user= super(SignUpSerializers,self).create(validated_data)
      if user.auth_type==VIA_EMAIL:
          code=user.create_verify_code(VIA_EMAIL)
          send_email(user.email,code)
      elif user.auth_type==VIA_PHONE:
          code=user.create_verify_code(VIA_PHONE)
          # send_phone_code(user.phone_number,code)
          send_email(user.phone_number,code)
      user.save()
      return user



    def validate(self,data):
        super(SignUpSerializers,self).validate(data)
        data=self.auth_validate(data)
        return data




    @staticmethod
    def auth_validate(data):

        user_input=str(data.get('email_phone_number')).lower()
        input_type=check_email_or_phone(user_input)
        if input_type==VIA_EMAIL:
            data={
                'email':user_input,
                'auth_type':VIA_EMAIL,
            }
        elif input_type==VIA_PHONE:
            data={
                'phone_number':user_input,
                'auth_type':VIA_PHONE,
            }
        else:
            data={
                "success":False,
                'message':'invalid email or phone number'
            }
            raise ValidationError(data)

        return data


    def validate_email_phone_number(self,value):
        value=value.lower()
        if value and Users.objects.filter(email=value).exists():
            data={
                "success":False,
                'message':'Bu email malumotlar bazasida mavjud!'
            }
            raise ValidationError(data)
        elif value and Users.objects.filter(phone_number=value).exists():
            data={
                "success":False,
                'message':'Bu telefon raqam malumotlar bazasida mavjud!'
            }
            raise ValidationError(data)
        return value

    def to_representation(self, instance):
        data = super(SignUpSerializers, self).to_representation(instance)
        data.update(instance.token())

        return data

class ChangeUserInformation(serializers.Serializer):
    first_name=serializers.CharField(write_only=True,required=True)
    last_name=serializers.CharField(write_only=True,required=True)
    username=serializers.CharField(write_only=True,required=True)
    password=serializers.CharField(write_only=True,required=True)
    confirm_password=serializers.CharField(write_only=True,required=True)

    def validate(self,data):
        password=data.get('password',None)
        confirm_password=data.get('confirm_password',None)

        if password!=confirm_password:
             raise ValidationError(
                 {
                     "message":"Kiritgan parollaringiz bir xil emas!"
                 }
             )
        if password:
            validate_password(password)
            validate_password(confirm_password)

        return data
    def validate_username(self,username):

        if len(username)<5 or len(username)>30:
            raise ValidationError(
                {
                    "message":"Kiritgan username 5 ta belgidan kam yoki 30 ta belgidan ko'p bo'lishi mumkin emas!"
                }
            )

        if username.isdigit():
            raise ValidationError(
                {
                    "message":"Kiritilgan username faqat harflardan iborat bo'lishi kerak!"
                }
            )
        return username


    def validate_first_name(self,first_name):
        if len(first_name)<5 or len(first_name)>30:
            raise ValidationError(
                {
                    "message":"Kiritilgan ism 5 ta belgidan kam yoki 30 ta belgidan ko'p bo'lishi mumkin emas!"
                }
            )
        if first_name.isdigit():
            raise ValidationError(
                {
                    "message":"Kiritilgan ism faqat harflardan iborat bo'lishi kerak!"
                }
            )
        return first_name
    def validate_last_name(self,last_name):
        if len(last_name)<5 or len(last_name)>30:
            raise ValidationError(
                {
                    "message":"Kiritilgan familiya 5 ta belgidan kam yoki 30 ta belgidan ko'p bo'lishi mumkin emas!"
                }
            )
        if last_name.isdigit():
            raise ValidationError(
                {
                    "message":"Kiritilgan familiya faqat harflardan iborat bo'lishi kerak!"
                }
            )
        return last_name

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        password=validated_data.get("password",None)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VEFIRED:
            instance.auth_status = DONE
        instance.save()
        return instance


class ChangePhotoSerializers(serializers.Serializer):
    photo=serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=('jpg','jpeg','png','heic','heif'))])

    def update(self, instance, validated_data):
        photo=validated_data.get('photo')
        if photo:
            instance.photo=photo
            instance.auth_status=PHOTO_STEP
            instance.save()
        return instance



class LoginSerializers(TokenObtainPairSerializer):
   def __init__(self,*args,**kwargs):
       super(LoginSerializers,self).__init__(*args,**kwargs)
       self.fields["user_input"]=serializers.CharField(required=True)
       self.fields["username"]=serializers.CharField(required=False,read_only=True)

   def auth_validate(self,data):
       user_input=data.get('user_input')
       if check_auth_type(user_input)=="username":
           username=user_input
       elif check_auth_type(user_input)=="email":
           user=Users.objects.get(email__iaxact=user_input)
           username=user.username
       elif check_auth_type(user_input)=='phone':
           user=Users.objects.get(phone_number=user_input)
           username=user.username
       else:
           data={
               "success":False,
               "message":"Siz email, username, telefon raqam kiritishingiz kerak!"

           }
           raise ValidationError(data)

       authentication_kwargs = {
           self.username_field: username,
           'password': data['password']
       }








