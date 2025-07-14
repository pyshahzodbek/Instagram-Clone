from rest_framework import  serializers
from shared.unitily import check_email_or_phone, send_email, send_phone_code
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
