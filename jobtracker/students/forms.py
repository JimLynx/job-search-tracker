from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StudentProfile, JobApplication, NetworkingContact, WeeklyActivityTarget, DirectApproach, RecruiterContact, Interview, LinkedInPost

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='First name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Last name')

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

class StudentProfileForm(forms.ModelForm):
    linkedin = forms.URLField(
        required=True,
        label="LinkedIn URL",
        widget=forms.URLInput(attrs={
            'placeholder': 'https://www.linkedin.com/in/[your_username]'
        })
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),  # Set to 2 rows for a smaller height
        required=False,
        label="Bio"
    )

    class Meta:
        model = StudentProfile
        fields = ['linkedin', 'github', 'bio']  # Add 'github' here

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            'date_applied',
            'website',
            'job_title',
            'company_name',
            'application_url',
            'contact',
            'response',
            'notes',
        ]
        widgets = {
            'date_applied': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
            'application_url': forms.TextInput(attrs={'placeholder': 'Paste or type the URL'}),
        }

    def clean_application_url(self):
        url = self.cleaned_data.get('application_url')
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url

class NetworkingContactForm(forms.ModelForm):
    class Meta:
        model = NetworkingContact
        fields = ['date', 'contact_name', 'conversation', 'outcome', 'notes', 'accepted']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, widget=forms.EmailInput(attrs={'autofocus': True}))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            user = User.objects.filter(email=email).first()
            if not user:
                raise forms.ValidationError("Invalid email or password.")
            self.user_cache = authenticate(username=user.username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid email or password.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")
        return self.cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)

class WeeklyActivityTargetForm(forms.ModelForm):
    class Meta:
        model = WeeklyActivityTarget
        fields = [
            'applications_target',
            'networking_contacts_target',
            'linkedin_connections_target',
            'direct_approach_target',
            'linkedin_posts_target',
            'recruiters_target',
            'interviews_target',
        ]

class DirectApproachForm(forms.ModelForm):
    class Meta:
        model = DirectApproach
        fields = [
            'targeting', 'location', 'contact', 'reached_out', 'date',
            'approach_method', 'response', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class RecruiterContactForm(forms.ModelForm):
    class Meta:
        model = RecruiterContact
        fields = ['date', 'role', 'agency', 'stage', 'follow_up', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['date', 'role', 'company', 'contact', 'stage', 'notes', 'follow_up']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

class LinkedInPostForm(forms.ModelForm):
    class Meta:
        model = LinkedInPost
        fields = ['date_posted', 'subject', 'post_type']
        widgets = {
            'date_posted': forms.DateInput(attrs={'type': 'date'}),
        }