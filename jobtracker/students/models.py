from django.contrib.auth.models import User
from django.db import models
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)

    def __str__(self):
        return self.user.username

class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_applied = models.DateField()
    website = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    application_url = models.URLField(blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True)
    response = models.CharField(max_length=10, choices=[('yes', 'Yes'), ('not_yet', 'Not yet')], default='not_yet')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.company_name} - {self.job_title}"

class NetworkingContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=100)
    contact_role = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    request_sent = models.DateField()  # NEW: When the request was sent
    accepted = models.BooleanField(default=False)
    accepted_date = models.DateField(null=True, blank=True)  # Optional: when accepted
    conversation = models.BooleanField(default=False)
    conversation_date = models.DateField(null=True, blank=True)  # Optional: when conversation happened
    outcome = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.contact_name} ({self.company})"

class WeeklyActivityTarget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    week_start = models.DateField()  # Monday of the week
    applications_target = models.PositiveIntegerField(default=10)
    networking_contacts_target = models.PositiveIntegerField(default=40)
    linkedin_connections_target = models.PositiveIntegerField(default=20)
    direct_approach_target = models.PositiveIntegerField(default=5)
    linkedin_posts_target = models.PositiveIntegerField(default=1)
    recruiters_target = models.PositiveIntegerField(default=0)
    interviews_target = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'week_start')
        ordering = ['-week_start']

    def __str__(self):
        return f"{self.user.username} - {self.week_start}"

class DirectApproach(models.Model):
    REACHED_OUT_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('in_progress', 'In Progress'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    targeting = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=255)
    reached_out = models.CharField(max_length=12, choices=REACHED_OUT_CHOICES, default='no')
    date = models.DateField()
    approach_method = models.CharField(max_length=255)
    response = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.targeting} - {self.contact}"

class RecruiterContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    agency = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    contact = models.CharField(max_length=100, blank=True)  # Add this line
    stage = models.CharField(
        max_length=32,
        choices=[
            ('cv_submitted', 'CV submitted'),
            ('phone_screen', 'Phone screen'),
            ('unsuccessful', 'Unsuccessful'),
            ('video_interview', 'Video interview'),
        ],
        default='cv_submitted'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.role} at {self.agency} ({self.date})"

class Interview(models.Model):
    STAGE_CHOICES = [
        ('phone_screen', 'Phone screen'),
        ('video_interview', 'Video interview'),
        ('technical_assessment', 'Technical assessment'),
        ('one_way_video', 'One-way video interview'),
        ('face_to_face', 'Face to face interview'),
        ('final', 'Final interview'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    role = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES)
    notes = models.TextField(blank=True)
    follow_up = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.role} at {self.company} ({self.date})"

class LinkedInPost(models.Model):
    POST_TYPE_CHOICES = [
        ('personal_info', 'Personal Info'),
        ('project', 'Project'),
        ('shared_teammates_post', 'Shared teammates post'),
        ('event', 'Event'),
        ('industry_content', 'Industry content'),
        # Add more as needed
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateField()
    subject = models.CharField(max_length=255)
    post_type = models.CharField(max_length=30, choices=POST_TYPE_CHOICES)

    def __str__(self):
        return f"{self.subject} ({self.get_post_type_display()}) - {self.date_posted}"

class LinkedInConnection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # ...other fields...

class NetworkingContactForm(forms.ModelForm):
    class Meta:
        model = NetworkingContact
        fields = [
            'request_sent', 'contact_name', 'contact_role', 'company',
            'accepted', 'accepted_date', 'conversation', 'conversation_date',
            'outcome', 'notes'
        ]

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email}: {self.message[:50]}"
