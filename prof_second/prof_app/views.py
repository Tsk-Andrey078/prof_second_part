import os
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
import openpyxl
from .models import Prof, ProfCollegianBodies, ProfMember, Awards, Vacation, Report, Vizit, SocialPartnershipAgreements
from .serializer import ProfCollegianBodiesSerializer, ProfMemberSerializer, ProfSerializer, AwardsSerializer, VacationSerializer, VizitSerializer, ReportSerializer, SocialPartnershipAgreementsSerializer, UserSerializer



class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'is_admin': user.is_staff,  
            'is_superuser': user.is_superuser  
        })

class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in SAFE_METHODS:
            return True
        
        return request.user.groups.filter(name='Admin').exists()
    
class IsAdminUser(BasePermission):
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

class RegisterUserView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        username = request.data.get('username')
        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, существует ли пользователь с таким именем
        if User.objects.filter(username=username).exists():
            return Response({"error": "User with this username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Генерация случайного пароля
        password = User.objects.make_random_password()

        # Создание пользователя
        user = User.objects.create_user(username=username, password=password)

        # Возвращаем созданный пользователя и пароль
        return Response({"username": username, "password": password}, status=status.HTTP_201_CREATED)

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser] 

class ProfView(viewsets.ModelViewSet):
    queryset = Prof.objects.all()
    serializer_class = ProfSerializer
    lookup_field = "bin"
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["industry", "higher_union_org", "union_name", "union_type", "bin", "chairman_name"]

    def retrieve(self, request, bin=None):
        try:
            prof = Prof.objects.get(bin=bin)
            result = self.serialize_prof(prof)

            return Response(result)

        except Prof.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def serialize_prof(self, prof):
        prof_data = ProfSerializer(prof).data
        prof_data['children'] = self.get_children(prof)
        return prof_data

    def get_children(self, prof):
        children = Prof.objects.filter(higher_union_org=prof.union_name)
        serialized_children = [self.serialize_prof(child) for child in children]  
        return serialized_children

class ProfMemberView(viewsets.ModelViewSet):
    queryset = ProfMember.objects.all()
    serializer_class = ProfMemberSerializer
    lookup_field = "id"
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["name", "union_ticket_number", "gender", "birth_date", "position", "role", "education", "awards", "vacation", "prof_id"]

class ProfCollegianBodiesView(viewsets.ModelViewSet):
    queryset = ProfCollegianBodies.objects.all()
    serializer_class = ProfCollegianBodiesSerializer
    lookup_field = "id"
    permission_classes = [IsAdminOrReadOnly]

class AwardsView(viewsets.ModelViewSet):
    queryset = Awards.objects.all()
    serializer_class = AwardsSerializer
    lookup_field = "id"
    permission_classes = [IsAdminOrReadOnly]

class VacationView(viewsets.ModelViewSet):
    queryset = Vacation.objects.all()
    serializer_class = VacationSerializer
    lookup_field = "id"
    permission_classes = [IsAdminOrReadOnly]

class ReportView(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    lookup_field = "id"
    permission_classes = [IsAdminOrReadOnly]

class VizitView(viewsets.ModelViewSet):
    queryset = Vizit.objects.all()
    serializer_class = VizitSerializer
    lookup_field = "id"
    permission_classes = [IsAdminOrReadOnly]

class SocialPartnershipView(viewsets.ModelViewSet):
    queryset = SocialPartnershipAgreements.objects.all()
    serializer_class = SocialPartnershipAgreementsSerializer
    lookup_field = "id"
    permission_classes = [IsAdminOrReadOnly]

class AwardsVacationProfIdVIew(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        prof_member_id = request.query_params.get('prof_member_id')
        request_type = request.query_params.get('type')

        if not prof_member_id:
            return Response({'error': 'prof_member_id parameter is required'})
        try:
            if request_type == "awards":
                serializer_class = AwardsSerializer
                data_object = Awards.objects.filter(prof_memeber_id = prof_member_id)
            if request_type == "vacation":
                serializer_class = VacationSerializer
                data_object = Vacation.objects.filter(prof_memeber_id = prof_member_id)
        except data_object.DoesNotExist:
            return Response({'error': 'Object does not exist'})
        
        serializer = serializer_class(data_object, many = True)
        return Response(serializer.data)

class UploadProfMembers(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def post(self, request, *args, **kwargs):
        # Получаем prof_id из query параметра
        prof_id = request.query_params.get('prof_id')

        if not prof_id:
            return Response({'error': 'prof_id query parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем существование объекта Prof
        try:
            prof = Prof.objects.get(id=prof_id)  # Поиск объекта Prof по его id
        except Prof.DoesNotExist:
            return Response({'error': f'Prof with id {prof_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Получаем файл из запроса
        file = request.FILES.get('file')

        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Загружаем и читаем Excel файл
            wb = openpyxl.load_workbook(file)
            sheet = wb.active

            for row in sheet.iter_rows(min_row=2, values_only=True):  # Начинаем со второй строки (с пропуском заголовков)
                photo = row[0]
                name = row[1]
                union_ticket_number = row[2]
                gender = row[3]
                birth_date = row[4]
                position = row[5]
                role = row[6]
                education = row[7]
                total_work_experience = row[8]
                org_work_experience = row[9]
                union_membership_date = row[10]
                awards = row[11]
                vacation = row[12]
                phone = row[13]
                email = row[14]

                # Создание объекта ProfMember
                ProfMember.objects.create(
                    prof_id=prof,  # Используем объект Prof из query параметра
                    photo=photo,
                    name=name,
                    union_ticket_number=union_ticket_number,
                    gender=gender,
                    birth_date=birth_date,
                    position=position,
                    role=role,
                    education=education,
                    total_work_experience=total_work_experience,
                    org_work_experience=org_work_experience,
                    union_membership_date=union_membership_date,
                    awards=awards,
                    vacation=vacation,
                    phone=phone,
                    email=email,
                )

            return Response({'message': 'Data uploaded successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class GetTreeView(APIView):
    def get(self, request, *args, **kwargs):
        pass
