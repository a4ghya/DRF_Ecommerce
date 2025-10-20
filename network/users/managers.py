from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):
    def create_user(self,password= None, email = None, phone_number = None, **extra_fields):
        if not email and not phone_number:
            raise ValueError("User must have email address or phone number")
        
        username = email or phone_number

        user = self.model(
            username = username,
            email=self.normalize_email(email) if email else None,
            phone_number=phone_number,
            **extra_fields
        )

        if email and password:
            user.set_password(password)
        
        elif email and not password:
            raise ValueError("email user must have password")
        elif phone_number:                                                                   
            user.set_unusable_password()  # Phone users: set unusable password to satisfy validation
        

        



        # if phone_number:
        #     user_date['phone_number'] = phone_number
        #    # print(f"debug: phone_number_entry", {phone_number})

        user.full_clean()

        user.save(using = self._db)

        return user
    def create_phone_user(self,phone_number,**extra_fields):  # now this method is availavle for queyset.
        return self.create_user(phone_number=phone_number,**extra_fields)
    def create_email_user(self,email,password,**extra_fields):
        return self.create_user(email=email,password=password,**extra_fields)

    
    def create_google_user(self,google_data):
        pass
    