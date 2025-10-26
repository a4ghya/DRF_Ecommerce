import random
import time
import redis
from django.core.cache import cache


class OTPService:
    OTP_TIMEOUT = 120
    MAX_ATTEMPTS = 3

    @staticmethod
    def generate_otp(phone):

        otp = random.randint(1000, 9999)
        current_time = time.time()

        r= redis.Redis()
        pipe = r.pipeline()

        pipe.hset(f"otp_{phone}",mapping ={
            'otp': otp,
            'attempts': 0,
            'created_at':current_time
        })
        pipe.expire(f"otp_{phone}",OTPService.OTP_TIMEOUT)

        pipe.execute()

        return {
            'status': 'success', 
            'message': 'OTP generated successfully',
            'otp':otp # remove
           
        }
    
    @staticmethod
    def verify_otp(phone_number,user_otp):

        otp_key = f"otp_{phone_number}"

        r = redis.Redis()
        pipe = r.pipeline()

        if not r.exists(otp_key):  # or use r.exists()
            return {
                'status': 'invalid', 
                'message': 'OTP not found or expired'
            }


        pipe.hincrby(otp_key,'attempts',1)
        pipe.hget(otp_key, 'otp')
        pipe.hget(otp_key, 'created_at')

        attempts, stored_otp, created_at = pipe.execute()
        if stored_otp is None:
            return {
                'status': 'invalid', 
                'message': 'OTP expired'
            }

        attempts = int(attempts)
        stored_otp = int(stored_otp) if stored_otp else None
        created_at = float(created_at) if created_at else None

        current_time = time.time()
        if created_at and (current_time - created_at) > OTPService.OTP_TIMEOUT:
            OTPService._cleanup_otp(phone_number)
            return {
                'status': 'invalid', 
                'message': 'OTP expired'
            }

        if attempts > OTPService.MAX_ATTEMPTS:
            return {
            'status': 'invalid', 
            'message': 'Max Try Excedded',
                }
        if stored_otp and stored_otp == int(user_otp):
            OTPService._cleanup_otp(phone_number)
            return {
                "status": "valid", 
                "message": "OTP verified successfully."
            }
        else:
            remaining_attempts = OTPService.MAX_ATTEMPTS - attempts
            return {
                "status": "invalid", 
                "message": f"Invalid OTP. {remaining_attempts} attempts remaining."
            }
    @staticmethod
    def _cleanup_otp(phone_number):
        r = redis.Redis()
        r.delete(f"otp_{phone_number}")
    


# class OTPService:

#     @staticmethod
#     def generate_otp(phone_number):
#         otp_geneartor = random.randint(1000,9999)
#         current_time = time.time()
#         cache.set(f"otp_{phone_number}",otp_geneartor,timeout =120)
#         cache.set(f"otp_attempts_{phone_number}")
#         cache.set(f"current_time_{phone_number}",current_time,timeout =120)

        
#         return {'message':'sucessfully saved in cache'}

#     @staticmethod
#     def verify_otp(phone_number,otp,max_attempts =3):

#         attempts_key = f"otp_attempts_{phone_number}"
#         otp_key = f"otp_{phone_number}"
#         time_key = f"current_time_{phone_number}"

#         stored_otp = cache.get(otp_key)
#         generated_otp = cache.get(f"otp_{phone_number}")
#         generated_time = cache.get(f"current_time_{phone_number}")

#         attempts = cache.incr(attempts_key, 1)

#         if cache.get(f"otp_blocked_{phone_number}"):
#             return {"status": "blocked", "message": "Too many failed attempts. Please try again later."}

#         if attempts > max_attempts:
#             cache.set(f"otp_blocked_{phone_number}", True, timeout=120)
#             cache.delete(otp_key) # Invalidate the OTP
#             cache.delete(attempts_key) # Clear attempts
#             cache.delete(time_key)  # Clean up

#             return {"status": "blocked", "message": "Too many failed attempts. You are temporarily blocked."}
        
#         if not generated_otp:
#             raise ValueError('otp not found to match')
        

       
        
    

#         current_time = time.time()
#         time_differnce = current_time - generated_time
#         if time_differnce > 120:
#             cache.set(f"otp_blocked_{phone_number}", True, timeout=120)
#             cache.delete(otp_key) # Invalidate the OTP
#             cache.delete(attempts_key) # Clear attempts
#             cache.delete(time_key)  # Clean up
#             return {"status": "blocked", "message": "Time Expired"}

            
#         if stored_otp and stored_otp == otp:
#             cache.delete(otp_key)
#             cache.delete(attempts_key)
#             cache.delete(f"otp_blocked_{phone_number}")
#             return {"status": "valid", "message": "OTP Verified"}
#         elif stored_otp:
#             return {"status": "invalid", "message": "Invalid OTP"}
#         else:
#             # OTP has expired or was never generated
#             return {"status": "expired", "message": "Your OTP has expired or is invalid."}
#         #     cache.delete(f"otp_{phone_number}")
#         #     return True
#         # else:
#         #     cache.incr()
#         # return False
        
