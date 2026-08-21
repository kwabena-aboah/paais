from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('core', '0003_learning_features')]

    operations = [
        migrations.CreateModel(
            name='AIGenerationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=255)),
                ('level', models.CharField(blank=True, max_length=20)),
                ('model', models.CharField(blank=True, max_length=100)),
                ('input_tokens', models.IntegerField(default=0)),
                ('output_tokens', models.IntegerField(default=0)),
                ('duration_seconds', models.FloatField(default=0)),
                ('success', models.BooleanField(default=False)),
                ('error_message', models.TextField(blank=True)),
                ('prompt_text', models.TextField(blank=True, help_text='Exact prompt sent to the model.')),
                ('response_json', models.JSONField(blank=True, default=dict, help_text='Structured model output for audit/debugging.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('lesson', models.ForeignKey(blank=True, help_text='Set once the draft lesson is created from this call.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ai_generation_logs', to='core.lesson')),
                ('track', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ai_generation_logs', to='core.track')),
                ('triggered_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ai_generation_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
