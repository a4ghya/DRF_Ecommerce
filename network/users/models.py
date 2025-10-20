from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User,AbstractBaseUser

from users.managers import CustomUserManager

# Create your models here.
class CustomUserModel(AbstractBaseUser):
    VERIFICATION_METHODS = [
    ('email', 'Email'),
    ('phone', 'Phone'),
    ]
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(
        unique=True,
        verbose_name="email",
        max_length=225,
        null=True,
        blank=True
    )
    phone_number = models.CharField(
        unique=True,
        verbose_name="phone",
        max_length=15,
        null=True,
        blank=True
    )
   
    verification_method = models.CharField(
        max_length=10, 
        choices=VERIFICATION_METHODS,
        null=True,
        blank=True
    )

    

    joined_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username" 
    REQUIRED_FIELDS = []

    
    def get_username(self):
        return self.email or self.phone_number

    def clean(self):
        super().clean()
        if not self.username:
            self.username = self.get_username()
            print(f"clean method hit: {self.username}") 
        if not self.email and not self.phone_number:
            raise ValidationError("Either email or phone number must be provided.")
          # set username
            
        if self.email and not self.phone_number:
            self.verification_method = 'email'
        elif self.phone_number and not self.email:
            self.verification_method = 'phone'
        
    def save(self,*args,**kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
## end users

class EndUsers_LogInfo(models.Model):
    #users = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length= 20, null=True,blank=False)
    last_name = models.CharField(max_length= 20, null=True,blank=False)
    email = models.EmailField(null=True, blank=True)
    phonenumber = models.IntegerField(unique=True,null=True,blank=True)
    is_enduser = models.BooleanField(default=True,null=True, blank=True)
    is_seller = models.BooleanField(default=False,null=True, blank=True)
    

    def save(self, *args, **kwargs):
        if self.email or self.phonenumber:
            pass
            #EndUsers_LogInfo.objects.create(email = self.email, phonenumber = self.phonenumber, *args)
        else:
            raise ValidationError("please put phonenumber or email")
        super().save(*args, **kwargs)

    # phone or email must 

class Sellers_LogInfo(models.Model):
    first_name = models.CharField(max_length= 20, null=True,blank=False)
    last_name = models.CharField(max_length= 20, null=True,blank=False)
    email = models.EmailField(null=True, blank=True)
    phonenumber = models.IntegerField(max_length=10,unique=True,null=True,blank=True)

