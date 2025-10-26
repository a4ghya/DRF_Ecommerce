from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from users.forms import EndUserForm
from users.models import EndUsers_LogInfo
from users.serializers import EmailRegistration_serializer,PhoneVerifyRegisterSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import api_view,permission_classes,action
from rest_framework.permissions import AllowAny
import random
#import requests
import urllib.request
import urllib.parse

from users.throttles import EmailThrottle,PhoneThrottle,OTPThrottle
from users.services.otp_service import OTPService

#jwt
from rest_framework_simplejwt.tokens import RefreshToken


class RegistrationView(ViewSet):
    permission_classes = [AllowAny]
    
    @action(detail =False,methods =['post'],throttle_classes=[EmailThrottle])
    def email(self,request):
        serializer = EmailRegistration_serializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            return self._success_response(user.username)
        return Response(serializer.errors, status=400)
    
    @action(detail=False, methods=['post'],throttle_classes=[OTPThrottle])
    def send_otp(self, request):
       
        # OTP sending logic
        phone = request.data.get('phone_number')
        if phone:
            otp = OTPService.generate_otp(phone)
            return Response(otp)
        return Response({'error': 'Phone number required'}, status=400)
        
    @action(detail=False,methods=['post'],throttle_classes=[PhoneThrottle])
    def phone(self,request):
        serializer = PhoneVerifyRegisterSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            return self._success_response(user.username)
        return Response(serializer.errors, status=400)
    
    def _success_response(self,username):
        
        return Response({
            'message': f'{username} registration successful',
            
        }, status=201)


class EmailRegistrationAPI(APIView):

    permission_classes = [AllowAny]
    throttle_scope  = 'email_register'

    def post(self,request):
        serializer = EmailRegistration_serializer(data = request.data)
        if serializer.is_valid():
            user =serializer.save()

            return Response({
                'message': 'User creation Sucessfull.',
                'user':{
                    'id': user.id,
                    'username': user.username
                }
            }, status= status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # Create your views here.
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def verify_user(request):
#     phone_number = request.data.get('phonenumber')
#     email = request.data.get('email')
#     # if email:
        
#     print(f"view:-> phone_number: {phone_number} and email: {email}")
#     return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)


# # def send_otp(phonenumber,otp):

 
# # def sendSMS(apikey, numbers, sender, message):
# #     data = urllib.parse.urlencode({apikey,numbers, message,sender})
# #     data = data.encode('utf-8')
# #     request = urllib.request.Request('https://api.textlocal.in/send/?')
# #     f = urllib.request.urlopen(request, data)
# #     fr = f.read()
# #     return(fr)
    


    
   


# class Registration(APIView):
#     serializer_class = EndUsers_LogInfo_Serials
#     queryset = EndUsers_LogInfo.objects.all()


#     def post(self,request,*args,**kwargs):

#         serilaizer_data = self.serializer_class(data = request.data)
#         if serilaizer_data.is_valid():
#             phone_number = serilaizer_data.validated_data['phonenumber']

#             # generate otp
#             otp = random.randint(1000,9999)

#             # resp = sendSMS('NjU2NzRjMzc2ZjM3NDgzNjYyNTY0ZjQ5NmY2NjU0NDQ=', '917001065323', 'Jims Autos', 'This is your message')
#             print (f"otp for verification: {otp}" )
#             return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
#         return Response(serilaizer_data.errors, status=status.HTTP_400_BAD_REQUEST)
    
  



# # def registration(request):
   
        
# #     if request.method == 'POST':
# #         formSerializer = EndUsers_LogInfo_Serials(data= request.data)
        
# #         if formSerializer.is_valid():
# #             formSerializer.save()
# #             return re



# # class Registration(CreateAPIView):
# #     serializer_class = EndUsers_LogInfo_Serials
# #     queryset = EndUsers_LogInfo.objects.all()
   
# #     # def perform_create(self, serializer_class):
# #     #     serializer_class.save(users = self.request.user)
    

# #     def post(self, request, *args, **kwargs):   # get login user automaticly -- check
# #         serializer = self.get_serializer(data=request.data)
# #         print(serializer)
# #         serializer.is_valid(raise_exception=True)
# #         self.perform_create(serializer)
# #         headers = self.get_success_headers(serializer.data)
# #         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
   


# def loginView(request):
#     pass

    