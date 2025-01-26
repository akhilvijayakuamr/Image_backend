from rest_framework import serializers
from .models import CustomUser, ImageModel
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# User register serializers

class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
    required = True,
    validators = [UniqueValidator(queryset=CustomUser.objects.all(),message="Email Already Exists")]
    )
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'phone_number']
        extra_kwargs = {
            'password': {'write_only':True}
        }
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    
    
    
    
# Add Image serializer

class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ['id', 'user', 'image', 'title', 'order', 'created_at']
        read_only_fields = ['created_at'] 
        


# Token customisation

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = user.id
        return token
    
    

    
    