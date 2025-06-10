from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.welcome, name='welcome'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Job Applications
    path('applications/', views.JobApplicationListView.as_view(), name='applications'),
    path('applications/add/', views.JobApplicationCreateView.as_view(), name='add_application'),
    path('applications/<int:pk>/edit/', views.JobApplicationUpdateView.as_view(), name='edit_application'),
    path('applications/<int:pk>/delete/', views.JobApplicationDeleteView.as_view(), name='delete_application'),
    path('applications/bulk-delete/', views.bulk_delete_applications, name='bulk_delete_applications'),

    # Networking Contacts
    path('networking/', views.NetworkingContactListView.as_view(), name='networking'),
    path('networking/add/', views.NetworkingContactCreateView.as_view(), name='add_contact'),
    path('networking/<int:pk>/edit/', views.NetworkingContactUpdateView.as_view(), name='edit_contact'),
    path('networking/<int:pk>/delete/', views.NetworkingContactDeleteView.as_view(), name='delete_contact'),
    path('networking/bulk-delete/', views.bulk_delete_contacts, name='bulk_delete_contacts'),

    # Direct Approach
    path('direct-approach/', views.DirectApproachListView.as_view(), name='direct_approach'),
    path('direct-approach/add/', views.DirectApproachCreateView.as_view(), name='add_direct_approach'),
    path('direct-approach/<int:pk>/edit/', views.DirectApproachUpdateView.as_view(), name='edit_direct_approach'),
    path('direct-approach/<int:pk>/delete/', views.DirectApproachDeleteView.as_view(), name='delete_direct_approach'),
    path('direct-approach/bulk-delete/', views.bulk_delete_direct_approach, name='bulk_delete_direct_approach'),

    # Recruiters
    path('recruiters/', views.RecruiterContactListView.as_view(), name='recruiters'),
    path('recruiters/add/', views.RecruiterContactCreateView.as_view(), name='add_recruiter'),
    path('recruiters/<int:pk>/edit/', views.RecruiterContactUpdateView.as_view(), name='edit_recruiter'),
    path('recruiters/<int:pk>/delete/', views.RecruiterContactDeleteView.as_view(), name='delete_recruiter'),
    path('recruiters/bulk-delete/', views.bulk_delete_recruiters, name='bulk_delete_recruiters'),

    # Interviews
    path('interviews/', views.InterviewListView.as_view(), name='interviews'),
    path('interviews/add/', views.InterviewCreateView.as_view(), name='add_interview'),
    path('interviews/<int:pk>/edit/', views.InterviewUpdateView.as_view(), name='edit_interview'),
    path('interviews/<int:pk>/delete/', views.InterviewDeleteView.as_view(), name='delete_interview'),
    path('interviews/bulk-delete/', views.bulk_delete_interviews, name='bulk_delete_interviews'),

    # LinkedIn Posts
    path('linkedin-posts/', views.LinkedInPostListView.as_view(), name='linkedin_posts'),
    path('linkedin-posts/add/', views.LinkedInPostCreateView.as_view(), name='add_linkedin_post'),
    path('linkedin-posts/<int:pk>/edit/', views.LinkedInPostUpdateView.as_view(), name='edit_linkedin_post'),
    path('linkedin-posts/<int:pk>/delete/', views.LinkedInPostDeleteView.as_view(), name='delete_linkedin_post'),
    path('linkedin-posts/bulk-delete/', views.bulk_delete_linkedin_posts, name='bulk_delete_linkedin_posts'),

    # User/Profile/Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('delete-profile/', views.delete_profile, name='delete_profile'),

    # Admin
    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('weekly-targets/edit/', views.edit_weekly_targets, name='edit_weekly_targets'),
]