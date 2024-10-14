from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import ProfView, ProfCollegianBodiesView, VizitView, VacationView, AwardsView, SocialPartnershipView, ProfMemberView, ReportView, AwardsVacationProfIdVIew, CustomAuthToken, RegisterUserView, generate_reset_token, reset_password, GetCollegianByBin, GetReportByBin

router = DefaultRouter()
router.register('prof-view', ProfView, basename = 'prof-view')
router.register('prof-member-view', ProfMemberView, basename = 'prof-member-view')
router.register('prof-collegian-bodies-view', ProfCollegianBodiesView, basename = 'prof-collegian-bodies-view')
router.register('vizit-view', VizitView, basename = 'vizit-view')
router.register('vacation-view', VacationView, basename = 'vacation-view')
router.register('report-view', ReportView, basename = 'report-view')
router.register('awards-view', AwardsView, basename = 'awards-view')
router.register('social-partnership-view', SocialPartnershipView, basename = 'social-partnership-view')

urlpatterns = [
    path('token/', obtain_auth_token, name='obtain_token'),
    path('auth/login/', CustomAuthToken.as_view(), name='user-login'),
    path('register/', RegisterUserView.as_view(), name='user-register'),
    path('generate_reset_token/', generate_reset_token, name='generate_reset_token'),
    path('reset_password/', reset_password, name='reset_password'),
    path('prof/<str:bin>/', ProfView.as_view({'get': 'retrieve'}), name='prof-detail'),
    path('get-collegian-by-bin/', GetCollegianByBin.as_view(), name='get-collegian-by-bin'),
    path('get-report-by-bin/', GetReportByBin.as_view(), name='get-report-by-bin'),
    path('awards-vacation-prof-member-id-view', AwardsVacationProfIdVIew.as_view(), name='awards-vacation-prof-member-id-view'),
    path('', include(router.urls))
]
