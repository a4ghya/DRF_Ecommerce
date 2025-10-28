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

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username" 
    REQUIRED_FIELDS = []

    
    def get_username(self):
        return self.email or self.phone_number

    def clean(self):
        if not self.username:
            self.username = self.get_username()
            print(f"clean method hit: {self.username}") 
        if not self.email and not self.phone_number:
            raise ValidationError("Either email or phone number must be provided.")
          # set username
            
        # if self.email and not self.phone_number:
        #     self.verification_method = 'email'
        # elif self.phone_number and not self.email:
        #     self.verification_method = 'phone'
        super().clean()
        
    def save(self,*args,**kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
## end users

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUserModel, on_delete=models.CASCADE,related_name = 'profile')
    first_name = models.CharField(max_length= 20, null=True,blank=False)
    last_name = models.CharField(max_length= 20, null=True,blank=False)
    dob = models.DateField(null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def get_username(self):
        return self.user.username
    
    def __str__(self):
        return f"{self.get_username()}'s Profile"
    
# class FriendShip(models.Model):
#     from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
#     to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         unique_together = ['from_user', 'to_user'] 
    
#     def __str__(self):
#         return f"{self.from_user.username} follows {self.to_user.username}"
    
# class Post(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
#     content = models.TextField(max_length=1000)
#     image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    
#     # Engagement metrics
#     likes_count = models.PositiveIntegerField(default=0)
#     comments_count = models.PositiveIntegerField(default=0)
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         ordering = ['-created_at']  # Newest posts first
    
#     def __str__(self):
#         return f"Post by {self.user.username}"

# class Like(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         unique_together = ['user', 'post'] 
    
#     def __str__(self):
#         return f"{self.user.username} likes post {self.post.id}"


# class Comment(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
#     content = models.TextField(max_length=500)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         ordering = ['created_at']  # Oldest comments first
    
#     def __str__(self):
#         return f"Comment by {self.user.username}"
    

    
    # phone or email must 

# class Sellers_LogInfo(models.Model):
#     first_name = models.CharField(max_length= 20, null=True,blank=False)
#     last_name = models.CharField(max_length= 20, null=True,blank=False)
#     email = models.EmailField(null=True, blank=True)
#     phonenumber = models.IntegerField(max_length=10,unique=True,null=True,blank=True)

