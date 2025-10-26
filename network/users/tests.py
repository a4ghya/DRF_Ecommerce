from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from users.models import CustomUserModel
import redis
# test model and manager
class CustomUserModelTests(TestCase):
    def test_create_user_with_email(self):
        user = CustomUserModel.objects.create_email_user(
            email = 'test@gmail.com',
            password = 'password'
        )

        self.assertEqual(user.email, 'test@gmail.com')
        self.assertTrue(user.check_password("password"))
        self.assertFalse(user.is_admin)
        self.assertEqual(user.username,'test@gmail.com' )
        self.assertEqual(user.verification_method,'email' )
 
    
    def test_create_user_with_phone(self):
        user = CustomUserModel.objects.create_phone_user(
            phone_number="1234567890",
            # password="securepass123"
        )
        self.assertEqual(user.phone_number, "1234567890")
      #  self.assertTrue(user.check_password("securepass123"))
        self.assertEqual(user.username,'1234567890' )
        self.assertEqual(user.verification_method,'phone' )



    def test_cannot_create_user_without_email_or_phone(self):
        with self.assertRaises(ValueError):
            CustomUserModel.objects.create_user(password="somepass")

   
        

        


# Test the backend
from django.contrib.auth import authenticate
from django.core.cache import cache

class AuthenticationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.phone_user = CustomUserModel.objects.create_phone_user(
            phone_number="1234567890"
        )
        self.email_user = CustomUserModel.objects.create_email_user(email = 'askarghya@gmail.com',password = 'a4ghya128')
    
    def test_phone_authentication_with_valid_otp(self):
        # Store OTP in cache
        cache.set("otp_1234567890", "98989", timeout=600)
        
        # Authenticate with OTP
        user = authenticate(
            username="1234567890", 
            otp="98989"
        )
        self.assertEqual(self.phone_user.username,'1234567890' )
        self.assertEqual(user, self.phone_user)
        # OTP should be deleted after use
        self.assertIsNone(cache.get("otp_1234567890"))
    
    def test_phone_authentication_with_invalid_otp(self):
        cache.set("otp_1234567890", "123456", timeout=600)
        
        user = authenticate(
            username="1234567890", 
            otp="wrong_otp"  # Invalid OTP
        )
        
        self.assertIsNone(user)
        # OTP should still be there (not deleted on failure)
        self.assertEqual(cache.get("otp_1234567890"), "123456")
    
    def test_phone_authentication_with_expired_otp(self):
        # Don't set OTP - simulate expired/missing OTP
        user = authenticate(
            username="1234567890", 
            otp="123456"
        )
        
        self.assertIsNone(user)

    def test_email_with_correct_password(self):
        e_user = authenticate(
            username = 'askarghya@gmail.com',
            password = 'a4ghya128'
        )

        self.assertEqual(self.email_user.username,'askarghya@gmail.com')
        self.assertEqual(e_user,self.email_user)


########## Test serializers.#############
from users.serializers import EmailRegistration_serializer
class EmailSerializerTest(TestCase):
    def setUp(self):
        cache.clear()
        self.valid_data = {
            'email': 'askarghya@gmail.com',
            'password': 'A4ghya@128',
            'confirm_password': 'A4ghya@128'
        }
        self.mismatch_pass = {
            'email': 'askarghya@gmail.com',
            'password': 'A4ghya@128',
            'confirm_password': 'Arghya@128'

        }

        self.weak_pass ={
            'email': 'askarghya@gmail.com',
            'password': 'Arghya',
            'confirm_password': 'Arghya'
        }

        self.no_confirm ={
            'email': 'askarghya@gmail.com',
            'password': 'A4ghya@128'

        }

        self.no_email ={
            'password': 'A4ghya@128',
            'confirm_password': 'A4ghya@128'
        }
    
        return super().setUp()
    
    def test_email_user_creation(self):
        serializer = EmailRegistration_serializer(data = self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        #print(f"User: {user}")
        self.assertEqual(CustomUserModel.objects.filter(email = 'askarghya@gmail.com').exists(),True )
        self.assertEqual(user.email,'askarghya@gmail.com')

    def test_email_with_mismatch_password(self):
        serializer = EmailRegistration_serializer(data = self.mismatch_pass)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors['non_field_errors'][0]), 'password did not match')
    
    def test_with_weak_password(self):
        serializer = EmailRegistration_serializer(data = self.weak_pass)
        self.assertFalse(serializer.is_valid())
        print(serializer.errors)

    def test_no_confirmation_password(self):
        serializer = EmailRegistration_serializer(data = self.no_confirm)
        self.assertFalse(serializer.is_valid())
        print(serializer.errors)

    def test_no_email(self):
        serializer = EmailRegistration_serializer(data = self.no_email)
        self.assertFalse(serializer.is_valid())
        print(serializer.errors)
        with self.assertRaises(AssertionError):
            serializer.save()
        self.assertFalse(CustomUserModel.objects.filter(email='askarghya@gmail.com').exists())
        


# test for phone registration

from users.serializers import PhoneSendOTPSerializer,PhoneVerifyRegisterSerializer
from users.services.otp_service import OTPService

class PhoneRegistrationTest(TestCase):

    def setUp(self):
        cache.clear()
        
        # Generate OTP first
        OTPService.generate_otp(7076246322)
        
        # Get the actual OTP from Redis for testing
        r = redis.Redis(decode_responses=True)
        otp_data = r.hgetall(f"otp_7076246322")
        actual_otp = otp_data.get('otp') if otp_data else None

        self.validate_data = {
            'phone_number': '7076246322',  # Changed to string
            'otp': actual_otp
        }

        self.mismatch_data = {
            'phone_number': '7076246322',  # Changed to string
            'otp': '9999'  # Changed to string
        }
        return super().setUp()
    
    def test_phone_registration(self):
        serializer = PhoneVerifyRegisterSerializer(data=self.validate_data)
        self.assertTrue(serializer.is_valid())
    
        # Save the user
        user = serializer.save()
        
        # Assertions
        self.assertEqual(user.phone_number, '7076246322')  # String comparison
        self.assertTrue(CustomUserModel.objects.filter(phone_number='7076246322').exists())

    def test_with_invalid_otp(self):
        serializer = PhoneVerifyRegisterSerializer(data=self.mismatch_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)  # Changed from 'otp' to 'non_field_errors'

    def test_expired_otp(self):
        # Test expired OTP by manually expiring it
        r = redis.Redis()
        r.delete(f"otp_7076246322")  # Remove the OTP
        
        serializer = PhoneVerifyRegisterSerializer(data=self.validate_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
# class PhoneRegistrationTest(TestCase):

#     def setUp(self):
#         cache.clear()
#         send_otp = OTPService.generate_otp(7076246322)
        
#         self.validate_data={
#             'phone_number': 7076246322,
#             'otp': send_otp
#         }

#         self.mismatch_data = {
#             'phone_number': 7076246322,
#             'otp': 9999 # a random otp
#         }
#         return super().setUp()
    
#     def test_phone_registration(self):
       
#        # ph = PhoneSendOTPSerializer(data = self.validate_data)
#        serializer = PhoneVerifyRegisterSerializer(data = self.validate_data)
#        self.assertTrue(serializer.is_valid())
    
#     # 5. Save the user
#        user = serializer.save()
        
#         # 6. Assertions
#        self.assertEqual(user.phone_number, '7076246322')
#        self.assertTrue(CustomUserModel.objects.filter(phone_number='7076246322').exists())

#     def test_with_invalid_otp(self):
#         serializer = PhoneVerifyRegisterSerializer(data=self.mismatch_data)
#         self.assertFalse(serializer.is_valid())
#         self.assertIn('otp', serializer.errors)
    


# test mixed data

class MixedRegistration(TestCase):

    def setUp(self):
        cache.clear()
        send_otp = OTPService.generate_otp(7076246322)
        self.mixed_data = {
            'email': 'askarghya@gmail.com',
            'phone_number': 7076246322,
            'password': 'A4ghya@128',
            'confirm_password': 'A4ghya@128',
            'otp':send_otp   
        }

    def test_mixed_email_registration(self):
        serilizer = EmailRegistration_serializer(data =self.mixed_data)
        self.assertTrue(serilizer.is_valid())
        user = serilizer.save()
        self.assertEqual(user.email, 'askarghya@gmail.com')
        self.assertFalse(user.phone_number, '7076246322')

    def test_mixed_phone_registration(self):
        serilizer = PhoneVerifyRegisterSerializer(data =self.mixed_data)
        self.assertTrue(serilizer.is_valid())
        user = serilizer.save()
        self.assertFalse(user.email, 'askarghya@gmail.com')
        self.assertEqual(user.phone_number, '7076246322')