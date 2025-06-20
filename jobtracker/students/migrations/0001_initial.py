# Generated by Django 5.2.1 on 2025-06-04 10:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectApproach',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('targeting', models.CharField(max_length=255)),
                ('location', models.CharField(blank=True, max_length=255)),
                ('contact', models.CharField(max_length=255)),
                ('reached_out', models.CharField(choices=[('yes', 'Yes'), ('no', 'No'), ('in_progress', 'In Progress')], default='no', max_length=12)),
                ('date', models.DateField()),
                ('approach_method', models.CharField(max_length=255)),
                ('response', models.CharField(choices=[('yes', 'Yes'), ('no', 'No')], default='no', max_length=3)),
                ('notes', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('role', models.CharField(max_length=255)),
                ('company', models.CharField(max_length=255)),
                ('contact', models.CharField(max_length=255)),
                ('stage', models.CharField(choices=[('phone_screen', 'Phone screen'), ('video_interview', 'Video interview'), ('technical_assessment', 'Technical assessment'), ('one_way_video', 'One-way video interview'), ('face_to_face', 'Face to face interview'), ('final', 'Final interview')], max_length=30)),
                ('notes', models.TextField(blank=True)),
                ('follow_up', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_applied', models.DateField()),
                ('website', models.CharField(max_length=255)),
                ('job_title', models.CharField(max_length=255)),
                ('company_name', models.CharField(max_length=255)),
                ('application_url', models.URLField(blank=True, null=True)),
                ('contact', models.CharField(blank=True, max_length=255)),
                ('response', models.CharField(choices=[('yes', 'Yes'), ('not_yet', 'Not yet')], default='not_yet', max_length=10)),
                ('notes', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LinkedInConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LinkedInPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_posted', models.DateField()),
                ('subject', models.CharField(max_length=255)),
                ('post_type', models.CharField(choices=[('personal_info', 'Personal Info'), ('project', 'Project'), ('shared_teammates_post', 'Shared teammates post'), ('event', 'Event'), ('industry_content', 'Industry content')], max_length=30)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NetworkingContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('contact_name', models.CharField(max_length=255)),
                ('contact_role', models.CharField(max_length=255)),
                ('company', models.CharField(max_length=255)),
                ('conversation', models.BooleanField(default=False)),
                ('outcome', models.CharField(blank=True, max_length=255)),
                ('notes', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RecruiterContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('role', models.CharField(max_length=255)),
                ('agency', models.CharField(max_length=255)),
                ('stage', models.CharField(max_length=255)),
                ('follow_up', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True)),
                ('linkedin', models.URLField(blank=True)),
                ('github', models.URLField(blank=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WeeklyActivityTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_start', models.DateField()),
                ('applications_target', models.PositiveIntegerField(default=10)),
                ('networking_contacts_target', models.PositiveIntegerField(default=40)),
                ('linkedin_connections_target', models.PositiveIntegerField(default=20)),
                ('direct_approach_target', models.PositiveIntegerField(default=5)),
                ('linkedin_posts_target', models.PositiveIntegerField(default=1)),
                ('recruiters_target', models.PositiveIntegerField(default=0)),
                ('interviews_target', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-week_start'],
                'unique_together': {('user', 'week_start')},
            },
        ),
    ]
