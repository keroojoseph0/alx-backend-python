from django.shortcuts import render
from rest_framework import viewsets
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.decorators import api_view, permission_classes
from .models import User
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from .permissions import IsOwnerOrReadOnly
from rest_framework.views import APIView
from .auth import LoginSerializer, UserSerializer, SignUpSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email'] # type: ignore
        password = serializer.validated_data['password'] # type: ignore
        
        user = authenticate(email=email, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        else:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
class SignUpView(APIView):
    """View for user registration"""
    permission_classes = [AllowAny]  # Allow unauthenticated access

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        refresh = RefreshToken.for_user(user) # type: ignore
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
        
        
class LogoutView(APIView):
    """View for user logout"""
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out'})
        except Exception as e:
            return Response(
                {'error': 'Invalid token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().prefetch_related('participants', 'messages')
    serializer_class = ConversationSerializer
    permission_classes = [IsOwnerOrReadOnly]
    
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().select_related('sender_id', 'conversation')
    serializer_class = MessageSerializer
    permission_classes = [IsOwnerOrReadOnly] 
    
    
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def signup(request):
#     serializer = SignUpSerializer(data = request.data)
#     
#     if serializer.is_valid():
#         email = request.data['email']
#         
#         if User.objects.filter(email = email).exists():
#             return Response({'message': 'The user email exist before'}, status=status.HTTP_400_BAD_REQUEST)
#         else: 
#             User.objects.create(
#                 email = email, 
#                 username = email.split('@')[0],
#                 password = make_password(request.data['password']),
#                 first_name = request.data['first_name'],
#                 last_name = request.data['last_name']
#             )
#             return Response({'message': 'User create successfuly'}, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)