from django.urls import path
from . import views

app_name = "whistleblower"

urlpatterns = [
    # URLs for report interactions
    path('report/', views.report, name='report'),
    path('report/<int:report_id>/upvote/', views.upvote_report, name='upvote_report'),
    path('report/<int:report_id>/downvote/', views.downvote_report, name='downvote_report'),
    path('report_submitted/', views.report_submitted, name='report_submitted'),

    # URLs for viewing reports
    path('reports_list/', views.reports_list, name='reports_list'),
    path('pending_submissions/', views.user_pending_submissions, name='pending_submissions'),

    # Admin-specific URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('edit-submission/<int:pk>/', views.edit_submission, name='edit_submission'),

    # Detail views for reports for admin and main user
    path('submission-details/<int:pk>/', views.submission_details, name='submission_details'),
    # Detail views for generic users
    path('report_info/<int:report_id>/', views.report_info, name='report_info'),

    # Appeal handling
    path('appeal/<int:report_id>/', views.appeal, name='appeal'),
    path('review_appeals/', views.review_appeals, name='review_appeals'),
    path('all_submissions/', views.all_submissions, name='all_submissions'),

    path('appeal_details/<int:pk>/', views.appeal_details, name='appeal_details'),


    # Additional information and denied submissions
    path('policy/', views.policy_page, name='policy'),
    path('privacy/', views.privacy_page, name='privacy'),
    path('terms/', views.terms_page, name='terms'),
    path('denied_submissions/', views.denied_submissions, name='denied_submissions'),

    # Delete submission
    path('delete-report/<int:pk>/', views.delete_report_files, name='delete_report_files'),


]
