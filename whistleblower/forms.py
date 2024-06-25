from django import forms
from django.contrib.auth import get_user_model
from .models import Report, Appeal
from homePage.templatetags.group_filters import has_group



User = get_user_model()

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'description', 'company', 'file', 'appear_anonymous', 'admin_notes', 'status', 'publication_status']  # Exclude admin fields here
        widgets = {
            'title': forms.TextInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'company': forms.TextInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'file': forms.FileInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm'}),
            'appear_anonymous': forms.CheckboxInput(attrs={'class': 'rounded'}),
            'admin_notes': forms.TextInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'status': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'publication_status': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReportForm, self).__init__(*args, **kwargs)

        # Conditionally include admin fields if the user is staff
        # if user and user.is_staff:
        #     self.fields['status'] = forms.ChoiceField(choices=Report.STATUS_CHOICES)
        #     self.fields['publication_status'] = forms.ChoiceField(choices=Report.PUBLICATION_STATUS_CHOICES)

        if user and not has_group(user, "siteAdmin"):
            del self.fields['admin_notes']
            del self.fields['status']
            del self.fields['publication_status']

class AppealForm(forms.ModelForm):
    class Meta:
        model = Appeal
        fields = ["reasons", "evidence"]
        widgets = {
            'reasons': forms.Textarea(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'evidence': forms.FileInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AppealForm, self).__init__(*args, **kwargs)