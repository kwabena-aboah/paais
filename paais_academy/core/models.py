from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.utils.timezone import now
from django.db.models import Q
import uuid
import random
import string

class PlatformSettings(models.Model):
    """Global platform settings manageable by admins"""
    
    site_name = models.CharField(max_length=100, default='PAAIS Academy')
    site_description = models.TextField(default='Learn the AI tools that do your everyday work')
    site_logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    site_favicon = models.ImageField(upload_to='favicons/', null=True, blank=True)
    
    # Brand Colors (stored as hex)
    primary_color = models.CharField(max_length=7, default='#0A0A33')  # Navy
    secondary_color = models.CharField(max_length=7, default='#E900FF')  # Magenta
    accent_color = models.CharField(max_length=7, default='#2EE6D6')  # Cyan
    
    # Contact & Social
    support_email = models.EmailField(default='support@paaisacademy.com')
    whatsapp_group = models.CharField(max_length=255, blank=True)
    
    # Features
    enable_paystack = models.BooleanField(default=True)
    enable_ai_features = models.BooleanField(default=True)
    enable_marketplace = models.BooleanField(default=True)
    enable_certificates = models.BooleanField(default=True)
    
    # Footer
    footer_text = models.TextField(default='© 2026 Pan African AI Summits & Corporate Training Ltd (PACT)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Platform Settings'
    
    def __str__(self):
        return self.site_name


class Track(models.Model):
    """Learning tracks (Marketing, Sales, Finance, etc.)"""
    
    FUNCTION_CHOICES = [
        ('marketing', 'Marketing & Communications'),
        ('sales', 'Sales & Business Development'),
        ('finance', 'Finance & Accounting'),
        ('hr', 'Human Resources'),
        ('operations', 'Operations & Supply Chain'),
        ('customer_service', 'Customer Service'),
        ('founder', 'Founder / SME Owner'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    function = models.CharField(max_length=50, choices=FUNCTION_CHOICES, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    pitch = models.TextField(help_text="Short marketing pitch for the track")
    
    icon = models.ImageField(upload_to='track_icons/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='track_covers/', null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0, help_text="Display order")
    
    # Pricing
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Lesson(models.Model):
    """Individual lessons within tracks"""
    
    LEVEL_CHOICES = [
        ('starter', 'Starter'),
        ('practitioner', 'Practitioner'),
        ('champion', 'Champion'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='lessons')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='starter')
    
    # Content
    duration_minutes = models.IntegerField(default=20, help_text="Estimated duration in minutes")
    content_html = models.TextField(help_text="Rich HTML content")
    video_url = models.URLField(blank=True, help_text="Optional embedded video")
    
    # Learning Objectives
    objectives = models.JSONField(default=list, help_text="Array of learning objectives")
    
    # AI-Powered Features
    sample_prompt = models.TextField(blank=True, help_text="Example AI prompt for this lesson")
    ai_tools_covered = models.JSONField(default=list, help_text="Tools covered: ChatGPT, Claude, Perplexity, etc.")
    
    # Assessment
    quiz_questions = models.JSONField(default=list, help_text="Quiz questions for this lesson")
    
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['track', 'level', 'order']
    
    def __str__(self):
        return f"{self.track.name} - {self.title}"


class AIGenerationLog(models.Model):
    """Audit/cost log for every AI lesson-generation call — one row per attempt."""
 
    track = models.ForeignKey(
        Track, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ai_generation_logs',
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ai_generation_logs',
        help_text="Set once the draft lesson is created from this call.",
    )
    topic = models.CharField(max_length=255)
    level = models.CharField(max_length=20, blank=True)
    triggered_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ai_generation_logs',
    )
 
    model = models.CharField(max_length=100, blank=True)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    duration_seconds = models.FloatField(default=0)
 
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    prompt_text = models.TextField(blank=True, help_text="Exact prompt sent to the model.")
    response_json = models.JSONField(default=dict, blank=True, help_text="Structured model output for audit/debugging.")
 
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['-created_at']
 
    def __str__(self):
        return f"{self.topic} ({'ok' if self.success else 'failed'})"
 


class UserProfile(models.Model):
    """Extended user profile"""
    
    FUNCTION_CHOICES = Track.FUNCTION_CHOICES
    COUNTRY_CHOICES = [
        ('gh', 'Ghana'),
        ('ng', 'Nigeria'),
        ('ke', 'Kenya'),
        ('za', 'South Africa'),
        ('rw', 'Rwanda'),
        ('ci', 'Côte d\'Ivoire'),
        ('sn', 'Senegal'),
        ('uk', 'United Kingdom'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Registration info
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    business_function = models.CharField(max_length=50, choices=FUNCTION_CHOICES, blank=True)
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    
    # Profile
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Learning preferences
    preferred_track = models.ForeignKey(Track, on_delete=models.SET_NULL, null=True, blank=True)
    email_notifications = models.BooleanField(default=True)
    marketing_consent = models.BooleanField(default=False)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_active_learner = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class OTPVerification(models.Model):
    """One-Time Password for registration"""
    
    phone_or_email = models.CharField(max_length=255)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
    
    def is_expired(self):
        return now() > self.expires_at
    
    def __str__(self):
        return f"{self.phone_or_email}"


class AssessmentAttempt(models.Model):
    """Stores a user's submitted quiz or assessment attempt."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_attempts')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assessment_attempts')
    score = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)
    answers = models.JSONField(default=list)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} ({self.score}%)"


class LessonProgress(models.Model):
    """Tracks user progress through lessons"""
    
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    progress_percentage = models.IntegerField(default=0)
    
    quiz_score = models.IntegerField(null=True, blank=True)
    quiz_passed = models.BooleanField(default=False)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'lesson')
        ordering = ['-last_accessed']
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"


class Certificate(models.Model):
    """Credential certificates"""
    
    CREDENTIAL_TYPES = [
        ('starter', 'AI Starter'),
        ('practitioner', 'AI Practitioner'),
        ('champion', 'AI Champion'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='certificates')
    
    credential_type = models.CharField(max_length=20, choices=CREDENTIAL_TYPES)
    credential_number = models.CharField(max_length=50, unique=True)
    
    # Badge/Image
    badge_image = models.ImageField(upload_to='badges/', null=True, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=True)
    verification_code = models.CharField(max_length=50, unique=True)
    
    # Dates
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Public sharing
    is_public = models.BooleanField(default=True)
    public_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.credential_number:
            self.credential_number = f"PAAIS-{uuid.uuid4().hex[:8].upper()}"
        if not self.verification_code:
            self.verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_credential_type_display()}"


class TrackCompletion(models.Model):
    """Tracks when a user completes a full track"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='track_completions')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='completions')
    level = models.CharField(max_length=20, choices=Lesson.LEVEL_CHOICES)
    
    completed_at = models.DateTimeField(auto_now_add=True)
    certificate = models.ForeignKey(Certificate, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'track', 'level')
    
    def __str__(self):
        return f"{self.user.username} - {self.track.name} ({self.level})"


class Transaction(models.Model):
    """Payment transactions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GHS')
    
    item_type = models.CharField(max_length=50)  # 'track', 'certificate', etc.
    item_id = models.CharField(max_length=100)
    
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Paystack Integration
    paystack_reference = models.CharField(max_length=100, blank=True)
    paystack_authorization_url = models.URLField(blank=True)
    
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency}"


class Streak(models.Model):
    """Daily learning streak summary for a user."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_count = models.PositiveIntegerField(default=0)
    longest_count = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.current_count} day streak"


class Achievement(models.Model):
    """A badge definition and the users who have earned it."""

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='bi-trophy')
    requirement_type = models.CharField(max_length=30)
    requirement_value = models.PositiveIntegerField(default=1)
    users = models.ManyToManyField(User, through='UserAchievement', related_name='achievements')

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """An achievement earned by a user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='earners')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'achievement')
        ordering = ['-earned_at']


class ProgressMilestone(models.Model):
    """A progress target shown to learners."""

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    target_type = models.CharField(max_length=30)
    target_value = models.PositiveIntegerField()
    icon = models.CharField(max_length=50, default='bi-flag')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CommunityPost(models.Model):
    """A learner discussion post."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    title = models.CharField(max_length=200)
    body = models.TextField()
    track = models.ForeignKey(Track, on_delete=models.SET_NULL, null=True, blank=True, related_name='community_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class CommunityComment(models.Model):
    """A reply to a community post."""

    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class CommunityPostLike(models.Model):
    """One like per user per discussion post."""

    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')


class Notification(models.Model):
    """User notifications"""
    
    TYPE_CHOICES = [
        ('lesson_new', 'New Lesson'),
        ('track_complete', 'Track Completion'),
        ('certificate_earned', 'Certificate Earned'),
        ('marketplace_match', 'Job Match'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
