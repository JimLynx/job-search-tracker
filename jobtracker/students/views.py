from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from datetime import date, datetime, timedelta
from django.utils import timezone

from .forms import (
    StudentProfileForm, JobApplicationForm, WeeklyActivityTargetForm,
    NetworkingContactForm, EmailAuthenticationForm, DirectApproachForm,
    RecruiterContactForm, InterviewForm, LinkedInPostForm, CustomUserCreationForm
)
from .models import (
    StudentProfile, JobApplication, NetworkingContact, WeeklyActivityTarget,
    DirectApproach, RecruiterContact, Interview, LinkedInPost, LinkedInConnection, Notification
)

User = get_user_model()

def get_notification_context(request):
    unread_notifications = request.user.notification_set.filter(read=False).count()
    notifications = request.user.notification_set.order_by('-created_at')[:5]
    return {
        'unread_notifications': unread_notifications,
        'notifications': notifications,
    }

# --- Profile and Auth Views (function-based for simplicity) ---

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "There was an error with your registration. Please check the form.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'students/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful! Welcome back.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    else:
        form = EmailAuthenticationForm()
    return render(request, 'students/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- Profile View (function-based for custom logic) ---

@login_required
def profile(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was updated successfully!")
            return redirect('dashboard')
    else:
        form = StudentProfileForm(instance=profile)
    context = {'form': form}
    context.update(get_notification_context(request))
    return render(request, 'students/profile.html', context)

# --- CBV CRUD for JobApplication ---

class JobApplicationListView(LoginRequiredMixin, ListView):
    model = JobApplication
    template_name = 'students/applications.html'
    context_object_name = 'applications'

    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(company_name__icontains=q) |
                Q(job_title__icontains=q) |
                Q(notes__icontains=q)
            )
        return qs.order_by('-date_applied')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = JobApplicationForm()
        context['query'] = self.request.GET.get('q', '')
        context.update(get_notification_context(self.request))
        return context

class JobApplicationCreateView(LoginRequiredMixin, CreateView):
    model = JobApplication
    form_class = JobApplicationForm
    template_name = 'students/add_application.html'
    success_url = reverse_lazy('applications')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

class JobApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = JobApplication
    form_class = JobApplicationForm
    template_name = 'students/edit_application.html'
    success_url = reverse_lazy('applications')

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

class JobApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = JobApplication
    template_name = 'students/delete_application.html'
    success_url = reverse_lazy('applications')

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

# --- CBV CRUD for NetworkingContact ---

class NetworkingContactListView(LoginRequiredMixin, ListView):
    model = NetworkingContact
    template_name = 'students/networking.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(contact_name__icontains=q) |
                Q(company__icontains=q) |
                Q(contact_role__icontains=q)
            )
        return qs.order_by('-request_sent')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = NetworkingContactForm()
        context['query'] = self.request.GET.get('q', '')
        context.update(get_notification_context(self.request))
        return context

class NetworkingContactCreateView(LoginRequiredMixin, CreateView):
    model = NetworkingContact
    form_class = NetworkingContactForm
    template_name = 'students/add_contact.html'
    success_url = reverse_lazy('networking')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

class NetworkingContactUpdateView(LoginRequiredMixin, UpdateView):
    model = NetworkingContact
    form_class = NetworkingContactForm
    template_name = 'students/edit_contact.html'
    success_url = reverse_lazy('networking')

    def get_queryset(self):
        return NetworkingContact.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

class NetworkingContactDeleteView(LoginRequiredMixin, DeleteView):
    model = NetworkingContact
    template_name = 'students/delete_contact.html'
    success_url = reverse_lazy('networking')

    def get_queryset(self):
        return NetworkingContact.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

# --- Repeat for RecruiterContact, DirectApproach, Interview, LinkedInPost ---

class RecruiterContactListView(LoginRequiredMixin, ListView):
    model = RecruiterContact
    template_name = 'students/recruiters.html'
    context_object_name = 'recruiters'

    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(role__icontains=q) |
                Q(agency__icontains=q) |
                Q(stage__icontains=q)
            )
        return qs.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RecruiterContactForm()
        context['query'] = self.request.GET.get('q', '')
        context.update(get_notification_context(self.request))
        return context

class RecruiterContactCreateView(LoginRequiredMixin, CreateView):
    model = RecruiterContact
    form_class = RecruiterContactForm
    template_name = 'students/add_recruiter.html'
    success_url = reverse_lazy('recruiters')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

class RecruiterContactUpdateView(LoginRequiredMixin, UpdateView):
    model = RecruiterContact
    form_class = RecruiterContactForm
    template_name = 'students/edit_recruiter.html'
    success_url = reverse_lazy('recruiters')

    def get_queryset(self):
        return RecruiterContact.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

class RecruiterContactDeleteView(LoginRequiredMixin, DeleteView):
    model = RecruiterContact
    template_name = 'students/delete_recruiter.html'
    success_url = reverse_lazy('recruiters')

    def get_queryset(self):
        return RecruiterContact.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

# --- DirectApproach ---

class DirectApproachListView(LoginRequiredMixin, ListView):
    model = DirectApproach
    template_name = 'students/direct_approach.html'
    context_object_name = 'approaches'

    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(targeting__icontains=q) |
                Q(location__icontains=q) |
                Q(contact__icontains=q)
            )
        return qs.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DirectApproachForm()
        context['query'] = self.request.GET.get('q', '')
        context.update(get_notification_context(self.request))
        return context

class DirectApproachCreateView(LoginRequiredMixin, CreateView):
    model = DirectApproach
    form_class = DirectApproachForm
    template_name = 'students/add_direct_approach.html'
    success_url = reverse_lazy('direct_approach')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

class DirectApproachUpdateView(LoginRequiredMixin, UpdateView):
    model = DirectApproach
    form_class = DirectApproachForm
    template_name = 'students/edit_direct_approach.html'
    success_url = reverse_lazy('direct_approach')

    def get_queryset(self):
        return DirectApproach.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

class DirectApproachDeleteView(LoginRequiredMixin, DeleteView):
    model = DirectApproach
    template_name = 'students/delete_direct_approach.html'
    success_url = reverse_lazy('direct_approach')

    def get_queryset(self):
        return DirectApproach.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

# --- Interview ---

class InterviewListView(LoginRequiredMixin, ListView):
    model = Interview
    template_name = 'students/interviews.html'
    context_object_name = 'interviews'

    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(role__icontains=q) |
                Q(company__icontains=q) |
                Q(contact__icontains=q)
            )
        return qs.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = InterviewForm()
        context['query'] = self.request.GET.get('q', '')
        context.update(get_notification_context(self.request))
        return context

class InterviewCreateView(LoginRequiredMixin, CreateView):
    model = Interview
    form_class = InterviewForm
    template_name = 'students/add_interview.html'
    success_url = reverse_lazy('interviews')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        Notification.objects.create(
            user=self.request.user,
            message=f"Interview scheduled for {form.instance.role} at {form.instance.company} on {form.instance.date}.",
            url="/interviews/"
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

class InterviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Interview
    form_class = InterviewForm
    template_name = 'students/edit_interview.html'
    success_url = reverse_lazy('interviews')

    def get_queryset(self):
        return Interview.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

class InterviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Interview
    template_name = 'students/delete_interview.html'
    success_url = reverse_lazy('interviews')

    def get_queryset(self):
        return Interview.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

# --- LinkedInPost ---

class LinkedInPostListView(LoginRequiredMixin, ListView):
    model = LinkedInPost
    template_name = 'students/linkedin_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(subject__icontains=q) |
                Q(post_type__icontains=q)
            )
        return qs.order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LinkedInPostForm()
        context['query'] = self.request.GET.get('q', '')
        context.update(get_notification_context(self.request))
        return context

class LinkedInPostCreateView(LoginRequiredMixin, CreateView):
    model = LinkedInPost
    form_class = LinkedInPostForm
    template_name = 'students/add_linkedin_post.html'
    success_url = reverse_lazy('linkedin_posts')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

class LinkedInPostUpdateView(LoginRequiredMixin, UpdateView):
    model = LinkedInPost
    form_class = LinkedInPostForm
    template_name = 'students/edit_linkedin_post.html'
    success_url = reverse_lazy('linkedin_posts')

    def get_queryset(self):
        return LinkedInPost.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

class LinkedInPostDeleteView(LoginRequiredMixin, DeleteView):
    model = LinkedInPost
    template_name = 'students/delete_linkedin_post.html'
    success_url = reverse_lazy('linkedin_posts')

    def get_queryset(self):
        return LinkedInPost.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_notification_context(self.request))
        return context

# --- Other Views (dashboard, admin, etc.) can remain function-based for now ---

@login_required
def dashboard(request):
    today = timezone.localdate()
    week_str = request.GET.get('week')
    if week_str:
        week_start = datetime.strptime(week_str, "%Y-%m-%d").date()
    else:
        week_start = today - timedelta(days=today.weekday())
    week_start_dt = timezone.make_aware(datetime.combine(week_start, datetime.min.time()))
    week_end_dt = timezone.make_aware(datetime.combine(week_start + timedelta(days=7), datetime.min.time()))
    target, _ = WeeklyActivityTarget.objects.get_or_create(user=request.user, week_start=week_start)

    # Networking metrics
    contacts = NetworkingContact.objects.filter(
        user=request.user,
        request_sent__gte=week_start,
        request_sent__lt=week_start + timedelta(days=7)
    )
    num_contacts = contacts.count()
    sent_count = num_contacts
    accepted_count = contacts.filter(accepted=True).count()
    conversation_count = contacts.filter(conversation=True).count()

    def progress(actual, target):
        return int(min((actual / target) * 100, 100)) if target else 0

    context = {
        'num_contacts': num_contacts,
        'max_contacts': target.networking_contacts_target,
        'networking_progress': progress(num_contacts, target.networking_contacts_target),
        'sent_count': sent_count,
        'accepted_count': accepted_count,
        'conversation_count': conversation_count,
        'sent_target': 40,
        'accepted_target': 20,
        'conversation_target': 5,
        'percent_sent': progress(sent_count, 40),
        'percent_accepted': progress(accepted_count, 20),
        'percent_conversed': progress(conversation_count, 5),

        'num_applications': JobApplication.objects.filter(
            user=request.user,
            date_applied__gte=week_start,
            date_applied__lt=week_start + timedelta(days=7)
        ).count(),
        'max_applications': target.applications_target,
        'applications_progress': progress(
            JobApplication.objects.filter(
                user=request.user,
                date_applied__gte=week_start,
                date_applied__lt=week_start + timedelta(days=7)
            ).count(),
            target.applications_target
        ),
        'num_linkedin_connections': LinkedInConnection.objects.filter(
            user=request.user,
            created_at__gte=week_start_dt,
            created_at__lt=week_end_dt
        ).count(),
        'max_linkedin_connections': target.linkedin_connections_target,
        'linkedin_connections_progress': progress(
            LinkedInConnection.objects.filter(
                user=request.user,
                created_at__gte=week_start_dt,
                created_at__lt=week_end_dt
            ).count(),
            target.linkedin_connections_target
        ),
        'num_direct_approach': DirectApproach.objects.filter(
            user=request.user,
            date__gte=week_start,
            date__lt=week_start + timedelta(days=7)
        ).count(),
        'max_direct_approach': target.direct_approach_target,
        'direct_approach_progress': progress(
            DirectApproach.objects.filter(
                user=request.user,
                date__gte=week_start,
                date__lt=week_start + timedelta(days=7)
            ).count(),
            target.direct_approach_target
        ),
        # Recruiters and Interviews are accumulative (all-time)
        'num_recruiters': RecruiterContact.objects.filter(user=request.user).count(),
        'max_recruiters': target.recruiters_target,
        'recruiters_progress': progress(
            RecruiterContact.objects.filter(user=request.user).count(),
            target.recruiters_target
        ),
        'num_interviews': Interview.objects.filter(user=request.user).count(),
        'max_interviews': target.interviews_target,
        'interviews_progress': progress(
            Interview.objects.filter(user=request.user).count(),
            target.interviews_target
        ),
        'num_linkedin_posts': LinkedInPost.objects.filter(
            user=request.user,
            date_posted__gte=week_start,
            date_posted__lt=week_start + timedelta(days=7)
        ).count(),
        'max_linkedin_posts': target.linkedin_posts_target,
        'linkedin_posts_progress': progress(
            LinkedInPost.objects.filter(
                user=request.user,
                date_posted__gte=week_start,
                date_posted__lt=week_start + timedelta(days=7)
            ).count(),
            target.linkedin_posts_target
        ),
        'recent_applications': JobApplication.objects.filter(user=request.user).order_by('-date_applied')[:5],
        'week_start': week_start,
        'week_start_display': week_start.strftime('%B %d, %Y'),
        'prev_week': week_start - timedelta(days=7),
        'next_week': week_start + timedelta(days=7),
        'today': today,
    }
    context.update(get_notification_context(request))
    return render(request, 'students/dashboard.html', context)

@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your profile has been deleted.")
        return redirect('welcome')
    context = {}
    context.update(get_notification_context(request))
    return render(request, 'students/delete_profile.html', context)

@login_required
def direct_approach(request):
    query = request.GET.get('q', '')
    approaches = DirectApproach.objects.filter(user=request.user)
    if query:
        approaches = approaches.filter(
            Q(targeting__icontains=query) |
            Q(location__icontains=query) |
            Q(contact__icontains=query)
        )
    approaches = approaches.order_by('-date')

    if request.method == 'POST':
        form = DirectApproachForm(request.POST)
        if form.is_valid():
            approach = form.save(commit=False)
            approach.user = request.user
            approach.save()
            messages.success(request, "Direct approach added successfully!")
            return redirect('direct_approach')
    else:
        form = DirectApproachForm()
    context = {'approaches': approaches, 'form': form}
    context.update(get_notification_context(request))
    return render(request, 'students/direct_approach.html', context)

def tutorial(request):
    return render(request, 'students/tutorial.html')

@login_required
def welcome(request):
    context = {}
    context.update(get_notification_context(request))
    return render(request, 'students/welcome.html', context)

@login_required
def edit_direct_approach(request, pk):
    approach = get_object_or_404(DirectApproach, pk=pk, user=request.user)
    if request.method == 'POST':
        form = DirectApproachForm(request.POST, instance=approach)
        if form.is_valid():
            form.save()
            messages.success(request, "Direct approach updated successfully!")
            return redirect('direct_approach')
    else:
        form = DirectApproachForm(instance=approach)
    context = {'form': form, 'approach': approach}
    context.update(get_notification_context(request))
    return render(request, 'students/edit_direct_approach.html', context)

@login_required
def delete_direct_approach(request, pk):
    approach = get_object_or_404(DirectApproach, pk=pk, user=request.user)
    if request.method == 'POST':
        approach.delete()
        messages.success(request, "Direct approach deleted successfully!")
        return redirect('direct_approach')
    context = {'approach': approach}
    context.update(get_notification_context(request))
    return render(request, 'students/delete_direct_approach.html', context)

@login_required
def recruiters(request):
    query = request.GET.get('q', '')
    recruiters = RecruiterContact.objects.filter(user=request.user)
    if query:
        recruiters = recruiters.filter(
            Q(role__icontains=query) |
            Q(agency__icontains=query) |
            Q(stage__icontains=query)
        )
    recruiters = recruiters.order_by('-date')

    if request.method == 'POST':
        form = RecruiterContactForm(request.POST)
        if form.is_valid():
            recruiter = form.save(commit=False)
            recruiter.user = request.user
            recruiter.save()
            messages.success(request, "Recruiter contact added successfully!")
            return redirect('recruiters')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RecruiterContactForm()
    context = {
        'recruiters': recruiters,
        'form': form,
        'query': query,
    }
    context.update(get_notification_context(request))
    return render(request, 'students/recruiters.html', context)

@login_required
def interviews(request):
    query = request.GET.get('q', '')
    interviews = Interview.objects.filter(user=request.user)
    if query:
        interviews = interviews.filter(
            Q(role__icontains=query) |
            Q(company__icontains=query) |
            Q(contact__icontains=query)
        )
    interviews = interviews.order_by('-date')

    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.user = request.user
            interview.save()
            # Example: Create notification for interview
            Notification.objects.create(
                user=request.user,
                message=f"Interview scheduled for {interview.role} at {interview.company} on {interview.date}.",
                url="/interviews/"
            )
            messages.success(request, "Interview added and reminder created!")
            return redirect('interviews')
    else:
        form = InterviewForm()
    context = {'interviews': interviews, 'form': form}
    context.update(get_notification_context(request))
    return render(request, 'students/interviews.html', context)

@login_required
def edit_interview(request, pk):
    interview = get_object_or_404(Interview, pk=pk, user=request.user)
    if request.method == 'POST':
        form = InterviewForm(request.POST, instance=interview)
        if form.is_valid():
            form.save()
            messages.success(request, "Interview updated successfully!")
            return redirect('interviews')
    else:
        form = InterviewForm(instance=interview)
    context = {'form': form, 'interview': interview}
    context.update(get_notification_context(request))
    return render(request, 'students/edit_interview.html', context)

@login_required
def delete_interview(request, pk):
    interview = get_object_or_404(Interview, pk=pk, user=request.user)
    if request.method == 'POST':
        interview.delete()
        messages.success(request, "Interview deleted successfully!")
        return redirect('interviews')
    context = {'interview': interview}
    context.update(get_notification_context(request))
    return render(request, 'students/delete_interview.html', context)

@login_required
def edit_recruiter(request, pk):
    recruiter = get_object_or_404(RecruiterContact, pk=pk, user=request.user)
    if request.method == 'POST':
        form = RecruiterContactForm(request.POST, instance=recruiter)
        if form.is_valid():
            form.save()
            messages.success(request, "Recruiter contact updated successfully!")
            return redirect('recruiters')
    else:
        form = RecruiterContactForm(instance=recruiter)
    context = {'form': form, 'recruiter': recruiter}
    context.update(get_notification_context(request))
    return render(request, 'students/edit_recruiter.html', context)

@login_required
def delete_recruiter(request, pk):
    recruiter = get_object_or_404(RecruiterContact, pk=pk, user=request.user)
    if request.method == 'POST':
        recruiter.delete()
        messages.success(request, "Recruiter contact deleted successfully!")
        return redirect('recruiters')
    context = {'recruiter': recruiter}
    context.update(get_notification_context(request))
    return render(request, 'students/delete_recruiter.html', context)

@login_required
def linkedin_posts(request):
    query = request.GET.get('q', '')
    posts = LinkedInPost.objects.filter(user=request.user)
    if query:
        posts = posts.filter(
            Q(subject__icontains=query) |
            Q(post_type__icontains=query)
        )
    posts = posts.order_by('-date_posted')

    if request.method == 'POST':
        form = LinkedInPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "LinkedIn post added successfully!")
            return redirect('linkedin_posts')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LinkedInPostForm()
    context = {
        'posts': posts,
        'form': form,
        'query': query,
    }
    context.update(get_notification_context(request))
    return render(request, 'students/linkedin_posts.html', context)

@login_required
def edit_linkedin_post(request, pk):
    post = get_object_or_404(LinkedInPost, pk=pk, user=request.user)
    if request.method == 'POST':
        form = LinkedInPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "LinkedIn post updated successfully!")
            return redirect('linkedin_posts')
    else:
        form = LinkedInPostForm(instance=post)
    context = {'form': form, 'post': post}
    context.update(get_notification_context(request))
    return render(request, 'students/edit_linkedin_post.html', context)

@login_required
def delete_linkedin_post(request, pk):
    post = get_object_or_404(LinkedInPost, pk=pk, user=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, "LinkedIn post deleted successfully!")
        return redirect('linkedin_posts')
    context = {'post': post}
    context.update(get_notification_context(request))
    return render(request, 'students/delete_linkedin_post.html', context)

@login_required
def networking_questions(request):
    context = {}
    context.update(get_notification_context(request))
    return render(request, 'students/networking_questions.html', context)

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    students = User.objects.filter(is_staff=False)
    progress_data = []
    for student in students:
        num_targets = WeeklyActivityTarget.objects.filter(user=student).count()
        progress_data.append({
            'student': student,
            'num_targets': num_targets,
        })
    context = {'progress_data': progress_data}
    context.update(get_notification_context(request))
    return render(request, 'students/admin_dashboard.html', context)

@login_required
def bulk_delete_applications(request):
    if request.method == "POST":
        ids = request.POST.getlist("selected_ids")
        JobApplication.objects.filter(id__in=ids, user=request.user).delete()
    return redirect('applications')

@login_required
def bulk_delete_contacts(request):
    if request.method == "POST":
        ids = request.POST.getlist("selected_ids")
        NetworkingContact.objects.filter(id__in=ids, user=request.user).delete()
    return redirect('networking')

@login_required
def bulk_delete_interviews(request):
    if request.method == "POST":
        ids = request.POST.getlist("selected_ids")
        Interview.objects.filter(id__in=ids, user=request.user).delete()
    return redirect('interviews')

@login_required
def bulk_delete_direct_approach(request):
    if request.method == "POST":
        ids = request.POST.getlist("selected_ids")
        DirectApproach.objects.filter(id__in=ids, user=request.user).delete()
    return redirect('direct_approach')

@login_required
def bulk_delete_recruiters(request):
    if request.method == "POST":
        ids = request.POST.getlist("selected_ids")
        RecruiterContact.objects.filter(id__in=ids, user=request.user).delete()
    return redirect('recruiters')

@login_required
def bulk_delete_linkedin_posts(request):
    if request.method == "POST":
        ids = request.POST.getlist("selected_ids")
        LinkedInPost.objects.filter(id__in=ids, user=request.user).delete()
    return redirect('linkedin_posts')

@login_required
def edit_contact(request, pk):
    contact = get_object_or_404(NetworkingContact, pk=pk, user=request.user)
    if request.method == 'POST':
        form = NetworkingContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, "Contact updated successfully!")
            return redirect('networking')
    else:
        form = NetworkingContactForm(instance=contact)
    context = {'form': form, 'contact': contact}
    context.update(get_notification_context(request))
    return render(request, 'students/edit_contact.html', context)

@login_required
def delete_contact(request, pk):
    contact = get_object_or_404(NetworkingContact, pk=pk, user=request.user)
    if request.method == 'POST':
        contact.delete()
        messages.success(request, "Contact deleted successfully!")
        return redirect('networking')
    context = {'contact': contact}
    context.update(get_notification_context(request))
    return render(request, 'students/delete_contact.html', context)

@login_required
def edit_weekly_targets(request):
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    target, _ = WeeklyActivityTarget.objects.get_or_create(user=request.user, week_start=week_start)

    if request.method == 'POST':
        form = WeeklyActivityTargetForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(request, "Weekly targets updated!")
            return redirect('dashboard')
    else:
        form = WeeklyActivityTargetForm(instance=target)
    context = {'form': form, 'week_start': week_start}
    context.update(get_notification_context(request))
    return render(request, 'students/edit_weekly_targets.html', context)

def add_contact(request):
    if request.method == 'POST':
        form = NetworkingContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Contact added successfully!")
            return redirect('networking')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = NetworkingContactForm()
    context = {'form': form}
    context.update(get_notification_context(request))
    return render(request, 'students/add_contact.html', context)

from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'students/dashboard.html'

    def get_context_data(self, **kwargs):
        from datetime import datetime, timedelta
        from django.utils import timezone

        context = super().get_context_data(**kwargs)
        request = self.request
        today = timezone.localdate()
        week_str = request.GET.get('week')
        if week_str:
            week_start = datetime.strptime(week_str, "%Y-%m-%d").date()
        else:
            week_start = today - timedelta(days=today.weekday())
        week_start_dt = timezone.make_aware(datetime.combine(week_start, datetime.min.time()))
        week_end_dt = timezone.make_aware(datetime.combine(week_start + timedelta(days=7), datetime.min.time()))
        target, _ = WeeklyActivityTarget.objects.get_or_create(user=request.user, week_start=week_start)

        # Networking metrics
        contacts = NetworkingContact.objects.filter(
            user=request.user,
            request_sent__gte=week_start,
            request_sent__lt=week_start + timedelta(days=7)
        )
        num_contacts = contacts.count()
        sent_count = num_contacts
        accepted_count = contacts.filter(accepted=True).count()
        conversation_count = contacts.filter(conversation=True).count()

        def progress(actual, target):
            return int(min((actual / target) * 100, 100)) if target else 0

        context.update({
            'num_contacts': num_contacts,
            'max_contacts': target.networking_contacts_target,
            'networking_progress': progress(num_contacts, target.networking_contacts_target),
            'sent_count': sent_count,
            'accepted_count': accepted_count,
            'conversation_count': conversation_count,
            'sent_target': 40,
            'accepted_target': 20,
            'conversation_target': 5,
            'percent_sent': progress(sent_count, 40),
            'percent_accepted': progress(accepted_count, 20),
            'percent_conversed': progress(conversation_count, 5),

            'num_applications': JobApplication.objects.filter(
                user=request.user,
                date_applied__gte=week_start,
                date_applied__lt=week_start + timedelta(days=7)
            ).count(),
            'max_applications': target.applications_target,
            'applications_progress': progress(
                JobApplication.objects.filter(
                    user=request.user,
                    date_applied__gte=week_start,
                    date_applied__lt=week_start + timedelta(days=7)
                ).count(),
                target.applications_target
            ),
            'num_linkedin_connections': LinkedInConnection.objects.filter(
                user=request.user,
                created_at__gte=week_start_dt,
                created_at__lt=week_end_dt
            ).count(),
            'max_linkedin_connections': target.linkedin_connections_target,
            'linkedin_connections_progress': progress(
                LinkedInConnection.objects.filter(
                    user=request.user,
                    created_at__gte=week_start_dt,
                    created_at__lt=week_end_dt
                ).count(),
                target.linkedin_connections_target
            ),
            'num_direct_approach': DirectApproach.objects.filter(
                user=request.user,
                date__gte=week_start,
                date__lt=week_start + timedelta(days=7)
            ).count(),
            'max_direct_approach': target.direct_approach_target,
            'direct_approach_progress': progress(
                DirectApproach.objects.filter(
                    user=request.user,
                    date__gte=week_start,
                    date__lt=week_start + timedelta(days=7)
                ).count(),
                target.direct_approach_target
            ),
            # Recruiters and Interviews are accumulative (all-time)
            'num_recruiters': RecruiterContact.objects.filter(user=request.user).count(),
            'max_recruiters': target.recruiters_target,
            'recruiters_progress': progress(
                RecruiterContact.objects.filter(user=request.user).count(),
                target.recruiters_target
            ),
            'num_interviews': Interview.objects.filter(user=request.user).count(),
            'max_interviews': target.interviews_target,
            'interviews_progress': progress(
                Interview.objects.filter(user=request.user).count(),
                target.interviews_target
            ),
            'num_linkedin_posts': LinkedInPost.objects.filter(
                user=request.user,
                date_posted__gte=week_start,
                date_posted__lt=week_start + timedelta(days=7)
            ).count(),
            'max_linkedin_posts': target.linkedin_posts_target,
            'linkedin_posts_progress': progress(
                LinkedInPost.objects.filter(
                    user=request.user,
                    date_posted__gte=week_start,
                    date_posted__lt=week_start + timedelta(days=7)
                ).count(),
                target.linkedin_posts_target
            ),
            'recent_applications': JobApplication.objects.filter(user=request.user).order_by('-date_applied')[:5],
            'week_start': week_start,
            'week_start_display': week_start.strftime('%B %d, %Y'),
            'prev_week': week_start - timedelta(days=7),
            'next_week': week_start + timedelta(days=7),
            'today': today,
        })
        # --- New: Weekly Overview Data (reverse order, add week numbers) ---
        this_monday = today - timedelta(days=today.weekday())
        list_of_weeks = [this_monday - timedelta(weeks=i) for i in range(3, -1, -1)]  # always Mondays

        week_dates = [week.strftime('%Y-%m-%d') for week in list_of_weeks]
        week_numbers = [f"Week {idx+1}" for idx in range(len(list_of_weeks))]

        networking_counts = [
            NetworkingContact.count_for_week(request.user, week)
            for week in list_of_weeks
        ]
        applications_counts = [
            JobApplication.count_for_week(request.user, week)
            for week in list_of_weeks
        ]
        direct_counts = [
            DirectApproach.count_for_week(request.user, week)
            for week in list_of_weeks
        ]
        linkedin_counts = [
            LinkedInPost.count_for_week(request.user, week)
            for week in list_of_weeks
        ]

        context['week_dates'] = week_dates
        context['week_numbers'] = week_numbers
        context['networking_counts'] = networking_counts
        context['applications_counts'] = applications_counts
        context['direct_counts'] = direct_counts
        context['linkedin_counts'] = linkedin_counts

        context.update(get_notification_context(request))
        return context

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminDashboardView(TemplateView):
    template_name = 'students/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        students = User.objects.filter(is_staff=False)
        progress_data = []
        for student in students:
            num_targets = WeeklyActivityTarget.objects.filter(user=student).count()
            progress_data.append({
                'student': student,
                'num_targets': num_targets,
            })
        context['progress_data'] = progress_data
        context.update(get_notification_context(self.request))
        return context

