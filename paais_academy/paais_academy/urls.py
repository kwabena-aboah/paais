from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from core.views import (
    TrackViewSet, LessonViewSet, LessonProgressViewSet,
    AssessmentAttemptViewSet, CertificateViewSet, NotificationViewSet,
    OTPRegistrationView, OTPVerifyView,
    UserProfileView, DashboardView,
    PaystackInitializeView, DonationInitializeView, PaystackVerifyView,
    PlatformSettingsView, GamificationView, AnalyticsView, CommunityPostViewSet,
    health_check,
)

# API Router
router = DefaultRouter()
router.register(r'tracks', TrackViewSet, basename='track')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'progress', LessonProgressViewSet, basename='progress')
router.register(r'assessment-attempts', AssessmentAttemptViewSet, basename='assessment-attempt')
router.register(r'certificates', CertificateViewSet, basename='certificate')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'community/posts', CommunityPostViewSet, basename='community-post')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('api/v1/health/', health_check, name='api-health-check'),

    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include(router.urls)),
    
    # Authentication
    path('api/v1/auth/register/send-otp/', OTPRegistrationView.as_view(), name='send-otp'),
    path('api/v1/auth/register/verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User
    path('api/v1/user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/v1/user/dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/v1/user/gamification/', GamificationView.as_view(), name='gamification'),
    path('api/v1/user/analytics/', AnalyticsView.as_view(), name='analytics'),
    
    # Payments
    path('api/v1/payments/initialize/', PaystackInitializeView.as_view(), name='initialize-payment'),
    path('api/v1/donations/initialize/', DonationInitializeView.as_view(), name='initialize-donation'),
    path('api/v1/payments/verify/<str:reference>/', PaystackVerifyView.as_view(), name='verify-payment'),
    
    # Settings
    path('api/v1/settings/', PlatformSettingsView.as_view(), name='settings'),
    
    # DRF Auth (for browsable API)
    path('api/auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
