from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

# Create your models here.


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

