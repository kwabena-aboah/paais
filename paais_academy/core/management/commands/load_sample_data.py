"""
Django Management Command to Load Sample Initial Data
Usage: python manage.py load_sample_tracks

This command creates:
1. Default platform settings
2. All 7 function tracks
3. Sample lessons for each track
4. Sample users for testing
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    PlatformSettings, Track, Lesson, UserProfile, OTPVerification
)
from datetime import timedelta
from django.utils.timezone import now


class Command(BaseCommand):
    help = 'Load sample initial data for PAAIS Academy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing data before loading',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Deleting existing data...'))
            Track.objects.all().delete()
            PlatformSettings.objects.all().delete()

        self.load_platform_settings()
        self.load_tracks_and_lessons()
        self.load_sample_users()

        self.stdout.write(self.style.SUCCESS('✓ Sample data loaded successfully!'))

    def load_platform_settings(self):
        """Load default platform settings"""
        settings, created = PlatformSettings.objects.get_or_create(
            defaults={
                'site_name': 'PAAIS Academy',
                'site_description': 'Learn the AI tools that do your everyday work',
                'primary_color': '#0A0A33',      # Navy
                'secondary_color': '#E900FF',    # Magenta
                'accent_color': '#2EE6D6',       # Cyan
                'support_email': 'support@paaisacademy.com',
                'enable_paystack': True,
                'enable_ai_features': True,
                'enable_marketplace': True,
                'enable_certificates': True,
                'footer_text': '© 2026 Pan African AI Summits & Corporate Training Ltd (PACT)',
            }
        )

        status = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'✓ Platform Settings {status}'))

    def load_tracks_and_lessons(self):
        """Load all 7 function tracks with sample lessons"""

        tracks_data = [
            {
                'function': 'marketing',
                'name': 'Marketing & Communications',
                'description': 'Campaign briefs, social content, newsletters and reports — produced in half the time.',
                'pitch': 'Campaign briefs, social content, newsletters and reports — produced in half the time.',
                'is_featured': True,
                'lessons': [
                    {
                        'title': 'Draft a full campaign brief from three bullet points',
                        'description': 'Turn scattered ideas into a structured brief your team can execute.',
                        'duration': 12,
                        'level': 'starter',
                        'sample_prompt': 'Create a marketing brief from these three points...'
                    },
                    {
                        'title': 'Generate a month of social posts in your brand voice',
                        'description': 'Feed the AI your best past posts and produce a consistent content calendar.',
                        'duration': 18,
                        'level': 'starter',
                        'sample_prompt': 'Generate 30 social media posts in the style of...'
                    },
                    {
                        'title': 'Summarise campaign performance into an executive update',
                        'description': 'From messy analytics export to a one-page leadership summary.',
                        'duration': 15,
                        'level': 'practitioner',
                        'sample_prompt': 'Summarize these analytics into an executive brief...'
                    },
                ]
            },
            {
                'function': 'sales',
                'name': 'Sales & Business Development',
                'description': 'Prospecting, proposals and follow-ups that write themselves — so you spend time selling.',
                'pitch': 'Prospecting, proposals and follow-ups that write themselves — so you spend time selling.',
                'is_featured': True,
                'lessons': [
                    {
                        'title': 'Research a prospect and draft a personalised opener',
                        'description': 'Company research plus first-touch email in one sitting.',
                        'duration': 14,
                        'level': 'starter',
                        'sample_prompt': 'Research this company and write a personalized cold email...'
                    },
                    {
                        'title': 'Turn a discovery call transcript into a proposal outline',
                        'description': 'Never start a proposal from a blank page again.',
                        'duration': 20,
                        'level': 'practitioner',
                        'sample_prompt': 'Extract key requirements from this call transcript...'
                    },
                ]
            },
            {
                'function': 'finance',
                'name': 'Finance & Accounting',
                'description': 'Cleaner spreadsheets, faster reconciliations, clearer reports.',
                'pitch': 'Cleaner spreadsheets, faster reconciliations, clearer reports.',
                'is_featured': False,
                'lessons': [
                    {
                        'title': 'Clean a messy spreadsheet with AI-written formulas',
                        'description': 'Describe the problem in plain English; get the formula that fixes it.',
                        'duration': 16,
                        'level': 'starter',
                        'sample_prompt': 'Create an Excel formula that does...'
                    },
                    {
                        'title': 'Draft variance commentary for your monthly pack',
                        'description': 'From raw numbers to board-ready narrative.',
                        'duration': 18,
                        'level': 'practitioner',
                        'sample_prompt': 'Write variance commentary for these numbers...'
                    },
                ]
            },
            {
                'function': 'hr',
                'name': 'Human Resources',
                'description': 'Job descriptions, CV screening, policies and people communications — humanised and faster.',
                'pitch': 'Job descriptions, CV screening, policies and people communications — humanised and faster.',
                'is_featured': False,
                'lessons': [
                    {
                        'title': 'Screen a stack of CVs against a role scorecard',
                        'description': 'Fair, consistent shortlisting with an auditable rationale.',
                        'duration': 15,
                        'level': 'starter',
                        'sample_prompt': 'Score these CVs against our requirements...'
                    },
                    {
                        'title': 'Write a job description that attracts, not lists',
                        'description': 'Lead with the problem the hire will solve.',
                        'duration': 12,
                        'level': 'starter',
                        'sample_prompt': 'Write a compelling job description for...'
                    },
                ]
            },
            {
                'function': 'operations',
                'name': 'Operations & Supply Chain',
                'description': 'SOPs, vendor comms and process documentation without the admin drag.',
                'pitch': 'SOPs, vendor comms and process documentation without the admin drag.',
                'is_featured': False,
                'lessons': [
                    {
                        'title': 'Turn a process walkthrough into a clean SOP',
                        'description': 'Record how you work; get documentation your team can follow.',
                        'duration': 18,
                        'level': 'starter',
                        'sample_prompt': 'Create an SOP from this process description...'
                    },
                ]
            },
            {
                'function': 'customer_service',
                'name': 'Customer Service',
                'description': 'Faster, kinder, more consistent responses across every channel.',
                'pitch': 'Faster, kinder, more consistent responses across every channel.',
                'is_featured': False,
                'lessons': [
                    {
                        'title': 'Build a response library for your top 20 queries',
                        'description': 'Consistent answers your whole team can use.',
                        'duration': 10,
                        'level': 'starter',
                        'sample_prompt': 'Create response templates for these common questions...'
                    },
                ]
            },
            {
                'function': 'founder',
                'name': 'Founder / SME Owner',
                'description': 'One person, every function. AI as your first employee.',
                'pitch': 'One person, every function. AI as your first employee.',
                'is_featured': False,
                'lessons': [
                    {
                        'title': 'Write your one-page business plan with AI as co-founder',
                        'description': 'Pressure-test your model with structured questioning.',
                        'duration': 20,
                        'level': 'starter',
                        'sample_prompt': 'Help me structure a business plan for...'
                    },
                ]
            },
        ]

        for idx, track_data in enumerate(tracks_data):
            track, created = Track.objects.get_or_create(
                function=track_data['function'],
                defaults={
                    'name': track_data['name'],
                    'description': track_data['description'],
                    'pitch': track_data['pitch'],
                    'is_featured': track_data.get('is_featured', False),
                    'order': idx,
                    'is_active': True,
                    'is_free': True,
                }
            )

            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  ✓ Track: {track.name} {status}')

            # Load lessons for this track
            for lesson_idx, lesson_data in enumerate(track_data['lessons']):
                lesson, _ = Lesson.objects.get_or_create(
                    track=track,
                    title=lesson_data['title'],
                    defaults={
                        'description': lesson_data['description'],
                        'duration_minutes': lesson_data['duration'],
                        'level': lesson_data['level'],
                        'content_html': f'<h2>{lesson_data["title"]}</h2><p>{lesson_data["description"]}</p>',
                        'sample_prompt': lesson_data['sample_prompt'],
                        'ai_tools_covered': ['ChatGPT', 'Claude', 'Perplexity'],
                        'objectives': [
                            f'Master {lesson_data["title"].lower()}',
                            'Learn practical AI application',
                            'Get work done faster'
                        ],
                        'quiz_questions': [
                            {
                                'question': 'What was the main topic of this lesson?',
                                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                                'correct': 0
                            }
                        ],
                        'order': lesson_idx,
                        'is_published': True,
                    }
                )
                self.stdout.write(f'    ✓ Lesson: {lesson.title}')

    def load_sample_users(self):
        """Load sample users for testing"""

        sample_users = [
            {
                'username': 'ama_marketing',
                'email': 'ama@example.com',
                'first_name': 'Ama',
                'last_name': 'Mensah',
                'password': 'testpass123',
                'profile': {
                    'phone': '+233XXXXXXXXX1',
                    'business_function': 'marketing',
                    'country': 'gh',
                    'company_name': 'Tech Startup Ghana',
                    'is_verified': True,
                }
            },
            {
                'username': 'kofi_sales',
                'email': 'kofi@example.com',
                'first_name': 'Kofi',
                'last_name': 'Owusu',
                'password': 'testpass123',
                'profile': {
                    'phone': '+233XXXXXXXXX2',
                    'business_function': 'sales',
                    'country': 'gh',
                    'company_name': 'Business Solutions Ltd',
                    'is_verified': True,
                }
            },
            {
                'username': 'abena_finance',
                'email': 'abena@example.com',
                'first_name': 'Abena',
                'last_name': 'Boateng',
                'password': 'testpass123',
                'profile': {
                    'phone': '+233XXXXXXXXX3',
                    'business_function': 'finance',
                    'country': 'gh',
                    'company_name': 'Finance Corp Africa',
                    'is_verified': True,
                }
            },
        ]

        for user_data in sample_users:
            profile_data = user_data.pop('profile')
            password = user_data.pop('password')

            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )

            if created:
                user.set_password(password)
                user.save()

            # Create or update profile
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults=profile_data
            )

            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'✓ Sample user {user.username} {status}')

        self.stdout.write(self.style.WARNING('\nTest user credentials:'))
        for user in sample_users:
            self.stdout.write(f'  Username: {user["username"]}, Password: testpass123')
