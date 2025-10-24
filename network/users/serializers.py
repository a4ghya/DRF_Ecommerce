from rest_framework import serializers
from users.models import EndUsers_LogInfo, Sellers_LogInfo, CustomUserModel
import re
from django.contrib.auth.password_validation import validate_password
#from django.contrib.auth.models import User
# class UserSerials(serializers.Modelserializer):
#     class Meta:
#         model = User
#         fields = ['username', 'password']

class EmailRegistration_serializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length = 8,max_length = 50, write_only = True, validators = [validate_password])
    confirm_password = serializers.CharField(min_length = 8,max_length = 50, write_only = True)
    # otp = serializers. IntegerField(max_value = 9999, min_value = 0001)

    class Meta:
        model = CustomUserModel
        fields = ['email','password','confirm_password']
        extra_kwargs = {
            'email':{'required': True}
        }

    def validate_email(self,value):
       
        
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.fullmatch(email_pattern, value):
            raise serializers.ValidationError('email format did not match')
        if CustomUserModel.objects.filter(email = value).exists():
            raise serializers.ValidationError('email already exists')
        return value
    
    
    def validate(self,data):
       
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('password did not match')
        
        return data
    def create(self,validate_data):
        return CustomUserModel.objects.create_email_user(email =validate_data['email'],password = validate_data['password'] )





class OTPVerificationSerializer(serializers.Serializer):
   
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.IntegerField(min_value=1000, max_value=9999)

    class Meta:
        model = CustomUserModel
        fields = ['phone_number']
        read_only_fields = ['joined_at', 'is_active', 'is_admin']

class EndUsers_LogInfo_Serials(serializers.ModelSerializer):
    class Meta:
        model = EndUsers_LogInfo
        fields = ['first_name','last_name','email','phonenumber']
        #read_only_fields = ['users']

    def validate(self, data):
        email = data.get('email')
        phonenumber = data.get('phonenumber')
        if not email or not phonenumber:
            raise serializers.ValidationEroor("Email or Phone Number is Mendetory")
        return data

    # def create(self, *args, **kwargs):
    #     if self.email or self.phonenumber:
    #         EndUsers_LogInfo.objects.create(**kwargs)
    #     else:
    #         raise serializers.ValidationError("please put phonenumber or email")
    #     return EndUsers_LogInfo
#from users.models import EndUsers_LogInfo
