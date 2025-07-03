from rest_framework import  serializers

from shared.unitily import check_email_or_phone
from .models import UserConfermation,Users,VIA_EMAIL,VIA_PHONE,CODE_VEFIRED,NEWS,DONE,PHOTO_STEP
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

    def validate(self,data):
        super(SignUpSerializers,self).validate(data)
        data=self.auth_validate(data)
        return data




    @staticmethod
    def auth_validate(data):
        print(data)
        user_input=str(data.get('email_phone_number')).lower()
        input_type=check_email_or_phone(user_input)
        print("user input",user_input)
        print('input_type',input_type)

        return data
