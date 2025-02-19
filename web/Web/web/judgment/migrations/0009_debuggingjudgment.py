# Generated by Django 3.0.5 on 2022-06-04 02:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_session_show_debugging_content'),
        ('judgment', '0008_judgment_is_seed'),
    ]

    operations = [
        migrations.CreateModel(
            name='DebuggingJudgment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_id', models.CharField(max_length=512)),
                ('relevance', models.IntegerField(blank=True, choices=[(2, 'Highly Relevant'), (1, 'Relevant'), (0, 'Non-Relevant')], null=True, verbose_name='Relevance')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Session')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'doc_id', 'session')},
                'index_together': {('user', 'doc_id', 'session')},
            },
        ),
    ]
