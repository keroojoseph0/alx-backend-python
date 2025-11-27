from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password = None, **extra_fields):
        
        if not email:
            raise ValueError('User mast have an email')
        
        
        email = self.normalize_email(email)
        username = self.generate_username(email)
        user = self.model(username = username, email = email, **extra_fields)
        user.set_password(password)
        user.save()
        
        return user
    
    def generate_username(self, email):
            username = email.split('@')[0]
    
    
    def create_superuser(self, email, password = None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, password, **extra_fields)