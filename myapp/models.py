from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .Manager import CustomUserManager
 
# Create your models here.



# User models


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=200, blank=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    
    objects = CustomUserManager()
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    
    def __str__(self):
        return self.email
    
    


# Image Model


class ImageModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blog_image')
    title = models.CharField(max_length=250, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    
    
    def __str__(self):
        return f"Image {self.id} - User: {self.user.username} - Title: {self.title or 'Untitled'} - Order {self.order}"
    