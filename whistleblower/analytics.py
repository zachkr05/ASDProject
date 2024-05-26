from .models import Report

from django.db.models import Count
from django.db.models.functions import TruncDay
from .models import Report

def find_reports_submitted_over_time():
    """
    Find the number of reports submitted, grouped by day.

    Returns: list of dicts containing submission date and count
        [
            {"submission_day": "2023-01-01", "submitted_count": 14},
            {"submission_day": "2023-01-02", "submitted_count": 20},
            // More days follow...
        ]
    """
    # Group reports by day of submission and count them
    reports_by_day = Report.objects \
        .annotate(submission_day=TruncDay('created_at')) \
        .values('submission_day') \
        .annotate(submitted_count=Count('id')) \
        .order_by('submission_day')

    for report in reports_by_day:
        if report['submission_day'] != None:
            report['submission_day'] = report['submission_day'].isoformat()
    
    return list(reports_by_day)


def find_form_statistics():
    """
    For all of the reports, find the status counts. 
    """
    # Group forms by status and count them
    status_counts = Report.objects.values('status').annotate(count=Count('id')).order_by('status')
    
    # Convert QuerySet to a dictionary for easier access
    status_dict = {item['status']: item['count'] for item in status_counts}
    
    # Ensure all possible statuses are included in the result
    all_statuses = ['new', 'in_progress', 'resolved']
    for status in all_statuses:
        status_dict.setdefault(status, 0)
    
    status_dict["New"] = status_dict.pop('new')
    status_dict["In Progress"] = status_dict.pop('in_progress')
    status_dict["Resolved"] = status_dict.pop('resolved')

    return status_dict