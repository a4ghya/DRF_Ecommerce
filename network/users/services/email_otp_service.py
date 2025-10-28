import random
import time
from django.core.cache import cache
import redis

class EmailVerification:
    OTP_TIMEOUT = 600
    MAX_ATTEMPTS = 3

    @staticmethod
    def send_verification_code(email):
        otp = random.randint(100000, 999999)
        current_time = time.time()
        
        r= redis.Redis()
        pipe = r.pipeline()

        pipe.hset(f"otp_{email}", mapping={
            'otp': otp,
            'attempts': 0,
            'created_at': current_time
        })
        pipe.expire(f"otp_{email}", EmailVerification.OTP_TIMEOUT)
        pipe.execute()
        
        return {
            'status': 'success', 
            'message': 'OTP generated successfully',
            'otp': otp  # Remove in production
        }

    @staticmethod
    def verify_otp(email, user_otp):
        otp_key = f"otp_{email}"
        r = redis.Redis()
        

        # Check if key exists
        if not r.exists(otp_key):  # Use redis_client.exists(), not cache.exists()
            return {
                'status': 'invalid', 
                'message': 'OTP not found or expired'
            }

        pipe = r.pipeline()
        pipe.hincrby(otp_key, 'attempts', 1)
        pipe.hget(otp_key, 'otp')
        pipe.hget(otp_key, 'created_at')
        
        # Execute pipeline and get results
        results = pipe.execute()
        attempts, stored_otp, created_at = results

        if stored_otp is None:
            EmailVerification._cleanup_otp(email)
            return {
                'status': 'invalid', 
                'message': 'OTP expired'
            }

        attempts = int(attempts)
        stored_otp = int(stored_otp) if stored_otp else None
        created_at = float(created_at) if created_at else None

        current_time = time.time()
        if created_at and (current_time - created_at) > EmailVerification.OTP_TIMEOUT:
            EmailVerification._cleanup_otp(email)
            return {
                'status': 'invalid', 
                'message': 'OTP expired'
            }

        if attempts > EmailVerification.MAX_ATTEMPTS:
            EmailVerification._cleanup_otp(email)
            return {
                'status': 'invalid', 
                'message': 'Max Try Exceeded'
            }

        if stored_otp and stored_otp == int(user_otp):
            EmailVerification._cleanup_otp(email)
            return {
                "status": "valid", 
                "message": "OTP verified successfully."
            }
        else:
            remaining_attempts = EmailVerification.MAX_ATTEMPTS - attempts
            return {
                "status": "invalid", 
                "message": f"Invalid OTP. {remaining_attempts} attempts remaining."
            }

    @staticmethod
    def _cleanup_otp(email):
        r = redis.Redis()
        r.delete(f"otp_{email}")