from django.contrib.auth.models import BaseUserManager


# Custom Manager

class CustomUserManager(BaseUserManager):
    
    # Create User manager.
    
    def create_user(self, email, password=None, **extra_fields):
        
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    
    
    
    # Create Superuser manager.
    
    def create_superuser(self, email, password=None, **extra_fields):
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)