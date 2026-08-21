from celery import shared_task
from django.contrib.auth.models import User

from .ai_generator import AIGenerationError, generate_lesson
from .models import AIGenerationLog, Lesson, Notification, Track


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def generate_lesson_task(self, track_id, topic, level='starter', duration_minutes=None, triggered_by_id=None):
    track = Track.objects.get(pk=track_id)
    user = User.objects.filter(pk=triggered_by_id).first() if triggered_by_id else None
    try:
        data = generate_lesson(track, topic, level, duration_minutes, triggered_by=user)
        lesson = Lesson.objects.create(
            track=track,
            is_published=False,
            order=track.lessons.count(),
            **data.to_lesson_fields(),
        )
        if data.generation_log_id:
            AIGenerationLog.objects.filter(pk=data.generation_log_id).update(lesson=lesson)
        if user:
            Notification.objects.create(
                user=user,
                type='lesson_new',
                title='AI lesson draft ready',
                message=f'Review the draft: {lesson.title}',
                link=f'/admin/core/lesson/{lesson.pk}/change/',
            )
        return str(lesson.pk)
    except AIGenerationError:
        raise
