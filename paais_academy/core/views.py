from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import connection
from django.http import JsonResponse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now
from django.db.models import Q, Count
from datetime import timedelta
import requests
import random
import string
import re
from decimal import Decimal, InvalidOperation
from uuid import uuid4
from decouple import config

from .models import (
    Track, Lesson, UserProfile, OTPVerification, LessonProgress,
    AssessmentAttempt, Certificate, TrackCompletion, Transaction, Notification,
    PlatformSettings, Streak, Achievement, UserAchievement, ProgressMilestone,
    CommunityPost, CommunityComment, CommunityPostLike
)
from .serializers import (
    TrackSerializer, LessonSerializer, UserProfileSerializer,
    LessonProgressSerializer, CertificateSerializer, TransactionSerializer,
    NotificationSerializer, OTPSerializer, OTPVerifySerializer,
    AssessmentAttemptSerializer, PlatformSettingsSerializer, DashboardSerializer,
    StreakSerializer, AchievementSerializer, MilestoneSerializer,
    CommunityPostSerializer, CommunityCommentSerializer, CommunityCommentCreateSerializer
)


# ============================================================
# Health Check
# ============================================================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Return service health without requiring authentication."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        return JsonResponse({'status': 'ok', 'database': 'ok'})
    except Exception:
        return JsonResponse(
            {'status': 'error', 'database': 'unavailable'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def normalize_phone_number(phone):
    """
    Normalize Ghana phone numbers to international E.164 format.

    Examples:
        0241234567       -> +233241234567
        241234567        -> +233241234567
        233241234567     -> +233241234567
        +233241234567    -> +233241234567
    """

    if not phone:
        return phone

    # Remove spaces, hyphens, brackets, etc.
    phone = re.sub(r'[^\d+]', '', str(phone).strip())

    # Remove international dialing prefix
    if phone.startswith('00'):
        phone = phone[2:]

    # Already has +
    if phone.startswith('+'):
        digits = phone[1:]
    else:
        digits = phone

    # Ghana local format: 0241234567
    if digits.startswith('0') and len(digits) == 10:
        digits = '233' + digits[1:]

    # Ghana format without leading zero: 241234567
    elif len(digits) == 9 and digits.startswith(('2', '5')):
        digits = '233' + digits

    return f'+{digits}'
# ============================================================
# Authentication & Registration Views
# ============================================================

class OTPRegistrationView(APIView):
    """Send OTP for registration"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        check_existing = request.data.get('check_existing', True)
        serializer = OTPSerializer(
            data=request.data,
            context={'check_existing': check_existing}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        contact = serializer.validated_data['contact'].strip()
        contact_type = serializer.validated_data['contact_type']

        # Normalize phone numbers before saving and sending
        if contact_type == 'phone':
            contact = normalize_phone_number(contact)
        else:
            contact = contact.lower()
        
        # Generate OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Delete old OTP
        OTPVerification.objects.filter(
            phone_or_email=contact,
            is_verified=False
        ).delete()
        
        # Create new OTP
        expires_at = now() + timedelta(minutes=10)
        otp = OTPVerification.objects.create(
            phone_or_email=contact,
            otp_code=otp_code,
            expires_at=expires_at
        )

        try:
            if contact_type == 'phone':
                self._send_sms(contact, otp_code)
            else:
                self._send_email(contact, otp_code)

        except Exception as exc:
            otp.delete()

            print(
                f'[OTP DELIVERY ERROR] {exc}',
                flush=True
            )

            return Response(
                {
                    'error': (
                        'We could not send your verification code. '
                        'Please try again.'
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Store registration data in session for later use
        request.session['registration_data'] = {
            'contact': contact,
            'contact_type': contact_type,
            'business_function': serializer.validated_data.get('business_function') or '',
            'country': serializer.validated_data.get('country') or '',
            'company_name': serializer.validated_data.get('company_name') or '',
        }
        
        return Response({
            'message': f'OTP sent to {contact}',
            'otp_id': str(otp.id),
        }, status=status.HTTP_200_OK)
    
    def _send_sms(self, phone, code):
        """Send OTP through Arkesel SMS API v2."""

        if settings.DEBUG:
            print(
                f'\n[PAAIS Academy OTP - phone: {phone}] {code}\n',
                flush=True
            )
            return

        api_key = settings.ARKESEL_API_KEY
        sender_id = settings.ARKESEL_SENDER_ID

        if not api_key:
            raise RuntimeError(
                'ARKESEL_API_KEY is not configured.'
            )

        message = (
            f'Your PAAIS Academy verification code is {code}. '
            f'It expires in 10 minutes.'
        )

        try:
            response = requests.post(
                'https://sms.arkesel.com/api/v2/sms/send',
                headers={
                    'api-key': api_key,
                    'Content-Type': 'application/json',
                },
                json={
                    'sender': sender_id,
                    'message': message,
                    'recipients': [phone],
                },
                timeout=15,
            )

            data = response.json()

            if not response.ok:
                print(
                    f'[Arkesel SMS ERROR] {data}',
                    flush=True
                )

                raise RuntimeError(
                    'Unable to send verification SMS.'
                )

            print(
                f'[Arkesel SMS SUCCESS] {data}',
                flush=True
            )

            return data

        except requests.RequestException as exc:
            print(
                f'[Arkesel SMS ERROR] {exc}',
                flush=True
            )

            raise RuntimeError(
                'Unable to send verification SMS.'
            ) from exc

    def _send_email(self, email, code):
        """Print OTPs in development and email them in production."""
        if settings.DEBUG:
            print('\n' + '=' * 60, flush=True)
            print(f'PAAIS ACADEMY OTP FOR {email}: {code}', flush=True)
            print('Development mode: no email was sent.', flush=True)
            print('=' * 60 + '\n', flush=True)
            return

        send_mail(
            subject='Your PAAIS Academy verification code',
            message=(
                f'Your PAAIS Academy verification code is: {code}\n\n'
                'This code expires in 10 minutes. If you did not request it, '
                'you can safely ignore this email.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )


class OTPVerifyView(APIView):
    """Verify OTP and create user account."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        contact = serializer.validated_data['contact'].strip()
        otp_code = serializer.validated_data['otp_code'].strip()

        # Normalize contact exactly as we did when sending the OTP
        if '@' in contact:
            contact = contact.lower()
        else:
            contact = normalize_phone_number(contact)

        try:
            otp = OTPVerification.objects.get(
                phone_or_email=contact,
                otp_code=otp_code,
                is_verified=False
            )

            # Check expiry
            if otp.is_expired():
                otp.delete()

                return Response(
                    {'error': 'OTP expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check maximum attempts
            if otp.attempts >= 3:
                otp.delete()

                return Response(
                    {'error': 'Too many attempts. Please request a new code.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Mark OTP as verified
            otp.is_verified = True
            otp.save(update_fields=['is_verified'])

            # Retrieve registration data
            reg_data = request.session.get(
                'registration_data',
                {}
            )

            # ===============================
            # EMAIL REGISTRATION
            # ===============================
            if '@' in contact:

                username_base = contact.split('@')[0]

                user, created = User.objects.get_or_create(
                    email=contact,
                    defaults={
                        'username': username_base
                    }
                )

            # ===============================
            # PHONE REGISTRATION
            # ===============================
            else:

                # Use the normalized international number
                # to create a predictable username
                phone_digits = re.sub(
                    r'\D',
                    '',
                    contact
                )

                username = f'user_{phone_digits}'

                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': (
                            f'{phone_digits}@paaisacademy.local'
                        )
                    }
                )

            # ===============================
            # CREATE / UPDATE PROFILE
            # ===============================

            profile, _ = UserProfile.objects.get_or_create(
                user=user
            )

            if '@' not in contact:
                profile.phone = contact

            profile.business_function = (
                reg_data.get('business_function')
                or profile.business_function
                or ''
            )

            profile.country = (
                reg_data.get('country')
                or profile.country
                or ''
            )

            profile.company_name = (
                reg_data.get('company_name')
                or profile.company_name
                or ''
            )

            profile.is_verified = True
            profile.save()

            # ===============================
            # GENERATE JWT
            # ===============================

            refresh = RefreshToken.for_user(user)

            # Remove registration data from session
            request.session.pop(
                'registration_data',
                None
            )

            return Response(
                {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'profile': UserProfileSerializer(profile).data,
                },
                status=status.HTTP_201_CREATED
            )

        except OTPVerification.DoesNotExist:

            # Find the active OTP and increase attempts
            otp_exists = OTPVerification.objects.filter(
                phone_or_email=contact,
                is_verified=False
            ).first()

            if otp_exists:
                otp_exists.attempts += 1
                otp_exists.save(
                    update_fields=['attempts']
                )

            return Response(
                {'error': 'Invalid OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

# ============================================================
# Track & Lesson Views
# ============================================================

class TrackViewSet(viewsets.ReadOnlyModelViewSet):
    """Track viewset"""
    
    queryset = Track.objects.filter(is_active=True).order_by('order')
    serializer_class = TrackSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['function', 'is_featured']
    
    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        """Get lessons for a track"""
        track = self.get_object()
        lessons = track.lessons.filter(is_published=True)
        serializer = LessonSerializer(
            lessons,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get user progress in a track"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        track = self.get_object()
        lessons = track.lessons.filter(is_published=True)
        
        total_lessons = lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            user=request.user,
            lesson__in=lessons,
            status='completed'
        ).count()
        
        progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        return Response({
            'track_id': str(track.id),
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percentage': int(progress_percentage),
        })


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """Lesson viewset"""
    
    queryset = Lesson.objects.filter(is_published=True)
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['track', 'level']
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start or resume a lesson"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        lesson = self.get_object()
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'status': 'in_progress'}
        )
        
        if not created and progress.status == 'started':
            progress.status = 'in_progress'
            progress.save()
        
        return Response(
            LessonProgressSerializer(progress).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def submit_quiz(self, request, pk=None):
        """Grade and persist a lesson quiz attempt on the server."""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        lesson = self.get_object()
        questions = lesson.quiz_questions or []
        answers = request.data.get('answers')

        if not questions:
            return Response({'error': 'This lesson has no quiz.'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(answers, list) or len(answers) != len(questions):
            return Response({'error': 'Submit one answer for every question.'}, status=status.HTTP_400_BAD_REQUEST)

        def correct_index(question):
            correct = question.get('correct_answer', question.get('correct'))
            if isinstance(correct, int):
                return correct
            if isinstance(correct, str):
                normalized = correct.strip()
                if normalized.isdigit():
                    return int(normalized)
                return next(
                    (index for index, option in enumerate(question.get('options', []))
                     if str(option).strip().lower() == normalized.lower()),
                    -1,
                )
            return -1

        correct_answers = sum(
            1 for question, answer in zip(questions, answers)
            if str(answer).lstrip('-').isdigit() and correct_index(question) == int(answer)
        )
        total_questions = len(questions)
        score = round((correct_answers / total_questions) * 100)
        passed = score >= 70
        attempt = AssessmentAttempt.objects.create(
            user=request.user,
            lesson=lesson,
            score=score,
            correct_answers=correct_answers,
            total_questions=total_questions,
            passed=passed,
            answers=answers,
        )

        progress, _ = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'status': 'in_progress'},
        )
        progress.quiz_score = score
        progress.quiz_passed = passed
        progress.save(update_fields=['quiz_score', 'quiz_passed', 'last_accessed'])

        return Response({
            'attempt': AssessmentAttemptSerializer(attempt).data,
            'score': score,
            'passed': passed,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'correct_indexes': [correct_index(question) for question in questions],
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a lesson"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        lesson = self.get_object()
        
        try:
            progress = LessonProgress.objects.get(
                user=request.user,
                lesson=lesson
            )
        except LessonProgress.DoesNotExist:
            progress = LessonProgress.objects.create(
                user=request.user,
                lesson=lesson
            )
        
        # Update progress. A passed quiz is required when the lesson has questions.
        submitted_score = request.data.get('quiz_score')
        if submitted_score is not None:
            try:
                progress.quiz_score = int(submitted_score)
                progress.quiz_passed = progress.quiz_score >= 70
            except (TypeError, ValueError):
                return Response({'error': 'quiz_score must be a number.'}, status=status.HTTP_400_BAD_REQUEST)

        progress.status = 'completed'
        progress.progress_percentage = 100
        progress.completed_at = now()
        progress.save()
        
        # Update gamification state after every completed lesson.
        record_learning_activity(request.user)
        self._check_track_completion(request.user, lesson.track)
        
        return Response(
            LessonProgressSerializer(progress).data,
            status=status.HTTP_200_OK
        )
    
    def _check_track_completion(self, user, track):
        """Check if a track is completed and issue certificate"""
        lessons = track.lessons.filter(is_published=True)
        total = lessons.count()
        completed = LessonProgress.objects.filter(
            user=user,
            lesson__in=lessons,
            status='completed'
        ).count()
        
        if total > 0 and completed == total:
            # Determine level based on lessons
            level = self._determine_level(track, completed)
            
            # Create or update track completion
            completion, _ = TrackCompletion.objects.get_or_create(
                user=user,
                track=track,
                level=level
            )
            
            # Issue certificate
            if not completion.certificate:
                cert = Certificate.objects.create(
                    user=user,
                    track=track,
                    credential_type=level
                )
                completion.certificate = cert
                completion.save()
                
                # Create notification
                Notification.objects.create(
                    user=user,
                    type='certificate_earned',
                    title='Certificate Earned!',
                    message=f'You\'ve earned the {cert.get_credential_type_display()} certificate!',
                    link=f'/certificates/{cert.id}'
                )
    
    def _determine_level(self, track, completed_count):
        """Determine credential level"""
        # This can be customized based on your logic
        return 'starter'  # Default to starter


# ============================================================
# User Progress & Dashboard Views
# ============================================================

class LessonProgressViewSet(viewsets.ModelViewSet):
    """User lesson progress"""
    
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LessonProgress.objects.filter(
            user=self.request.user
        ).order_by('-last_accessed')


class AssessmentAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """Authenticated user's quiz attempt history."""

    serializer_class = AssessmentAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AssessmentAttempt.objects.filter(user=self.request.user).select_related('lesson')


class UserProfileView(APIView):
    """User profile endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_fields = ('first_name', 'last_name', 'email')
        for field in user_fields:
            if field in request.data:
                setattr(request.user, field, request.data[field])
        request.user.save(update_fields=[field for field in user_fields if field in request.data])

        # Phone numbers are unique and are intentionally read-only in the UI.
        # Never pass a submitted phone value into the profile update serializer.
        profile_data = {
            key: value for key, value in request.data.items()
            if key not in (*user_fields, 'phone')
        }
        serializer = UserProfileSerializer(profile, data=profile_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardView(APIView):
    """User dashboard with all statistics"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        try:
            profile = user.profile
        except:
            profile = UserProfile.objects.create(user=user)
        
        certificates = Certificate.objects.filter(user=user)
        unread_notifications = Notification.objects.filter(
            user=user,
            is_read=False
        )[:5]
        
        serializer = DashboardSerializer(
            user,
            context={'request': request}
        )

        recent_progress = LessonProgress.objects.filter(
            user=user,
            status__in=['started', 'in_progress'],
        ).select_related('lesson', 'lesson__track').order_by('-last_accessed')
        continue_lesson = recent_progress.first().lesson if recent_progress.exists() else Lesson.objects.filter(
            is_published=True,
        ).order_by('track__order', 'order').first()
        assessment_attempts = AssessmentAttempt.objects.filter(user=user)
        assessment_summary = {
            'total_attempts': assessment_attempts.count(),
            'passed_attempts': assessment_attempts.filter(passed=True).count(),
            'average_score': round(sum(attempt.score for attempt in assessment_attempts) / assessment_attempts.count())
            if assessment_attempts.exists() else 0,
        }
        
        return Response({
            'profile': UserProfileSerializer(profile).data,
            'stats': {
                'total_lessons_completed': LessonProgress.objects.filter(
                    user=user,
                    status='completed'
                ).count(),
                'total_certificates': certificates.count(),
                'learning_hours': self._calculate_learning_hours(user),
                'current_streak': self._calculate_streak(user),
            },
            'current_tracks': TrackSerializer(
                Track.objects.filter(
                    lessons__progress__user=user,
                    lessons__progress__status__in=['started', 'in_progress']
                ).distinct()[:5],
                many=True,
                context={'request': request}
            ).data,
            'recent_lessons': LessonProgressSerializer(
                LessonProgress.objects.filter(user=user).order_by('-last_accessed')[:5],
                many=True
            ).data,
            'continue_lesson': LessonSerializer(
                continue_lesson,
                context={'request': request}
            ).data if continue_lesson else None,
            'assessment_summary': assessment_summary,
            'certificates': CertificateSerializer(certificates, many=True).data,
            'unread_notifications': NotificationSerializer(unread_notifications, many=True).data,
        })
    
    def _calculate_learning_hours(self, user):
        """Calculate total learning hours"""
        from django.db.models import Sum
        total_minutes = LessonProgress.objects.filter(
            user=user,
            status='completed'
        ).aggregate(
            total=Sum('lesson__duration_minutes')
        )['total'] or 0
        return total_minutes / 60
    
    def _calculate_streak(self, user):
        """Calculate learning streak"""
        from datetime import date
        
        streak = 0
        current_date = now().date()
        
        while True:
            has_activity = LessonProgress.objects.filter(
                user=user,
                last_accessed__date=current_date
            ).exists()
            
            if has_activity:
                streak += 1
                current_date = (now().replace(hour=0, minute=0, second=0) - timedelta(days=streak)).date()
            else:
                break
        
        return streak


# ============================================================
# Certificate Views
# ============================================================

class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """Certificate viewset"""
    
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Certificate.objects.filter(user=self.request.user)
        return Certificate.objects.filter(is_public=True)
    
    @action(detail=True, methods=['post'])
    def make_public(self, request, pk=None):
        certificate = self.get_object()
        if certificate.user != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        certificate.is_public = True
        certificate.save(update_fields=['is_public'])
        return Response(CertificateSerializer(certificate).data)

    @action(detail=True, methods=['get'])
    def verify(self, request, pk=None):
        """Verify a certificate"""
        cert = self.get_object()
        return Response({
            'is_valid': cert.is_verified and cert.is_public and (
                cert.expires_at is None or cert.expires_at >= now()
            ),
            'credential_number': cert.credential_number,
            'user_name': cert.user.get_full_name(),
            'credential_type': cert.get_credential_type_display(),
            'track': cert.track.name,
            'issued_at': cert.issued_at,
            'expires_at': cert.expires_at,
        })

# ============================================================
# Payment Views
# ============================================================

class DonationInitializeView(APIView):
    """Initialize an optional donation; lessons and tracks remain free."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            amount = Decimal(str(request.data.get('amount', '')).strip())
        except (InvalidOperation, AttributeError):
            return Response({'error': 'Enter a valid donation amount.'}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0 or amount > Decimal('99999999.99'):
            return Response({'error': 'Donation amount must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.email:
            return Response({'error': 'Add an email address before donating.'}, status=status.HTTP_400_BAD_REQUEST)

        transaction = Transaction.objects.create(
            user=request.user,
            amount=amount,
            currency='GHS',
            item_type='donation',
            item_id='support-cause',
            reference=f'DONATION-{uuid4().hex[:20].upper()}',
            description=request.data.get('message', 'Optional support for PAAIS Academy')[:500],
        )

        try:
            response = requests.post(
                'https://api.paystack.co/transaction/initialize',
                json={'email': request.user.email, 'amount': int(amount * 100), 'currency': 'GHS', 'reference': transaction.reference, 'callback_url': request.data.get('callback_url', ''), 'metadata': {'user_id': request.user.id, 'item_type': 'donation', 'purpose': 'support-cause'}},
                headers={'Authorization': f"Bearer {config('PAYSTACK_SECRET_KEY')}", 'Content-Type': 'application/json'},
                timeout=15,
            )
            data = response.json()
            if not response.ok or not data.get('status'):
                transaction.status = 'failed'
                transaction.save(update_fields=['status'])
                return Response({'error': 'Unable to start the donation payment.'}, status=status.HTTP_502_BAD_GATEWAY)

            transaction.paystack_reference = data['data']['reference']
            transaction.paystack_authorization_url = data['data']['authorization_url']
            transaction.save(update_fields=['paystack_reference', 'paystack_authorization_url'])
            return Response({'authorization_url': transaction.paystack_authorization_url, 'reference': transaction.reference, 'amount': str(amount), 'currency': 'GHS'})
        except (requests.RequestException, ValueError, KeyError):
            transaction.status = 'failed'
            transaction.save(update_fields=['status'])
            return Response({'error': 'Unable to connect to the payment provider.'}, status=status.HTTP_502_BAD_GATEWAY)


class PaystackInitializeView(APIView):
    """Initialize Paystack payment"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        amount = request.data.get('amount')
        item_type = request.data.get('item_type')  # 'track', 'certificate'
        item_id = request.data.get('item_id')
        
        if not all([amount, item_type, item_id]):
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create transaction record
        transaction = Transaction.objects.create(
            user=user,
            amount=amount,
            item_type=item_type,
            item_id=item_id,
            reference=f"PAAIS-{user.id}-{now().timestamp()}"
        )
        
        # Initialize Paystack payment
        paystack_url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {config('PAYSTACK_SECRET_KEY')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "email": user.email,
            "amount": int(float(amount) * 100),  # Convert to cents
            "reference": transaction.reference,
            "metadata": {
                "user_id": user.id,
                "item_type": item_type,
                "item_id": item_id
            }
        }
        
        try:
            response = requests.post(paystack_url, json=payload, headers=headers)
            data = response.json()
            
            if data['status']:
                transaction.paystack_reference = data['data']['reference']
                transaction.paystack_authorization_url = data['data']['authorization_url']
                transaction.save()
                
                return Response({
                    'authorization_url': data['data']['authorization_url'],
                    'access_code': data['data']['access_code'],
                    'reference': transaction.reference,
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Failed to initialize payment'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaystackVerifyView(APIView):
    """Verify Paystack payment"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, reference):
        # Verify with Paystack
        paystack_url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {config('PAYSTACK_SECRET_KEY')}"
        }
        
        try:
            response = requests.get(paystack_url, headers=headers)
            data = response.json()
            
            if data['status'] and data['data']['status'] == 'success':
                # Update transaction
                transaction = Transaction.objects.get(reference=reference)
                transaction.status = 'completed'
                transaction.completed_at = now()
                transaction.save()
                
                # Grant access to item
                self._grant_access(transaction)
                
                return Response({
                    'status': 'success',
                    'message': 'Payment verified and access granted'
                })
            else:
                return Response(
                    {'error': 'Payment verification failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _grant_access(self, transaction):
        """Grant access to purchased item"""
        if transaction.item_type == 'track':
            # Create enrollment or update profile
            pass
        elif transaction.item_type == 'certificate':
            # Mark certificate as paid
            pass


# ============================================================
# Settings Views
# ============================================================

class PlatformSettingsView(APIView):
    """Read public settings and update them for staff users."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        settings = PlatformSettings.objects.first()
        if not settings:
            settings = PlatformSettings.objects.create()

        serializer = PlatformSettingsSerializer(settings)
        return Response(serializer.data)

    def put(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({'detail': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        settings = PlatformSettings.objects.first() or PlatformSettings.objects.create()
        serializer = PlatformSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ============================================================
# Notification Views
# ============================================================

class NotificationViewSet(viewsets.ModelViewSet):
    """User notifications"""
    
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        return Response({'status': 'all marked as read'})


# ============================================================
# Gamification, analytics, and community
# ============================================================

def record_learning_activity(user):
    """Update the streak and award deterministic learning achievements."""
    today = now().date()
    streak, _ = Streak.objects.get_or_create(user=user)
    if streak.last_activity_date != today:
        if streak.last_activity_date == today - timedelta(days=1):
            streak.current_count += 1
        else:
            streak.current_count = 1
        streak.longest_count = max(streak.longest_count, streak.current_count)
        streak.last_activity_date = today
        streak.save()

    defaults = [
        ('first-lesson', 'First steps', 'Complete your first lesson.', 'bi-rocket', 'lessons', 1),
        ('five-lessons', 'Momentum builder', 'Complete five lessons.', 'bi-lightning', 'lessons', 5),
        ('seven-day-streak', 'Seven-day streak', 'Learn for seven consecutive days.', 'bi-fire', 'streak', 7),
    ]
    for code, name, description, icon, requirement_type, value in defaults:
        achievement, _ = Achievement.objects.get_or_create(
            code=code,
            defaults={'name': name, 'description': description, 'icon': icon,
                      'requirement_type': requirement_type, 'requirement_value': value},
        )
        lessons = LessonProgress.objects.filter(user=user, status='completed').count()
        current = streak.current_count if requirement_type == 'streak' else lessons
        if current >= value:
            UserAchievement.objects.get_or_create(user=user, achievement=achievement)


class GamificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        record_learning_activity(request.user)
        lessons = LessonProgress.objects.filter(user=request.user, status='completed').count()
        tracks = TrackCompletion.objects.filter(user=request.user).count()
        values = {'lessons': lessons, 'tracks': tracks, 'streak': getattr(request.user, 'streak', None).current_count if hasattr(request.user, 'streak') else 0}
        milestone_defaults = [
            ('lessons-5', 'Five lessons', 'Complete five lessons.', 'lessons', 5, 'bi-check2-circle'),
            ('lessons-10', 'Ten lessons', 'Complete ten lessons.', 'lessons', 10, 'bi-stars'),
            ('track-1', 'Track explorer', 'Complete a learning track.', 'tracks', 1, 'bi-compass'),
        ]
        for code, name, description, target_type, target_value, icon in milestone_defaults:
            ProgressMilestone.objects.get_or_create(
                code=code,
                defaults={'name': name, 'description': description, 'target_type': target_type,
                          'target_value': target_value, 'icon': icon},
            )
        milestones = ProgressMilestone.objects.filter(is_active=True)
        serializer_context = {'request': request, 'milestone_values': values}
        return Response({
            'streak': StreakSerializer(Streak.objects.get(user=request.user)).data,
            'achievements': AchievementSerializer(Achievement.objects.all(), many=True, context={'request': request}).data,
            'milestones': MilestoneSerializer(milestones, many=True, context=serializer_context).data,
        })


class AnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        completed = LessonProgress.objects.filter(user=user, status='completed')
        attempts = AssessmentAttempt.objects.filter(user=user)
        activity = []
        for offset in range(6, -1, -1):
            day = (now() - timedelta(days=offset)).date()
            activity.append({'date': day, 'lessons_completed': completed.filter(completed_at__date=day).count()})
        recommendations = Lesson.objects.filter(is_published=True).exclude(
            progress__user=user, progress__status='completed'
        ).order_by('track__order', 'order')[:3]
        return Response({
            'summary': {
                'learning_hours': round(sum(item.lesson.duration_minutes for item in completed) / 60, 1),
                'completion_rate': round(completed.count() / Lesson.objects.filter(is_published=True).count() * 100) if Lesson.objects.filter(is_published=True).exists() else 0,
                'average_quiz_score': round(sum(item.score for item in attempts) / attempts.count()) if attempts.exists() else 0,
            },
            'weekly_activity': activity,
            'recommendations': LessonSerializer(recommendations, many=True, context={'request': request}).data,
        })


class CommunityPostViewSet(viewsets.ModelViewSet):
    serializer_class = CommunityPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CommunityPost.objects.select_related('user', 'track').prefetch_related('comments__user', 'likes')

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        Notification.objects.create(
            user=self.request.user, type='general', title='Welcome to the community',
            message='Your discussion was published.', link='/community/'
        )

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = CommunityPostLike.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
        return Response({'liked': created, 'like_count': post.likes.count()})

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommunityCommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = CommunityComment.objects.create(post=post, user=request.user, **serializer.validated_data)
        return Response(CommunityCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
