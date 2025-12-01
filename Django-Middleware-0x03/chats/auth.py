from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'role', 'created_at', 'password']
        
        read_only_fields = ['user_id', 'created_at', 'username', 'email', 'role']
        
        extra_kwargs = {
            'passwoerd': {'write_only': True, 'required': True},
        }
        
    def validate_email(self, value):
        if '@' not in value:
            raise serializers.ValidationError('Not Valid Email')
        return value
    
    
class SignUpSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'password_confirm']
        
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False, 'write_only': True},
            'password_confirm': {'required': True, 'allow_blank': False, 'write_only': True},
        }
        
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Password don't mach")
        return data
    
    def create(self, validated_data):
        """ create new user"""
        
        validated_data.pop('password_confirm')
        username = validated_data.get('username', validated_data['email'].split('@')[0])
        user = User.objects.create_user(
            email = validated_data['email'],
            username = username,
            password = validated_data['password'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
        )
        
        return user
    
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)