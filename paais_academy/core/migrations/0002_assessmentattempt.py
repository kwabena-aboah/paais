from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssessmentAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=0)),
                ('correct_answers', models.IntegerField(default=0)),
                ('total_questions', models.IntegerField(default=0)),
                ('passed', models.BooleanField(default=False)),
                ('answers', models.JSONField(default=list)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_attempts', to='core.lesson')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_attempts', to='auth.user')),
            ],
            options={'ordering': ['-submitted_at']},
        ),
    ]
