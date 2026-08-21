from django.core.management.base import BaseCommand, CommandError
from core.ai_generator import AIGenerationError, generate_lesson
from core.models import Lesson, Track


class Command(BaseCommand):
    help = 'Generate one or more unpublished lesson drafts with AI.'

    def add_arguments(self, parser):
        parser.add_argument('--topic', required=True)
        parser.add_argument('--track', required=False, help='Track UUID or function slug. Required when multiple tracks exist.')
        parser.add_argument('--level', choices=('starter', 'practitioner', 'champion'), default='starter')
        parser.add_argument('--duration-minutes', type=int, default=None)
        parser.add_argument('--count', type=int, default=1)

    def handle(self, *args, **options):
        if options['count'] < 1:
            raise CommandError('--count must be at least 1.')
        track_ref = options.get('track')
        if track_ref:
            try:
                track = Track.objects.get(pk=track_ref)
            except (Track.DoesNotExist, ValueError):
                try:
                    track = Track.objects.get(function=track_ref)
                except Track.DoesNotExist as exc:
                    raise CommandError('Track not found. Use its UUID or function slug.') from exc
        else:
            tracks = Track.objects.filter(is_active=True)
            if tracks.count() != 1:
                raise CommandError('Pass --track when more than one active track exists.')
            track = tracks.first()

        for index in range(options['count']):
            try:
                content = generate_lesson(
                    track=track,
                    topic=options['topic'],
                    level=options['level'],
                    duration_minutes=options['duration_minutes'],
                )
            except AIGenerationError as exc:
                raise CommandError(f'Generation failed on item {index + 1}: {exc}') from exc
            lesson = Lesson.objects.create(
                track=track,
                is_published=False,
                order=track.lessons.count(),
                **content.to_lesson_fields(),
            )
            self.stdout.write(self.style.SUCCESS(f'Created draft {lesson.pk}: {lesson.title}'))
