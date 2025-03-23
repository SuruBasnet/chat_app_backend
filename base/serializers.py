from rest_framework import serializers
from .models import User

class AiChatSerializer(serializers.Serializer):
    message = serializers.CharField()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password','phone_no','email']

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','password']