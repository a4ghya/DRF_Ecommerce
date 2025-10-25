import random

from django.core.cache import cache
class OTPService:

    @staticmethod
    def generate_otp(phone_number):
        otp_geneartor = random.randint(1000,9999)
        cache.set(f"otp_{phone_number}",otp_geneartor,timeout =300)
        return otp_geneartor

    @staticmethod
    def verify_otp(phone_number,otp):
        generated_otp = cache.get(f"otp_{phone_number}")
        if generated_otp and  generated_otp == otp:
            cache.delete(f"otp_{phone_number}")
            return True
        return False
        
