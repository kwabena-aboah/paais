from django import forms


class AILessonGenerationForm(forms.Form):
    topic = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'autofocus': True}),
        help_text='Describe the lesson you want to draft.',
    )
    level = forms.ChoiceField(choices=(
        ('starter', 'Starter'),
        ('practitioner', 'Practitioner'),
        ('champion', 'Champion'),
    ), initial='starter')
    duration_minutes = forms.IntegerField(
        required=False, min_value=5, max_value=180,
        help_text='Optional target duration in minutes.',
    )
    run_in_background = forms.BooleanField(
        required=False,
        label='Run in background',
        help_text='Use Celery for slow generation or batch work.',
    )
