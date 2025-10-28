from rest_framework import serializers
from users.models import CustomUserModel,UserProfile
import re
from django.contrib.auth.password_validation import validate_password

from users.services.otp_service import OTPService
from users.services.email_otp_service import EmailVerification



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
        return CustomUserModel.objects.create_email_user(email =validate_data['email'],password = validate_data['password'],verification_method='email' )



class VerifyEmailUserSerializer(serializers.ModelSerializer):
    otp = serializers.IntegerField(min_value=100000, max_value=999999,write_only = True)

    class Meta:
        model = CustomUserModel
        fields = ['email','otp']
        read_only_fields = ['is_active']
        extra_kwargs = {
            'email':{'required':True},
            'otp':{'required':True}
        }
   
    def validate_email(self,value):
        try:
            user = CustomUserModel.objects.get(email=value)
            if user.is_active:  # Check individual user's is_active
                raise serializers.ValidationError('User is already verified')
        except CustomUserModel.DoesNotExist:
            raise serializers.ValidationError('Email does not exist')
            
        return value
    
    def validate(self,data):
        email = data.get('email')
        user_otp = data.get('otp')
        

        if email and user_otp:
            service = EmailVerification.verify_otp(email,user_otp)
            if service['status'] != 'valid':
                raise serializers.ValidationError(service['message'])
        
        return data
    def get_instance(self,validated_data):
        email = validated_data.get('email')
        user = CustomUserModel.objects.get(email = email)
        return user
    
    def update(self,instance,validated_data):
        validated_data.pop('otp', None)
        
        
        instance.is_active = True
        instance.save()
        return instance

            
    
class PhoneSendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    
    def validate_phone_number(self, value):
        if CustomUserModel.objects.filter(phone_number = value).exists():
            raise serializers.ValidationError('phone_number already exists')
        
        return value

class PhoneVerifyRegisterSerializer(serializers.ModelSerializer):
    otp = serializers.IntegerField(min_value=1000, max_value=9999,write_only = True)
    
    class Meta:
        model = CustomUserModel
        fields = ['phone_number', 'otp']
        extra_kwargs = {
            'phone_number': {'required':True}
        }

    def validate_phone_number(self, value):
        if CustomUserModel.objects.filter(phone_number = value).exists():
            raise serializers.ValidationError('phone_number already exists')
        
        return value
    
    def validate(self, data):
        phone = data['phone_number']
        user_input_otp = data['otp']

        if phone and user_input_otp:
            result = OTPService.verify_otp(phone,user_input_otp)
            if result['status'] != 'valid':

                raise serializers.ValidationError(result['message'])

        return data
    def create(self,validate_data):
        return CustomUserModel.objects.create_phone_user(phone_number =validate_data['phone_number'],is_active = True,verification_method = 'phone')

class OTPVerificationSerializer(serializers.Serializer):
   
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.IntegerField(min_value=1000, max_value=9999)

    class Meta:
        model = CustomUserModel
        fields = ['phone_number']
        read_only_fields = ['joined_at', 'is_active', 'is_admin']


# updating email/phone which was not used in time of registration.
class UpdateContactInfoSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(required =False,allow_blank =True)
    phone_number = serializers.CharField(required =False,allow_blank =True)

    class Meta:
        model = CustomUserModel
        fields = ['email','phone_number']

    
            
    def get_verification_method(self):
        if not self.instance:
            raise serializers.ValidationError("User instance required")
        
        return self.instance.verification_method
    
    def validate_email(self,value): # the email should be unique

        
        if self.get_verification_method() == 'email':
            
            if value:
                raise serializers.ValidationError("would not take email")
        else:

            if CustomUserModel.objects.filter(email = value).exists():
                raise serializers.ValidationError("the {value} existed with other account.")
        return value

    def validate_phone_number(self,value): # the phone should be unique
         
        if self.get_verification_method() == 'phone':
            
            if value:
                raise serializers.ValidationError("would not take phone")
        else:

            if CustomUserModel.objects.filter(phone_number = value).exists():
                raise serializers.ValidationError("the {value} existed with other account.")
            
        return value

    
    def validate(self,data):
        email = data.get('email')
        phone = data.get('phone_number')
        if email and phone:
            raise serializers.ValidationError("Cannot be both")
        
        if not email and not phone:
            raise serializers.ValidationError("Both Cannot be empty")
        
        return data
    
    def update(self,instance,validated_data):
        email = validated_data.get('email')
        phone_number = validated_data.get('phone_number')
        if email:
            instance.email = email
        if phone_number:
            instance.phone_number = phone_number
        instance.save()
        return instance
        
        

class UserProfileSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = UserProfile
        fields = ['first_name','last_name','dob','profile_picture','bio','website','location']



    
# class EndUsers_LogInfo_Serials(serializers.ModelSerializer):
#     class Meta:
#         model = EndUsers_LogInfo
#         fields = ['first_name','last_name','email','phonenumber']
#         #read_only_fields = ['users']

#     def validate(self, data):
#         email = data.get('email')
#         phonenumber = data.get('phonenumber')
#         if not email or not phonenumber:
#             raise serializers.ValidationEroor("Email or Phone Number is Mendetory")
#         return data

#     # def create(self, *args, **kwargs):
#     #     if self.email or self.phonenumber:
#     #         EndUsers_LogInfo.objects.create(**kwargs)
#     #     else:
#     #         raise serializers.ValidationError("please put phonenumber or email")
#     #     return EndUsers_LogInfo
# #from users.models import EndUsers_LogInfo
