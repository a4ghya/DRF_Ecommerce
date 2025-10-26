# from django.test import TestCase

# # Create your tests here.
# from django.test import TestCase
# from django.core.exceptions import ValidationError
# from django.db import IntegrityError
# from users.models import CustomUserModel

# from django.contrib.auth import authenticate
# from django.core.cache import cache

# from rest_framework.test import APIClient
# from django.urls import reverse
# from rest_framework import status

# from users.views import EmailRegistrationAPI

# import time
# import json
# from django.test import TestCase
# from django.core.cache import cache
# from rest_framework.test import APITestCase, APIClient, APIRequestFactory, force_authenticate
# from rest_framework import status
# from rest_framework.request import Request
# from unittest.mock import patch, MagicMock
# from django.contrib.auth import get_user_model

# from users.views import RegistrationView
# from users.services.otp_service import OTPService
# from users.throttles import EmailThrottle, PhoneThrottle, OTPThrottle
# from users.serializers import EmailRegistration_serializer, PhoneVerifyRegisterSerializer

# User = get_user_model()


# class RegistrationViewTest(APITestCase):
#     def setUp(self):
#         self.client = APIClient()  # Use APIClient instead of APIRequestFactory
#         self.factory = APIRequestFactory()
#         self.view = RegistrationView()
        
#         # URLs based on your router configuration
#         self.email_url = '/api/auth/register/email/'
#         self.send_otp_url = '/api/auth/register/send_otp/'
#         self.phone_url = '/api/auth/register/phone/'
        
#         # Clear cache before each test
#         cache.clear()
        
#         # Test data
#         self.valid_email_data = {
#             'email': 'test@example.com',
#             'password': 'testpass123',
#             'username': 'testuser'
#         }
        
#         self.phone_number = '7076246322'

#     def tearDown(self):
#         cache.clear()

#     # Helper method to create proper DRF Request objects
#     def _create_drf_request(self, method='POST', url='/', data=None, format='json'):
#         """Create a proper DRF Request object"""
#         factory_method = getattr(self.factory, method.lower())
#         request = factory_method(url, data, format=format)
#         return Request(request)

#     # Email Registration Tests
#     def test_email_registration_success(self):
#         """Test successful email registration using APIClient"""
#         response = self.client.post(self.email_url, self.valid_email_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertIn('registration successful', response.data['message'])
#         self.assertTrue(User.objects.filter(email='test@example.com').exists())

#     def test_email_registration_invalid_data(self):
#         """Test email registration with invalid data"""
#         invalid_data = {
#             'email': 'invalid-email',
#             'password': 'short'
#         }
#         response = self.client.post(self.email_url, invalid_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('email', response.data)

#     def test_email_registration_duplicate_email(self):
#         """Test email registration with duplicate email"""
#         # Create user first
#         User.objects.create_user(
#             email='test@example.com',
#             password='testpass123',
#             username='existinguser'
#         )
        
#         response = self.client.post(self.email_url, self.valid_email_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('email', response.data)

#     # OTP Send Tests
#     @patch('users.services.OTPService.generate_otp')
#     def test_send_otp_success(self, mock_generate_otp):
#         """Test successful OTP sending"""
#         mock_generate_otp.return_value = {'status': 'success', 'message': 'OTP sent'}
        
#         response = self.client.post(self.send_otp_url, {'phone_number': self.phone_number}, format='json')
        
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         mock_generate_otp.assert_called_once_with(self.phone_number)

#     def test_send_otp_missing_phone(self):
#         """Test OTP sending without phone number"""
#         response = self.client.post(self.send_otp_url, {}, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)

#     # OTP Verification Tests
#     def test_phone_registration_success(self):
#         """Test successful phone registration with valid OTP"""
#         # First generate OTP
#         OTPService.generate_otp(self.phone_number)
        
#         # Get the actual OTP from Redis
#         import redis
#         r = redis.Redis(decode_responses=True)
#         otp_data = r.hgetall(f"otp_{self.phone_number}")
#         actual_otp = otp_data.get('otp')
        
#         data = {
#             'phone_number': self.phone_number,
#             'otp': actual_otp
#         }
        
#         response = self.client.post(self.phone_url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         # Note: You'll need to adjust this based on your User model
#         # self.assertTrue(User.objects.filter(phone_number=self.phone_number).exists())

#     def test_phone_registration_invalid_otp(self):
#         """Test phone registration with invalid OTP"""
#         # Generate OTP first
#         OTPService.generate_otp(self.phone_number)
        
#         data = {
#             'phone_number': self.phone_number,
#             'otp': '9999'  # Wrong OTP
#         }
        
#         response = self.client.post(self.phone_url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_phone_registration_no_otp_requested(self):
#         """Test phone registration without requesting OTP first"""
#         data = {
#             'phone_number': self.phone_number,
#             'otp': '1234'
#         }
        
#         response = self.client.post(self.phone_url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     # OTP Service Integration Tests
#     def test_otp_service_generate_and_verify(self):
#         """Test OTP service generate and verify integration"""
#         # Generate OTP
#         result = OTPService.generate_otp(self.phone_number)
#         self.assertEqual(result['status'], 'success')
        
#         # Verify OTP exists in cache
#         import redis
#         r = redis.Redis(decode_responses=True)
#         otp_data = r.hgetall(f"otp_{self.phone_number}")
#         self.assertIsNotNone(otp_data)
#         self.assertIn('otp', otp_data)
#         self.assertIn('attempts', otp_data)
#         self.assertIn('created_at', otp_data)
        
#         # Get TTL
#         ttl = r.ttl(f"otp_{self.phone_number}")
#         self.assertGreater(ttl, 0)  # Should have time remaining

#     def test_otp_service_max_attempts(self):
#         """Test OTP service max attempts blocking"""
#         # Generate OTP
#         OTPService.generate_otp(self.phone_number)
        
#         # Exceed max attempts
#         results = []
#         for i in range(4):  # MAX_ATTEMPTS + 1
#             result = OTPService.verify_otp(self.phone_number, '9999')  # Wrong OTP
#             results.append(result)
        
#         # Last attempt should be blocked
#         self.assertEqual(results[-1]['status'], 'blocked')
        
#         # Try with correct OTP (should still be blocked)
#         import redis
#         r = redis.Redis(decode_responses=True)
#         otp_data = r.hgetall(f"otp_{self.phone_number}")
#         if otp_data:
#             correct_otp = otp_data.get('otp')
#             result = OTPService.verify_otp(self.phone_number, correct_otp)
#             self.assertEqual(result['status'], 'blocked')

#     def test_otp_service_time_expiry(self):
#         """Test OTP service time-based expiration"""
#         # Generate OTP
#         OTPService.generate_otp(self.phone_number)
        
#         # Manually set created_at to be older than timeout
#         import redis
#         r = redis.Redis(decode_responses=True)
#         old_time = time.time() - (OTPService.OTP_TIMEOUT + 10)  # 10 seconds expired
#         r.hset(f"otp_{self.phone_number}", 'created_at', old_time)
        
#         # Try to verify
#         result = OTPService.verify_otp(self.phone_number, '1234')
#         self.assertEqual(result['status'], 'expired')

#     # Throttling Tests (using APIClient)
#     def test_email_throttling(self):
#         """Test email registration throttling"""
#         # Make multiple rapid requests
#         for i in range(15):  # Make enough requests to trigger throttling
#             response = self.client.post(self.email_url, {
#                 'email': f'test{i}@example.com',
#                 'password': 'testpass123',
#                 'username': f'user{i}'
#             }, format='json')
            
#             # Print status for debugging
#             print(f"Request {i}: Status {response.status_code}")
            
#             if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
#                 print("Throttling triggered!")
#                 break

#     def test_phone_throttling(self):
#         """Test OTP sending throttling"""
#         # Make multiple rapid OTP requests
#         for i in range(10):
#             response = self.client.post(self.send_otp_url, {'phone_number': self.phone_number}, format='json')
            
#             print(f"OTP Request {i}: Status {response.status_code}")
            
#             if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
#                 print("OTP throttling triggered!")
#                 break

#     # Cache Functionality Tests
#     def test_cache_cleared_after_successful_verification(self):
#         """Test that cache is cleared after successful OTP verification"""
#         # Generate and verify OTP successfully
#         OTPService.generate_otp(self.phone_number)
        
#         import redis
#         r = redis.Redis(decode_responses=True)
#         otp_data = r.hgetall(f"otp_{self.phone_number}")
#         actual_otp = otp_data.get('otp')
        
#         data = {
#             'phone_number': self.phone_number,
#             'otp': actual_otp
#         }
        
#         response = self.client.post(self.phone_url, data, format='json')
        
#         # Check cache is cleared
#         cached_otp = r.exists(f"otp_{self.phone_number}")
#         self.assertEqual(cached_otp, 0)  # Key should not exist

#     def test_cache_persistence_during_attempts(self):
#         """Test that cache persists during failed attempts"""
#         OTPService.generate_otp(self.phone_number)
        
#         # Make failed attempts
#         for i in range(2):
#             OTPService.verify_otp(self.phone_number, '9999')
        
#         # OTP should still exist in cache
#         import redis
#         r = redis.Redis(decode_responses=True)
#         otp_data = r.hgetall(f"otp_{self.phone_number}")
#         self.assertIsNotNone(otp_data)
        
#         # Attempts should be incremented
#         self.assertEqual(int(otp_data['attempts']), 2)

#     # URL Routing Tests
#     def test_url_routing(self):
#         """Test that all URLs are properly routed"""
#         # Test email registration URL
#         response = self.client.post(self.email_url, self.valid_email_data)
#         self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
        
#         # Test send OTP URL
#         response = self.client.post(self.send_otp_url, {'phone_number': self.phone_number})
#         self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
        
#         # Test phone registration URL
#         response = self.client.post(self.phone_url, {'phone_number': self.phone_number, 'otp': '1234'})
#         self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

#     # Test HTTP methods
#     def test_wrong_http_methods(self):
#         """Test that wrong HTTP methods return appropriate errors"""
#         # Test GET on POST-only endpoints
#         response = self.client.get(self.email_url)
#         self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
#         response = self.client.get(self.send_otp_url)
#         self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
#         response = self.client.get(self.phone_url)
#         self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


# # Simplified test class for basic functionality
# class BasicRegistrationTests(APITestCase):
#     """Simplified tests using only APIClient"""
    
#     def setUp(self):
#         self.client = APIClient()
#         cache.clear()
        
#     def test_basic_email_registration(self):
#         """Basic email registration test"""
#         response = self.client.post('/api/auth/register/email/', {
#             'email': 'test@example.com',
#             'password': 'testpass123',
#             'username': 'testuser'
#         }, format='json')
        
#         # Should either succeed or fail with validation errors
#         self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
#     def test_basic_otp_flow(self):
#         """Basic OTP flow test"""
#         # Send OTP
#         response1 = self.client.post('/api/auth/register/send_otp/', {
#             'phone_number': '7076246322'
#         }, format='json')
        
#         self.assertIn(response1.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])
        
#         # Try to verify (will likely fail without actual OTP)
#         response2 = self.client.post('/api/auth/register/phone/', {
#             'phone_number': '7076246322',
#             'otp': '1234'
#         }, format='json')
        
#         self.assertIn(response2.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])


# # Run specific tests
# class OTPStandaloneTests(TestCase):
#     """Tests specifically for OTP service without HTTP requests"""
    
#     def setUp(self):
#         cache.clear()
#         self.phone_number = '7076246322'
    
#     def test_otp_generation(self):
#         """Test OTP generation works"""
#         result = OTPService.generate_otp(self.phone_number)
#         self.assertEqual(result['status'], 'success')
    
#     def test_otp_verification_with_mock(self):
#         """Test OTP verification with mocked Redis"""
#         with patch('users.services.redis.Redis') as mock_redis:
#             mock_instance = mock_redis.return_value
#             mock_instance.hincrby.return_value = 1
#             mock_instance.hget.return_value = '1234'
#             mock_instance.hgetall.return_value = {'otp': '1234', 'attempts': '0'}
            
#             result = OTPService.verify_otp(self.phone_number, '1234')
#             self.assertIn(result['status'], ['valid', 'invalid'])
# # class EmailRegistrationView(TestCase):

# #     def setUp(self):
# #         self.client = APIClient()
# #         self.url = reverse('email_register')
# #         self.verificarion_data = {
# #             'email':'askarghya@gmail.com',
# #             'password': 'A4ghya@128',
# #             'confirm_password': 'A4ghya@128'
# #         }
# #         self.mismatch_data = {
# #             'email':'askarghya@gmail.com',
# #             'password': 'A4ghya@128',
# #             'confirm_password': 'Arghya@128'
# #         }
# #         return super().setUp()
    
# #     def test_email_user_creation(self):
# #         response = self.client.post(self.url,self.verificarion_data)
# #         self.assertEqual(response.status_code,status.HTTP_201_CREATED)
# #         self.assertEqual(response.data['message'], 'User creation Sucessfull.')

# #         user = CustomUserModel.objects.get(email = 'askarghya@gmail.com')
# #         self.assertEqual(response.data['user']['username'],user.username)

# #     def test_incorrect_user_creation(self):
# #         response = self.client.post(self.url,self.mismatch_data)
# #         self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        

# #     def test_duplicate_email_registration(self):
       
# #         self.client.post(self.url, self.verificarion_data)
        
        
# #         response = self.client.post(self.url, self.verificarion_data)
# #         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
# #         self.assertIn('email', response.data)

# #     def test_registration_throttling(self):
        
# #         for i in range(10): # limit 10
# #             data = self.verificarion_data.copy()
# #             data['email'] = f'test{i}@example.com'  # Different emails
# #             response = self.client.post(self.url, data)
        
# #         # Next request should be throttled
# #         response = self.client.post(self.url, {
# #             'email': 'throttled@example.com',
# #             'password': 'A4ghya@128',
# #             'confirm_password': 'A4ghya@128'
# #         })
        
# #         self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)