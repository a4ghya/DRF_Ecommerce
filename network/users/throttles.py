from rest_framework.throttling import SimpleRateThrottle

class EmailThrottle(SimpleRateThrottle):
    scope = 'email'
    def get_cache_key(self, request, view):
        email = request.data.get('email')
        

        if email:
            clean_email = email.lower().strip()
            return f'throttle_{self.scope}_{clean_email}'
        
            
        return super().get_cache_key(request, view)
    

class PhoneThrottle(SimpleRateThrottle):
    scope = 'phone'
    def get_cache_key(self, request, view):
        phone = request.data.get('phone_number')
        if phone:
            clean_phone = phone.strip()
            return f'throttle_{self.scope}_{clean_phone}'
        return super().get_cache_key(request, view)

class OTPThrottle(SimpleRateThrottle):
    scope = 'otp_send'
    def get_cache_key(self, request, view):
        phone = request.data.get('phone_number')
        if phone:
            clean_phone = phone.strip()
            return f'throttle_{self.scope}_{clean_phone}'
        return super().get_cache_key(request, view)