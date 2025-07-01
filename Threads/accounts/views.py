from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, LogoutSerializer, ProfileSerializer
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, parser_classes
from django.shortcuts import get_object_or_404
from .models import User

class RegisterView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # Rasmlar uchun

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            refresh = RefreshToken.for_user(user) # JWT token yaratish
            return Response({
                "message": "Foydalanuvchi muvaffaqiyatli yaratildi",
                "user": user_data,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView): 
    # permission_classes = [AllowAny]  

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            return Response({
                "message": "Tizimga muvaffaqiyatli kirildi!",
                "user": user_data,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Tizimdan muvaffaqiyatli chiqildi!", }, status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]  # login bo‘lmaganlar ham ko‘ra oladi
    lookup_field = 'username'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  # serializerda .get_is_owner ishlashi uchun
        return context

    def get_object(self):
        return get_object_or_404(self.get_queryset(), username=self.kwargs['username'])

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        if not request.user.is_authenticated or request.user != obj:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Siz faqat o'z profilingizni o'zgartira olasiz.")
        return super().update(request, *args, **kwargs)
    

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def check_username(request):
    username = request.data.get('username')
    if not username:
        return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"available": False, "message": "Username already taken."})
    return Response({"available": True})


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def check_email(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({"available": False, "message": "Email already taken."})
    return Response({"available": True})


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def check_phone(request):
    phone = request.data.get('phone')
    if not phone:
        return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(phone=phone).exists():
        return Response({"available": False, "message": "Phone number already taken."})
    return Response({"available": True})


class AuthCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'user': request.user.username}, status=status.HTTP_200_OK)