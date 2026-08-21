from django.contrib import admin
from django.contrib import messages
from django.urls import reverse, path
from django.shortcuts import redirect, render
from django.utils.html import format_html
from django.db.models import Count

from .models import (
    Track, Lesson, UserProfile, Certificate, TrackCompletion,
    LessonProgress, AssessmentAttempt, Transaction, Notification, PlatformSettings,
    OTPVerification, AIGenerationLog,
)
from .ai_generator import generate_lesson, AIGenerationError
from .forms import AILessonGenerationForm  # see forms.py


# ============================================================
# Settings Admin
# ============================================================

@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Site Info', {
            'fields': ('site_name', 'site_description', 'site_logo', 'site_favicon')
        }),
        ('Colors (Hex)', {
            'fields': ('primary_color', 'secondary_color', 'accent_color')
        }),
        ('Contact & Social', {
            'fields': ('support_email', 'whatsapp_group')
        }),
        ('Features', {
            'fields': ('enable_paystack', 'enable_ai_features', 'enable_marketplace', 'enable_certificates')
        }),
        ('Footer', {
            'fields': ('footer_text',)
        }),
    )

    def has_add_permission(self, request):
        return not PlatformSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ============================================================
# Track & Lesson Admin
# ============================================================

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'level', 'duration_minutes', 'is_published')
    ordering = ('order',)


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('name', 'function', 'lesson_count', 'is_active', 'is_featured', 'order', 'generate_lesson_button')
    list_filter = ('is_active', 'is_featured', 'function', 'is_free', 'created_at')
    list_editable = ('order', 'is_active', 'is_featured')
    search_fields = ('name', 'description')

    fieldsets = (
        ('Track Information', {
            'fields': ('function', 'name', 'description', 'pitch')
        }),
        ('Media', {
            'fields': ('icon', 'cover_image')
        }),
        ('Visibility & Ordering', {
            'fields': ('is_active', 'is_featured', 'order')
        }),
        ('Pricing', {
            'fields': ('is_free', 'price')
        }),
    )

    inlines = [LessonInline]

    def lesson_count(self, obj):
        return obj.lessons.filter(is_published=True).count()
    lesson_count.short_description = 'Published Lessons'

    # --------------------------------------------------------
    # AI lesson generation — superusers only
    # --------------------------------------------------------

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<uuid:track_id>/generate-lesson/',
                self.admin_site.admin_view(self.generate_lesson_view),
                name='core_track_generate_lesson',
            ),
        ]
        return custom_urls + urls

    def generate_lesson_button(self, obj):
        url = reverse('admin:core_track_generate_lesson', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}">Generate lesson with AI</a>', url
        )
    generate_lesson_button.short_description = 'AI Generation'

    def generate_lesson_view(self, request, track_id):
        # Restrict to system administrators only — everyone else is bounced back.
        if not request.user.is_superuser:
            messages.error(request, "Only system administrators can generate lessons with AI.")
            return redirect('admin:core_track_changelist')

        track = self.get_object(request, track_id)
        if track is None:
            messages.error(request, "Track not found.")
            return redirect('admin:core_track_changelist')

        if request.method == 'POST':
            form = AILessonGenerationForm(request.POST)
            if form.is_valid():
                topic = form.cleaned_data['topic']
                level = form.cleaned_data['level']
                duration_minutes = form.cleaned_data.get('duration_minutes')
                run_async = form.cleaned_data.get('run_in_background')

                if run_async:
                    from .tasks import generate_lesson_task
                    generate_lesson_task.delay(
                        track_id=str(track.pk),
                        topic=topic,
                        level=level,
                        duration_minutes=duration_minutes,
                        triggered_by_id=request.user.pk,
                    )
                    messages.success(
                        request,
                        "Generation started in the background — you'll get a notification when the draft is ready."
                    )
                    return redirect('admin:core_track_changelist')

                try:
                    data = generate_lesson(
                        track=track, topic=topic, level=level,
                        duration_minutes=duration_minutes, triggered_by=request.user,
                    )
                except AIGenerationError as exc:
                    messages.error(request, f"Generation failed: {exc}")
                    return render(request, 'admin/generate_lesson_form.html', {
                        'form': form, 'track': track, 'opts': self.model._meta,
                    })

                lesson = Lesson.objects.create(
                    track=track,
                    is_published=False,  # always land as a draft for human review
                    order=track.lessons.count(),
                    **data.to_lesson_fields(),
                )
                if data.generation_log_id:
                    AIGenerationLog.objects.filter(pk=data.generation_log_id).update(lesson=lesson)
                messages.success(
                    request,
                    f'Draft lesson "{lesson.title}" created. Review it below, then check '
                    f'"is published" to make it live.'
                )
                return redirect(reverse('admin:core_lesson_change', args=[lesson.pk]))
        else:
            form = AILessonGenerationForm()

        return render(request, 'admin/generate_lesson_form.html', {
            'form': form, 'track': track, 'opts': self.model._meta,
        })


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'track', 'level', 'duration_minutes', 'is_published', 'order')
    list_filter = ('track', 'level', 'is_published', 'created_at')
    list_editable = ('order', 'is_published')
    search_fields = ('title', 'description')

    fieldsets = (
        ('Basic Info', {
            'fields': ('track', 'title', 'description', 'level', 'order')
        }),
        ('Content', {
            'fields': ('duration_minutes', 'content_html', 'video_url'),
            'classes': ('collapse',)
        }),
        ('Learning', {
            'fields': ('objectives', 'sample_prompt', 'ai_tools_covered'),
            'classes': ('collapse',)
        }),
        ('Assessment', {
            'fields': ('quiz_questions',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_published',),
            'description': 'A lesson only appears on the site (via the API) once "is published" is checked.',
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('track')


# ============================================================
# AI Generation Log Admin (read-only — cost/audit trail)
# ============================================================

@admin.register(AIGenerationLog)
class AIGenerationLogAdmin(admin.ModelAdmin):
    list_display = (
        'topic', 'track', 'level', 'success_badge', 'triggered_by',
        'model', 'token_summary', 'duration_seconds', 'created_at',
    )
    list_filter = ('success', 'level', 'model', 'created_at')
    search_fields = ('topic', 'track__name', 'triggered_by__username', 'error_message')
    readonly_fields = (
        'track', 'lesson', 'topic', 'level', 'triggered_by', 'model',
        'input_tokens', 'output_tokens', 'duration_seconds', 'success',
        'error_message', 'prompt_text', 'response_json', 'created_at',
    )

    def success_badge(self, obj):
        color = '#2ECC71' if obj.success else '#E74C3C'
        text = 'Success' if obj.success else 'Failed'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 2px; font-size: 11px;">{}</span>',
            color, text,
        )
    success_badge.short_description = 'Result'

    def token_summary(self, obj):
        return f"{obj.input_tokens} in / {obj.output_tokens} out"
    token_summary.short_description = 'Tokens'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # Keep the full audit trail; only superusers may prune it.
        return request.user.is_superuser


# ============================================================
# User & Profile Admin
# ============================================================

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0
    fields = ('phone', 'business_function', 'country', 'company_name', 'is_verified', 'is_active_learner')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'business_function', 'country', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'is_active_learner', 'business_function', 'country', 'created_at')
    search_fields = ('user__email', 'user__username', 'phone')

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Contact Info', {
            'fields': ('phone', 'company_name')
        }),
        ('Profile', {
            'fields': ('business_function', 'country', 'bio', 'avatar')
        }),
        ('Preferences', {
            'fields': ('preferred_track', 'email_notifications', 'marketing_consent')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active_learner')
        }),
    )

    readonly_fields = ('user',)

    def has_add_permission(self, request):
        return False  # Created through user registration


# ============================================================
# Progress & Certificate Admin
# ============================================================

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'status_badge', 'progress_percentage', 'quiz_passed', 'completed_at')
    list_filter = ('status', 'quiz_passed', 'started_at', 'completed_at')
    search_fields = ('user__email', 'lesson__title')
    readonly_fields = ('user', 'lesson', 'started_at', 'last_accessed', 'completed_at')

    fieldsets = (
        ('Progress', {
            'fields': ('user', 'lesson', 'status', 'progress_percentage')
        }),
        ('Assessment', {
            'fields': ('quiz_score', 'quiz_passed')
        }),
        ('Dates', {
            'fields': ('started_at', 'last_accessed', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        colors = {
            'started': '#FFA500',
            'in_progress': '#3498DB',
            'completed': '#2ECC71',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#999'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def has_add_permission(self, request):
        return False


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('credential_number', 'user', 'track', 'credential_type_badge', 'is_verified', 'issued_at')
    list_filter = ('credential_type', 'is_verified', 'issued_at')
    search_fields = ('user__email', 'credential_number', 'track__name')
    readonly_fields = ('credential_number', 'verification_code', 'issued_at')

    fieldsets = (
        ('Certificate Info', {
            'fields': ('user', 'track', 'credential_type', 'credential_number')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_code')
        }),
        ('Badge', {
            'fields': ('badge_image',)
        }),
        ('Sharing', {
            'fields': ('is_public', 'public_url')
        }),
        ('Dates', {
            'fields': ('issued_at', 'expires_at')
        }),
    )

    def credential_type_badge(self, obj):
        colors = {
            'starter': '#85C1E2',
            'practitioner': '#F39C12',
            'champion': '#E74C3C',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.credential_type, '#999'),
            obj.get_credential_type_display()
        )
    credential_type_badge.short_description = 'Credential'


@admin.register(TrackCompletion)
class TrackCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'track', 'level_badge', 'completed_at', 'has_certificate')
    list_filter = ('level', 'completed_at')
    search_fields = ('user__email', 'track__name')
    readonly_fields = ('user', 'track', 'completed_at')

    def level_badge(self, obj):
        colors = {
            'starter': '#85C1E2',
            'practitioner': '#F39C12',
            'champion': '#E74C3C',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.level, '#999'),
            obj.get_level_display()
        )
    level_badge.short_description = 'Level'

    def has_certificate(self, obj):
        return bool(obj.certificate)
    has_certificate.boolean = True
    has_certificate.short_description = 'Has Certificate'

    def has_add_permission(self, request):
        return False


# ============================================================
# Transaction Admin
# ============================================================

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'amount_display', 'item_type', 'status_badge', 'created_at')
    list_filter = ('status', 'item_type', 'currency', 'created_at')
    search_fields = ('user__email', 'reference', 'paystack_reference')
    readonly_fields = ('reference', 'created_at', 'completed_at', 'paystack_reference')

    fieldsets = (
        ('Transaction Info', {
            'fields': ('user', 'reference', 'amount', 'currency')
        }),
        ('Item', {
            'fields': ('item_type', 'item_id', 'description')
        }),
        ('Paystack', {
            'fields': ('paystack_reference', 'paystack_authorization_url', 'status'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    def amount_display(self, obj):
        return f"{obj.amount} {obj.currency}"
    amount_display.short_description = 'Amount'

    def status_badge(self, obj):
        colors = {
            'pending': '#F39C12',
            'completed': '#2ECC71',
            'failed': '#E74C3C',
            'cancelled': '#95A5A6',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#999'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


# ============================================================
# Notification Admin
# ============================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'is_read_badge', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('user', 'created_at')

    fieldsets = (
        ('Notification', {
            'fields': ('user', 'type', 'title', 'message')
        }),
        ('Interaction', {
            'fields': ('is_read', 'link')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def is_read_badge(self, obj):
        color = '#2ECC71' if obj.is_read else '#F39C12'
        text = 'Read' if obj.is_read else 'Unread'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 2px; font-size: 11px;">{}</span>',
            color,
            text
        )
    is_read_badge.short_description = 'Read Status'


# ============================================================
# OTP Admin (for debugging)
# ============================================================

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('phone_or_email', 'is_verified', 'attempts', 'expires_at', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('phone_or_email',)
    readonly_fields = ('otp_code', 'created_at', 'expires_at')

    fieldsets = (
        ('OTP', {
            'fields': ('phone_or_email', 'otp_code')
        }),
        ('Status', {
            'fields': ('is_verified', 'attempts')
        }),
        ('Expiry', {
            'fields': ('created_at', 'expires_at')
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ============================================================
# Admin Site Customization
# ============================================================

admin.site.site_header = "PAAIS Academy Administration"
admin.site.site_title = "PAAIS Academy Admin"
admin.site.index_title = "Welcome to PAAIS Academy"