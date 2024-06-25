# Standard library imports
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage
from django.core.exceptions import PermissionDenied


# Local imports from the current app
from .models import Report, Appeal
from .forms import ReportForm, AppealForm

from django.contrib import messages

def clear_messages(request):
    storage = messages.get_messages(request)
    for message in storage:
        # This loop will clear all messages.
        pass
    storage.used = True  # Mark the storage as used to prevent message from being re-added on next request.


# Helper function to check if a user is superuser or staff
def is_superuser_or_admin(user):
    """
    Checks if the user has superuser or staff privileges.
    """
    return user.groups.filter(name='siteAdmin').exists()

def is_NOT_superuser_or_admin(user):
    """
    Checks if the user has superuser or staff privileges.
    """
    return not user.groups.filter(name='siteAdmin').exists()

def is_authenticated_and_not_superuser_or_admin(user):
    return (not user.groups.filter(name='siteAdmin').exists()) & user.is_authenticated
#needs to be common user
@user_passes_test(is_authenticated_and_not_superuser_or_admin, login_url=reverse_lazy('accounts:signin'))
def user_pending_submissions(request):
    """
    Displays the pending submissions for the logged-in user.
    """
    user_reports = Report.objects.filter(
        reported_by=request.user,
        status__in=['new', 'in_progress'],
        publication_status__in=['In Progress']
    ).order_by('-created_at')
    return render(request, 'whistleblower/pending_submissions.html', {'reports': user_reports})

# needs to be admin
@user_passes_test(is_superuser_or_admin, login_url=reverse_lazy('accounts:signin'))
def review_submissions(request):
    """
    Displays all submissions for review by admin.
    """
    reports = Report.objects.all().order_by('-created_at')
    clear_messages(request)
    return render(request, 'whistleblower/admin_dashboard.html', {'reports': reports})

@login_required(login_url=reverse_lazy('accounts:signin'))
def upvote_report(request, report_id):
    clear_messages(request)
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        # Check if the user has already upvoted
        if request.user in report.upvotes.all():
            return JsonResponse({'error': 'You have already upvoted this report.',
                                 'upvotes': report.upvotes.count()}, status=400)
        # Check if the user has downvoted before and remove the downvote if so
        if request.user in report.downvotes.all():
            report.downvotes.remove(request.user)
        report.upvotes.add(request.user)
        return JsonResponse({'upvotes': report.upvotes.count()})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required(login_url=reverse_lazy('accounts:signin'))
def downvote_report(request, report_id):
    clear_messages(request)
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        if request.user in report.downvotes.all():
            return JsonResponse({'error': 'You have already downvoted this report.',
                                 "upvotes": report.upvotes.count()}, status=400)
        if request.user in report.upvotes.all():
            report.upvotes.remove(request.user)
        report.downvotes.add(request.user)
        # Return both upvote and downvote counts
        return JsonResponse({'upvotes': report.upvotes.count(), 'downvotes': report.downvotes.count()})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

#needs to be common user

def report(request):
    """
    Handles the creation of a new report.
    """
    clear_messages(request)

    # Check if the user is a staff member
    if is_superuser_or_admin(request.user):
        messages.error(request, "Access denied: Staff members cannot submit reports.")
        return redirect('home')  # Redirect to the homepage or appropriate URL

    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            new_report = form.save(commit=False)
            if form.cleaned_data.get('appear_anonymous', False) or not request.user.is_authenticated:
                new_report.reported_by = None
            else:
                new_report.reported_by = request.user
            new_report.save()
            return redirect('whistleblower:report_submitted')
    else:
        form = ReportForm(user=request.user)
    return render(request, 'whistleblower/report_form.html', {'form': form})

#needs to be admin
@user_passes_test(is_superuser_or_admin, login_url=reverse_lazy('accounts:signin'))
def admin_dashboard(request):
    clear_messages(request)
    # Initialize `reports` at the beginning to ensure it's always defined
    reports = Report.objects.filter(status__in=['in_progress', 'new', 'appealed'])

    # Retrieve the sort and search_query parameters from the request
    sort = request.GET.get('sort', 'date_desc')  # Default sorting
    search_query = request.GET.get('search_query', '')
    searchBarCustom = request.GET.get('searchBarCustom')

    # Apply search filtering if a search_query is provided
    if search_query:
        if searchBarCustom == 'Username':
            # only search username
            reports = reports.filter(reported_by__username__icontains=search_query)
        elif searchBarCustom == 'Description':
            # only search description
            reports = reports.filter(description__icontains=search_query)
        else:
            # Default behavior if no specific search option is selected or for 'all'
            reports = reports.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(reported_by__username__icontains=search_query)
            )

    if sort == 'date_desc':
        reports = reports.order_by('-created_at')
    elif sort == 'date_asc':
        reports = reports.order_by('created_at')
    elif sort == 'status':
        reports = reports.order_by('status')
    elif sort == 'new':
        reports = reports.filter(status='new').order_by('created_at')
    elif sort == 'in_progress':
        reports = reports.filter(status='in_progress').order_by('created_at')
    elif sort == 'appealed':
        reports = reports.filter(status='appealed').order_by('created_at')

    return render(request, 'whistleblower/admin_dashboard.html', {'reports': reports})


#needs to be common user
@user_passes_test(is_NOT_superuser_or_admin, login_url=reverse_lazy('accounts:signin'))
def report_submitted(request):
    """
    Displays a confirmation message after a report is submitted.
    """
    clear_messages(request)
    return render(request, 'whistleblower/report_submitted.html')

def reports_list(request):
    """
    Lists reports that are resolved and published.
    """
    clear_messages(request)
    reports = Report.objects.filter(
        Q(status="resolved") & Q(publication_status="Published")
    ).order_by('-created_at')
    sort = request.GET.get('sort', 'date_desc')  # Default sorting
    search_query = request.GET.get('search_query', '')
    searchBarCustom = request.GET.get('searchBarCustom')

    # Apply search filtering if a search_query is provided
    if search_query:
        if searchBarCustom == 'Username':
            # only search username
            reports = reports.filter(reported_by__username__icontains=search_query)
        elif searchBarCustom == 'Description':
            # only search description
            reports = reports.filter(description__icontains=search_query)
        else:
            # Default behavior if no specific search option is selected or for 'all'
            reports = reports.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(reported_by__username__icontains=search_query)
            )
    # Apply sorting based on the `sort` parameter
    if sort == 'date_desc':
        reports = reports.order_by('-created_at')
    elif sort == 'date_asc':
        reports = reports.order_by('created_at')
    elif sort == 'status':
        reports = reports.order_by('status')
    elif sort == 'upvote_asc':
        reports = reports.annotate(upvote_count=Count('upvotes')).order_by('upvote_count')
    elif sort == 'upvote_desc':
        reports = reports.annotate(upvote_count=Count('upvotes')).order_by('-upvote_count')
    return render(request, 'whistleblower/reports_list.html', {'reports': reports})

#needs to be common user
@user_passes_test(is_superuser_or_admin, login_url=reverse_lazy('accounts:signin'))
def edit_submission(request, pk):
    clear_messages(request)
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        form = ReportForm(request.POST, instance=report, user=request.user)
        if form.is_valid():
            # Check if the report's status is resolved and enforce publication status rule
            if form.cleaned_data['status'] == 'resolved':
                publication_status = form.cleaned_data.get('publication_status')
                if publication_status not in ['Published', 'Denied']:
                    clear_messages(request)
                    messages.error(request, 'Resolved reports must be either Published or Denied.')
                    return render(request, 'whistleblower/edit_submission.html', {'form': form, 'report': report})
            # Check if the report's status is in progress and enforce publication status rule
            elif form.cleaned_data['status'] == 'in_progress':
                publication_status = form.cleaned_data.get('publication_status')
                if publication_status != 'In Progress':
                    clear_messages(request)
                    messages.error(request, 'Reports with status In Progress must have the publication status as In Progress.')
                    return render(request, 'whistleblower/edit_submission.html', {'form': form, 'report': report})
            form.save()
            return redirect('whistleblower:admin_dashboard')
    else:
        form = ReportForm(instance=report, user=request.user)
    return render(request, 'whistleblower/edit_submission.html', {'form': form, 'report': report})

@login_required(login_url=reverse_lazy('accounts:signin'))
def submission_details(request, pk):
    """
    Displays details for a specific submission.
    """
    clear_messages(request)
    report = get_object_or_404(Report, pk=pk)
    if is_superuser_or_admin(request.user) and report.status != "resolved":
        report.status = 'in_progress'
        report.save()
    return render(request, 'whistleblower/submission_details.html', {'report': report})

def report_info(request, report_id):
    """
    Displays details for a specific report.
    """
    clear_messages(request)
    report = get_object_or_404(Report, pk=report_id)
    return render(request, 'whistleblower/report_info.html', {'report': report})

@login_required
def delete_report_files(request, pk):
    report = get_object_or_404(Report, pk=pk)

    try:
        # Authorization check
        if not request.user.is_staff and request.user != report.reported_by:
            messages.error(request, 'Unauthorized access.')
            raise PermissionDenied

        # Handle Appeal deletion along with its file
        if hasattr(report, 'appeal'):
            appeal = report.appeal
            if appeal.evidence and default_storage.exists(appeal.evidence.name):
                default_storage.delete(appeal.evidence.name)
            appeal.delete()
            print("deleted appeal")

        # Delete the file associated with the report
        if report.file and default_storage.exists(report.file.name):
            default_storage.delete(report.file.name)

        # Delete the report itself
        report.delete()
    except:
        messages.error(request, 'An error occurred while deleting the report.')
        return redirect('whistleblower:submission_details', pk=pk)

    messages.success(request, 'Report and all associated files have been deleted.')
    return redirect('whistleblower:reports_list')

# needs to be common user
@user_passes_test(is_NOT_superuser_or_admin, login_url=reverse_lazy('accounts:signin'))
def appeal(request, report_id):
    """
    Handles the submission of an appeal for a report.
    """
    clear_messages(request)
    report = Report.objects.get(pk=report_id)
    if request.method == "POST":
        form = AppealForm(request.POST, request.FILES, user = request.user)
        if form.is_valid():
            appeal = form.save(commit=False)
            #print(form.cleaned_data)
            appeal.user = request.user
            appeal.report = report
            appeal.save()
            report.status = "Appealed"
            report.save()
            return redirect('/')
    else:
        form = AppealForm()
    return render(request, "whistleblower/appeal_form.html", {"form": form, "report": report})

#needs to be admin
@user_passes_test(is_superuser_or_admin, login_url=reverse_lazy('accounts:signin'))
def review_appeals(request):
    """
    Lists appeals for admin review.
    """
    clear_messages(request)
    appeals = Appeal.objects.filter(report__status="Appealed")
    return render(request, 'whistleblower/review_appeals.html', {'appeals': appeals})

#anyone

def policy_page(request):
    """
    Displays federal policy and laws regarding whistleblowing.
    """
    clear_messages(request)
    return render(request, 'whistleblower/policy.html')

def privacy_page(request):
    """
    Displays privacy policy for our whistleblowing app.
    """
    clear_messages(request)
    return render(request, 'whistleblower/privacy.html')


def terms_page(request):
    """
    Displays privacy policy for our whistleblowing app.
    """
    clear_messages(request)
    return render(request, 'whistleblower/terms.html')

# needs to be common user
@user_passes_test(is_NOT_superuser_or_admin, login_url=reverse_lazy('accounts:signin'))
def denied_submissions(request):
    """
    Displays submissions that have been denied.
    """
    clear_messages(request)
    denied_reports = Report.objects.filter(
        reported_by=request.user,
        publication_status__in=['Denied'],
        status__in=['resolved'],
    ).order_by('-created_at')
    return render(request, 'whistleblower/denied_submissions.html', {'reports': denied_reports})

@user_passes_test(is_NOT_superuser_or_admin, login_url=reverse_lazy('accounts:signin'))
def all_submissions(request):
    """
    Displays all submissions submitted by the logged-in user who are not superusers or admins.
    """
    user_reports = Report.objects.filter(reported_by=request.user).order_by('-created_at')
    return render(request, 'whistleblower/all_submissions.html', {'reports': user_reports})

@login_required(login_url=reverse_lazy('accounts:signin'))
def appeal_details(request, pk):
    """
    View function to display details of a specific appeal along with associated reports.
    Only the user who created the appeal or an admin can view this page.
    """
    appeal = get_object_or_404(Appeal, pk=pk)
    # Check if the current user is the owner of the appeal or an admin
    if request.user != appeal.user and not is_superuser_or_admin(request.user):
        messages.error(request, "You are not authorized to view this appeal.")
        return redirect('home')  # Replace 'homepage' with your actual home URL name

    related_reports = Report.objects.filter(appeal=appeal)
    return render(request, 'whistleblower/appeal_details.html', {
        'appeal': appeal,
        'related_reports': related_reports
    })
