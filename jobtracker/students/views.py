from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from .forms import StudentProfileForm, JobApplicationForm, WeeklyActivityTargetForm, NetworkingContactForm, EmailAuthenticationForm, DirectApproachForm, RecruiterContactForm, InterviewForm, LinkedInPostForm, CustomUserCreationForm
from .models import StudentProfile, JobApplication, NetworkingContact, WeeklyActivityTarget, DirectApproach, RecruiterContact, Interview, LinkedInPost, LinkedInConnection
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Sum, F, Value, IntegerField
from django.contrib import messages
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import (
    WeeklyActivityTarget, NetworkingContact, JobApplication,
    DirectApproach, RecruiterContact, Interview, LinkedInPost
)

User = get_user_model()

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
    return render(request, 'students/profile.html', {'form': form})

@login_required
def applications(request):
    query = request.GET.get('q', '')
    applications = JobApplication.objects.filter(user=request.user)
    if query:
        applications = applications.filter(
            Q(company_name__icontains=query) |
            Q(job_title__icontains=query) |
            Q(notes__icontains=query)
        )
    applications = applications.order_by('-date_applied')
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            job_app = form.save(commit=False)
            job_app.user = request.user
            job_app.save()
            messages.success(request, "Job application added successfully!")
            return redirect('applications')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobApplicationForm()
    return render(request, 'students/applications.html', {
        'applications': applications,
        'form': form,
        'query': query,
    })

@login_required
def edit_application(request, pk):
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Application updated successfully!")
            return redirect('applications')
    else:
        form = JobApplicationForm(instance=application)
    return render(request, 'students/edit_application.html', {'form': form})

@login_required
def delete_application(request, pk):
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == 'POST':
        application.delete()
        messages.success(request, "Application deleted successfully!")
        return redirect('applications')
    return render(request, 'students/delete_application.html', {'application': application})

@login_required
def targets(request):
    query = request.GET.get('q', '')
    targets = WeeklyActivityTarget.objects.filter(user=request.user).order_by('activity')
    for t in targets:
        t.total_actual = (t.monday or 0) + (t.tuesday or 0) + (t.wednesday or 0) + (t.thursday or 0) + (t.friday or 0)
    if request.method == 'POST':
        form = WeeklyActivityTargetForm(request.POST)
        if form.is_valid():
            target = form.save(commit=False)
            target.user = request.user
            target.save()
            return redirect('targets')
    else:
        form = WeeklyActivityTargetForm()

    return render(request, 'students/targets.html', {
        'targets': targets,
        'form': form,
        'query': query,
    })

@login_required
def edit_target(request, pk):
    target = get_object_or_404(WeeklyActivityTarget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = WeeklyActivityTargetForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(request, "Target updated successfully!")
            return redirect('targets')
    else:
        form = WeeklyActivityTargetForm(instance=target)
    return render(request, 'students/edit_target.html', {'form': form, 'target': target})

@login_required
def delete_target(request, pk):
    target = get_object_or_404(WeeklyActivityTarget, pk=pk, user=request.user)
    if request.method == 'POST':
        target.delete()
        messages.success(request, "Target deleted successfully!")
        return redirect('targets')
    return render(request, 'students/delete_target.html', {'target': target})

@login_required
def networking(request):
    query = request.GET.get('q', '')
    contacts = NetworkingContact.objects.filter(user=request.user)
    if query:
        contacts = contacts.filter(
            Q(contact_name__icontains=query) |
            Q(company__icontains=query) |
            Q(contact_role__icontains=query)
        )
    contacts = contacts.order_by('-request_sent')

    if request.method == 'POST':
        form = NetworkingContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            return redirect('networking')
    else:
        form = NetworkingContactForm()

    return render(request, 'students/networking.html', {
        'contacts': contacts,
        'form': form,
        'query': query,
    })

def get_week_start(d):
    """Return the Monday of the week for a given date."""
    return d - timedelta(days=d.weekday())

@login_required
def dashboard(request):
    today = timezone.localdate()
    # Support ?week=YYYY-MM-DD for pagination
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
        'sent_target': 40,  # Set to 40
        'accepted_target': 20,  # Set to 20
        'conversation_target': 5,  # Set to 5
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
        'num_recruiters': RecruiterContact.objects.filter(
            user=request.user,
            date__gte=week_start,
            date__lt=week_start + timedelta(days=7)
        ).count(),
        'max_recruiters': target.recruiters_target,
        'recruiters_progress': progress(
            RecruiterContact.objects.filter(
                user=request.user,
                date__gte=week_start,
                date__lt=week_start + timedelta(days=7)
            ).count(),
            target.recruiters_target
        ),
        'num_interviews': Interview.objects.filter(
            user=request.user,
            date__gte=week_start,
            date__lt=week_start + timedelta(days=7)
        ).count(),
        'max_interviews': target.interviews_target,
        'interviews_progress': progress(
            Interview.objects.filter(
                user=request.user,
                date__gte=week_start,
                date__lt=week_start + timedelta(days=7)
            ).count(),
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
    return render(request, 'students/dashboard.html', context)

@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your profile has been deleted.")
        return redirect('welcome')  # or your homepage
    return render(request, 'students/delete_profile.html')

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

    return render(request, 'students/direct_approach.html', {'approaches': approaches, 'form': form})

def tutorial(request):
    return render(request, 'students/tutorial.html')

@login_required
def welcome(request):
    return render(request, 'students/welcome.html')

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
    return render(request, 'students/edit_direct_approach.html', {'form': form, 'approach': approach})

@login_required
def delete_direct_approach(request, pk):
    approach = get_object_or_404(DirectApproach, pk=pk, user=request.user)
    if request.method == 'POST':
        approach.delete()
        messages.success(request, "Direct approach deleted successfully!")
        return redirect('direct_approach')
    return render(request, 'students/delete_direct_approach.html', {'approach': approach})

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

    return render(request, 'students/recruiters.html', {
        'recruiters': recruiters,
        'form': form,
        'query': query,
    })

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
            return redirect('interviews')
    else:
        form = InterviewForm()

    return render(request, 'students/interviews.html', {'interviews': interviews, 'form': form})

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
    return render(request, 'students/edit_interview.html', {'form': form, 'interview': interview})

@login_required
def delete_interview(request, pk):
    interview = get_object_or_404(Interview, pk=pk, user=request.user)
    if request.method == 'POST':
        interview.delete()
        messages.success(request, "Interview deleted successfully!")
        return redirect('interviews')
    return render(request, 'students/delete_interview.html', {'interview': interview})

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
    return render(request, 'students/edit_recruiter.html', {'form': form, 'recruiter': recruiter})

@login_required
def delete_recruiter(request, pk):
    recruiter = get_object_or_404(RecruiterContact, pk=pk, user=request.user)
    if request.method == 'POST':
        recruiter.delete()
        messages.success(request, "Recruiter contact deleted successfully!")
        return redirect('recruiters')
    return render(request, 'students/delete_recruiter.html', {'recruiter': recruiter})

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

    return render(request, 'students/linkedin_posts.html', {
        'posts': posts,
        'form': form,
        'query': query,
    })

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
    return render(request, 'students/edit_linkedin_post.html', {'form': form, 'post': post})

@login_required
def delete_linkedin_post(request, pk):
    post = get_object_or_404(LinkedInPost, pk=pk, user=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, "LinkedIn post deleted successfully!")
        return redirect('linkedin_posts')
    return render(request, 'students/delete_linkedin_post.html', {'post': post})

@login_required
def networking_questions(request):
    return render(request, 'students/networking_questions.html')

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # Gather all students' progress data
    students = User.objects.filter(is_staff=False)
    progress_data = []
    for student in students:
        # Calculate progress for each student (example)
        num_targets = WeeklyActivityTarget.objects.filter(user=student).count()
        # ...repeat for other metrics...
        progress_data.append({
            'student': student,
            'num_targets': num_targets,
            # ...other metrics...
        })
    return render(request, 'students/admin_dashboard.html', {'progress_data': progress_data})

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import JobApplication

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
    return render(request, 'students/edit_contact.html', {'form': form, 'contact': contact})

@login_required
def delete_contact(request, pk):
    contact = get_object_or_404(NetworkingContact, pk=pk, user=request.user)
    if request.method == 'POST':
        contact.delete()
        messages.success(request, "Contact deleted successfully!")
        return redirect('networking')
    return render(request, 'students/delete_contact.html', {'contact': contact})

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
    return render(request, 'students/edit_weekly_targets.html', {'form': form, 'week_start': week_start})

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
    return render(request, 'students/add_contact.html', {'form': form})

