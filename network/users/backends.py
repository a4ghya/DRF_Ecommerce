from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model # in settings its the auth model was set.
from django.db.models import Q
from django.core.cache import cache


#from users.models import CustomSuperUserModel # superuser model

UserModel = get_user_model()

class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None,otp =None,**kwargs):
        if username is None:
            raise ValueError('no username')

        
        try:
            user = UserModel.objects.get(
                Q(email = username) | Q(phone_number = username)
            )
            #print(f"debug:backend, user is {user}")
        
        except UserModel.DoesNotExist:
            raise ValueError('not registered')
            
        
        if otp:
            return self._authenticate_phone(user, username,otp)
        elif password:
            return self._authenticate_email(user, password)
        else:
        
            raise ValueError('Authentication Failed')
            
    
    def _authenticate_phone(self,user,identifier, otp):
        stored_otp = cache.get(f"otp_{identifier}")  # username is the identifier
        if stored_otp and stored_otp == otp:
            cache.delete(f"otp_{identifier}")  # One-time use
            return user
       
        else:
            raise ValueError('Authentication Failed')


        #return None
    def _authenticate_email(self, user, password):
        if user.check_password(password):
            return user
        raise ValueError('Authentication Failed')
        

