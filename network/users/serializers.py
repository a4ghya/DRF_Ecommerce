from rest_framework import serializers
from users.models import EndUsers_LogInfo, Sellers_LogInfo
from django.contrib.auth.models import User
# class UserSerials(serializers.Modelserializer):
#     class Meta:
#         model = User
#         fields = ['username', 'password']

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
