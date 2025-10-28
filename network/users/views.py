from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from users.serializers import EmailRegistration_serializer,PhoneVerifyRegisterSerializer, UpdateContactInfoSerializer,UserProfileSerializer,VerifyEmailUserSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet,ModelViewSet
from rest_framework.decorators import api_view,permission_classes,action
from rest_framework.permissions import AllowAny,IsAuthenticated
import random
#import requests
import urllib.request
import urllib.parse

from users.throttles import EmailThrottle,PhoneThrottle,OTPThrottle
from users.services.otp_service import OTPService
from users.services.email_otp_service import EmailVerification

#jwt
from rest_framework_simplejwt.tokens import RefreshToken

#models
from users.models import UserProfile,CustomUserModel


class RegistrationView(ViewSet):
    permission_classes = [AllowAny]
    
    @action(detail =False,methods =['post'],throttle_classes=[EmailThrottle])
    def email(self,request):
        serializer = EmailRegistration_serializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()

           # token =RefreshToken.for_user(user)
            send_otp =EmailVerification.send_verification_code(user.email) # or user.email
            if send_otp['status'] == 'success':
                return Response({
                    'message': f'{user.username} created successfully. OTP sent to email.',
                    'user_id': user.id,
                    'email': user.email,
                    'otp':send_otp['otp']
                }, status=201)
            else:
                user.delete()
                return Response({'message': 'Verification service is unavailable'}, status=400)
        return Response(serializer.errors, status=400)
    
    @action(detail =False,methods =['post'],throttle_classes=[EmailThrottle])
    def verify_email(self,request):
        email = request.data.get('email')
        user_instance = CustomUserModel.objects.get(email=email)
        serializer = VerifyEmailUserSerializer(instance=user_instance,data = request.data)
        if serializer.is_valid():
            user_instance = serializer.get_instance(serializer.validated_data)
            updated_user = serializer.update(user_instance,serializer.validated_data)

            token =RefreshToken.for_user(updated_user)
            return self._success_response(updated_user.username,token)
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
            token =RefreshToken.for_user(user)

            return self._success_response(user.username,token)
        return Response(serializer.errors, status=400)
    
    def _success_response(self,username,token):
        
        return Response({
            'message': f'{username} registration successful',
            'access': str(token.access_token),  # ← Include access token!
            'refresh': str(token),
            
        }, status=201)
    
class ContactUpdateView(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False,methods=['get','patch'])
    def contact_update(self,request):
        user = request.user
        if request.method == 'PATCH':
            serializer = UpdateContactInfoSerializer(user,data = request.data,partial =True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Contact information updated successfully',
                    'data': serializer.data
                })
            return Response(serializer.errors, status=400)
        
        serializer = UpdateContactInfoSerializer(user)
        return Response(serializer.data)




########################################                 Login Views
class UserAuthenticateView(ViewSet):
    permission_classes = [AllowAny]


    @action(detail=False,methods=['post'])
    def email_login(self,request):

        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'errors':'Email and password Required'})
        
        try:
            user = CustomUserModel.objects.get(email = email)

            if user.verification_method == 'email':
                if user.check_password(password):
                    if user.is_active:
                        token =RefreshToken.for_user(user)
                        return Response({
                            'message': f'{user.username} registration successful',
                            'access': str(token.access_token),  # ← Include access token!
                            'refresh': str(token),
                        })
                    else:
                        return Response({'errors':'user is not active'},status=400)
                else:
                    return Response({'error': 'Invalid password'}, status=400)
            else:
                return Response({'error': 'Not an Email user'}, status=400)


        except CustomUserModel.DoesNotExist:
            return Response({'error': 'User not found'}, status=400)
                

    @action(detail=False, methods=['post'])#throttle_classes=[OTPThrottle]
    def send_otp(self, request):
       
        
        phone = request.data.get('phone_number')

        if not phone:
            return Response({'errors':'phone number Required'})

        try:
            user = CustomUserModel.objects.get(phone_number = phone)

            if user.verification_method == 'phone':
                
        
                otp = OTPService.generate_otp(phone)
                return Response(otp) # for now. change will be made in production
               
            else:
                return Response({'error': 'Not a phone User'}, status=400)
        except CustomUserModel.DoesNotExist:
            return Response({'error': 'User not found'}, status=400)
        
    @action(detail=False,methods=['post']) #throttle_classes=[PhoneThrottle]
    def phone(self,request):
        phone = request.data.get('phone_number')
        otp = request.data.get('otp')
        
        verify_result = OTPService.verify_otp(phone,otp)
        if verify_result['status'] == 'valid':
            
                 
            user = CustomUserModel.objects.get(phone_number = phone)

            token =RefreshToken.for_user(user)

            return Response({
                            'message': f'{user.username} registration successful',
                            'access': str(token.access_token),  # ← Include access token!
                            'refresh': str(token),
                        })
        return Response(verify_result['message'],status=400)



class ProfileView(ModelViewSet):
    
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch']


    def get_queryset(self):

        return UserProfile.objects.filter(user = self.request)
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    def perform_create(self, serializer):
    
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        
        serializer.save() 
# class LoginView(ViewSet):
#     permission_classes = [AllowAny]

#     @action()

# class EmailRegistrationAPI(APIView):

#     permission_classes = [AllowAny]
#     throttle_scope  = 'email_register'

#     def post(self,request):
#         serializer = EmailRegistration_serializer(data = request.data)
#         if serializer.is_valid():
#             user =serializer.save()

#             return Response({
#                 'message': 'User creation Sucessfull.',
#                 'user':{
#                     'id': user.id,
#                     'username': user.username
#                 }
#             }, status= status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # # Create your views here.
# # @api_view(['POST'])
# # @permission_classes([AllowAny])
# # def verify_user(request):
# #     phone_number = request.data.get('phonenumber')
# #     email = request.data.get('email')
# #     # if email:
        
# #     print(f"view:-> phone_number: {phone_number} and email: {email}")
# #     return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)


# # # def send_otp(phonenumber,otp):

 
# # # def sendSMS(apikey, numbers, sender, message):
# # #     data = urllib.parse.urlencode({apikey,numbers, message,sender})
# # #     data = data.encode('utf-8')
# # #     request = urllib.request.Request('https://api.textlocal.in/send/?')
# # #     f = urllib.request.urlopen(request, data)
# # #     fr = f.read()
# # #     return(fr)
    


    
   


# # class Registration(APIView):
# #     serializer_class = EndUsers_LogInfo_Serials
# #     queryset = EndUsers_LogInfo.objects.all()


# #     def post(self,request,*args,**kwargs):

# #         serilaizer_data = self.serializer_class(data = request.data)
# #         if serilaizer_data.is_valid():
# #             phone_number = serilaizer_data.validated_data['phonenumber']

# #             # generate otp
# #             otp = random.randint(1000,9999)

# #             # resp = sendSMS('NjU2NzRjMzc2ZjM3NDgzNjYyNTY0ZjQ5NmY2NjU0NDQ=', '917001065323', 'Jims Autos', 'This is your message')
# #             print (f"otp for verification: {otp}" )
# #             return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
# #         return Response(serilaizer_data.errors, status=status.HTTP_400_BAD_REQUEST)
    
  



# # # def registration(request):
   
        
# # #     if request.method == 'POST':
# # #         formSerializer = EndUsers_LogInfo_Serials(data= request.data)
        
# # #         if formSerializer.is_valid():
# # #             formSerializer.save()
# # #             return re



# # # class Registration(CreateAPIView):
# # #     serializer_class = EndUsers_LogInfo_Serials
# # #     queryset = EndUsers_LogInfo.objects.all()
   
# # #     # def perform_create(self, serializer_class):
# # #     #     serializer_class.save(users = self.request.user)
    

# # #     def post(self, request, *args, **kwargs):   # get login user automaticly -- check
# # #         serializer = self.get_serializer(data=request.data)
# # #         print(serializer)
# # #         serializer.is_valid(raise_exception=True)
# # #         self.perform_create(serializer)
# # #         headers = self.get_success_headers(serializer.data)
# # #         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
   


# # def loginView(request):
# #     pass

    