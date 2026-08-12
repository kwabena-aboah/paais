from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta

from .models import (
    Track, Lesson, UserProfile, OTPVerification, LessonProgress,
    AssessmentAttempt, Certificate, TrackCompletion, Transaction, Notification,
    PlatformSettings, Streak, Achievement, UserAchievement, ProgressMilestone,
    CommunityPost, CommunityComment
)


class UserSerializer(serializers.ModelSerializer):
    """User serializer with account details used by the profile page."""

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'is_active',
        )
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile with account summary and learning statistics."""

    user = UserSerializer(read_only=True)
    courses_started = serializers.SerializerMethodField()
    courses_completed = serializers.SerializerMethodField()
    certificates_earned = serializers.SerializerMethodField()
    account_status = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            'user', 'phone', 'business_function', 'country',
            'company_name', 'bio', 'avatar', 'preferred_track',
            'email_notifications', 'marketing_consent', 'is_verified', 'created_at',
            'courses_started', 'courses_completed', 'certificates_earned',
            'account_status',
        )

    def get_courses_started(self, obj):
        return LessonProgress.objects.filter(
            user=obj.user,
        ).values('lesson__track').distinct().count()

    def get_courses_completed(self, obj):
        return TrackCompletion.objects.filter(user=obj.user).values('track').distinct().count()

    def get_certificates_earned(self, obj):
        return Certificate.objects.filter(user=obj.user).count()

    def get_account_status(self, obj):
        return 'Active' if obj.user.is_active else 'Inactive'

    def validate_phone(self, value):
        if value and UserProfile.objects.filter(phone=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError('This phone number is already linked to another account.')
        return value


class TrackSerializer(serializers.ModelSerializer):
    """Track serializer with lesson count"""
    
    lesson_count = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Track
        fields = (
            'id', 'function', 'name', 'description', 'pitch',
            'icon', 'cover_image', 'is_active', 'is_featured',
            'is_free', 'price', 'lesson_count', 'user_progress', 'created_at'
        )
    
    def get_lesson_count(self, obj):
        return obj.lessons.filter(is_published=True).count()
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        completed = LessonProgress.objects.filter(
            user=request.user,
            lesson__track=obj,
            status='completed'
        ).count()
        
        total = obj.lessons.filter(is_published=True).count()
        return {'completed': completed, 'total': total} if total > 0 else None


class LessonSerializer(serializers.ModelSerializer):
    """Lesson serializer"""
    
    track_name = serializers.CharField(source='track.name', read_only=True)
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = (
            'id', 'track', 'track_name', 'title', 'description', 'level',
            'duration_minutes', 'content_html', 'video_url', 'objectives',
            'sample_prompt', 'ai_tools_covered', 'quiz_questions',
            'user_progress', 'is_published', 'created_at'
        )
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            progress = LessonProgress.objects.get(user=request.user, lesson=obj)
            return {
                'status': progress.status,
                'progress_percentage': progress.progress_percentage,
                'quiz_score': progress.quiz_score,
                'quiz_passed': progress.quiz_passed,
            }
        except LessonProgress.DoesNotExist:
            return None


class LessonProgressSerializer(serializers.ModelSerializer):
    """Lesson progress serializer"""
    
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = (
            'id', 'lesson', 'lesson_title', 'status', 'progress_percentage',
            'quiz_score', 'quiz_passed', 'started_at', 'completed_at'
        )


class AssessmentAttemptSerializer(serializers.ModelSerializer):
    """Read-only representation of a submitted assessment."""

    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = AssessmentAttempt
        fields = (
            'id', 'lesson', 'lesson_title', 'score', 'correct_answers',
            'total_questions', 'passed', 'submitted_at'
        )
        read_only_fields = fields


class CertificateSerializer(serializers.ModelSerializer):
    """Certificate/Credential serializer"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    track_name = serializers.CharField(source='track.name', read_only=True)
    
    class Meta:
        model = Certificate
        fields = (
            'id', 'user_name', 'track_name', 'credential_type',
            'credential_number', 'badge_image', 'verification_code',
            'is_verified', 'issued_at', 'expires_at', 'is_public',
            'public_url'
        )


class TrackCompletionSerializer(serializers.ModelSerializer):
    """Track completion serializer"""
    
    track_name = serializers.CharField(source='track.name', read_only=True)
    certificate = CertificateSerializer(read_only=True)
    
    class Meta:
        model = TrackCompletion
        fields = (
            'id', 'track', 'track_name', 'level', 'completed_at', 'certificate'
        )


class OTPSerializer(serializers.Serializer):
    """OTP Registration serializer"""
    
    contact = serializers.CharField(max_length=255)
    contact_type = serializers.ChoiceField(
        choices=(
            ('phone', 'Phone'),
            ('email', 'Email'),
        )
    )
    business_function = serializers.CharField(max_length=50, required=False)
    country = serializers.CharField(max_length=10, required=False)
    company_name = serializers.CharField(max_length=255, required=False)
    
    def validate_contact(self, value):
        value = value.strip()
        if '@' in value:
            value = value.lower()

        # Check if user already exists.
        if self.context.get('check_existing'):
            if '@' in value:
                if User.objects.filter(email__iexact=value).exists():
                    raise serializers.ValidationError(
                        "An account already exists for this email."
                    )
            elif UserProfile.objects.filter(phone=value).exists():
                raise serializers.ValidationError(
                    "An account already exists for this phone number."
                )
        return value


class OTPVerifySerializer(serializers.Serializer):
    """OTP verification serializer"""
    
    otp_code = serializers.CharField(max_length=6, min_length=6)
    contact = serializers.CharField(max_length=255)


class TransactionSerializer(serializers.ModelSerializer):
    """Transaction serializer"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = (
            'id', 'user_name', 'amount', 'currency', 'item_type',
            'item_id', 'reference', 'status', 'paystack_reference',
            'paystack_authorization_url', 'description', 'created_at',
            'completed_at'
        )
        read_only_fields = ('id', 'reference', 'status', 'created_at', 'completed_at')


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer"""
    
    class Meta:
        model = Notification
        fields = (
            'id', 'type', 'title', 'message', 'link', 'is_read', 'created_at'
        )


class PlatformSettingsSerializer(serializers.ModelSerializer):
    """Platform settings serializer (read-only for users)"""
    
    class Meta:
        model = PlatformSettings
        fields = (
            'site_name', 'site_description', 'site_logo', 'primary_color',
            'secondary_color', 'accent_color', 'support_email', 'whatsapp_group',
            'enable_paystack', 'enable_ai_features', 'enable_marketplace',
            'enable_certificates', 'footer_text'
        )


class DashboardSerializer(serializers.Serializer):
    """
    User dashboard data
    """

    profile = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    current_tracks = serializers.SerializerMethodField()
    recent_lessons = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    notifications = serializers.SerializerMethodField()


    def get_profile(self, obj):
        try:
            profile = UserProfile.objects.get(user=obj)
            return UserProfileSerializer(
                profile,
                context=self.context
            ).data

        except UserProfile.DoesNotExist:
            return None


    def get_stats(self, obj):

        return {
            "total_lessons_completed":
            LessonProgress.objects.filter(
                user=obj,
                status="completed"
            ).count(),

            "total_tracks_started":
            LessonProgress.objects.filter(
                user=obj
            )
            .values(
                "lesson__track"
            )
            .distinct()
            .count(),

            "total_certificates":
            Certificate.objects.filter(
                user=obj
            ).count(),

            "learning_streak":
            self._calculate_streak(obj)
        }


    def get_current_tracks(self, obj):

        tracks = Track.objects.filter(
            lessons__progress__user=obj,
            lessons__progress__status__in=[
                "started",
                "in_progress"
            ]
        ).distinct()[:5]


        return TrackSerializer(
            tracks,
            many=True,
            context=self.context
        ).data


    def get_recent_lessons(self,obj):

        lessons = LessonProgress.objects.filter(
            user=obj
        ).order_by(
            "-started_at"
        )[:5]


        return LessonProgressSerializer(
            lessons,
            many=True
        ).data


    def get_certificates(self,obj):

        certificates = Certificate.objects.filter(
            user=obj
        )

        return CertificateSerializer(
            certificates,
            many=True
        ).data


    def get_notifications(self,obj):

        notifications = Notification.objects.filter(
            user=obj
        )

        return NotificationSerializer(
            notifications,
            many=True
        ).data


    def _calculate_streak(self,user):

        streak = 0
        date = now().date()


        while LessonProgress.objects.filter(
            user=user,
            started_at__date=date
        ).exists():

            streak += 1
            date -= timedelta(days=1)


        return streak

class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = ('current_count', 'longest_count', 'last_activity_date')
        read_only_fields = fields


class AchievementSerializer(serializers.ModelSerializer):
    earned = serializers.SerializerMethodField()
    earned_at = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = ('code', 'name', 'description', 'icon', 'requirement_type', 'requirement_value', 'earned', 'earned_at')

    def get_earned(self, obj):
        user = self.context['request'].user
        return UserAchievement.objects.filter(user=user, achievement=obj).exists()

    def get_earned_at(self, obj):
        user = self.context['request'].user
        record = UserAchievement.objects.filter(user=user, achievement=obj).first()
        return record.earned_at if record else None


class MilestoneSerializer(serializers.ModelSerializer):
    current_value = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()

    class Meta:
        model = ProgressMilestone
        fields = ('code', 'name', 'description', 'target_type', 'target_value', 'icon', 'current_value', 'progress_percentage', 'completed')

    def _current_value(self, obj):
        return self.context.get('milestone_values', {}).get(obj.code, 0)

    def get_current_value(self, obj):
        return self._current_value(obj)

    def get_progress_percentage(self, obj):
        return min(100, round(self._current_value(obj) / obj.target_value * 100)) if obj.target_value else 0

    def get_completed(self, obj):
        return self._current_value(obj) >= obj.target_value


class CommunityCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = CommunityComment
        fields = ('id', 'author_name', 'body', 'created_at')
        read_only_fields = fields


class CommunityPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='user.get_full_name', read_only=True)
    track_name = serializers.CharField(source='track.name', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    liked_by_me = serializers.SerializerMethodField()
    comments = CommunityCommentSerializer(many=True, read_only=True)

    class Meta:
        model = CommunityPost
        fields = ('id', 'title', 'body', 'track', 'track_name', 'author_name', 'created_at', 'updated_at', 'comment_count', 'like_count', 'liked_by_me', 'comments')
        read_only_fields = ('user',)

    def get_liked_by_me(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.likes.filter(user=request.user).exists())


class CommunityCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityComment
        fields = ('body',)
