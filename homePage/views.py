from django.shortcuts import render
from whistleblower.analytics import *

def home(request):
    reports_over_time = find_reports_submitted_over_time()
    form_statistices = find_form_statistics()
    print("test:", reports_over_time, form_statistices)
    return render(request, 
                  'homePage/home.html', 
                  {"reports_over_time": reports_over_time,
                   "form_statistics": form_statistices})


def about(request):
    return render(request, 'homePage/about.html')