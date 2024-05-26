# whistleblower/models.py
from django.db import models
from django.contrib.auth.models import User
from storages.backends.s3boto3 import S3Boto3Storage

from django.core.validators import FileExtensionValidator

from uuid import uuid4
from django.utils.timezone import now

def create_new_file_name(instance, filename):
    """
    Generate a unique file name using a combination of the current timestamp, 
    a random UUID, and the original file extension.
    """
    # Extract the extension from the original file name
    ext = filename.split('.')[-1]
    # Generate a unique file name using the timestamp and UUID
    filename = f'{now().strftime("%Y%m%d%H%M%S")}_{uuid4().hex}_{filename}'
    # Return the path with the new file name
    return f'report_files/{filename}'

class Report(models.Model):
    """
    A model for creating a report.

    Attributes:
        title (str): 
            The title of the report.
        description (str): 
            The description of the report.
        company (str):
            The company related to specific user/report.
        created_at (datetime): 
            The date and time when the report was created.
        reported_by (User): 
            The user who reported the issue (can be null).
        file (FileField): 
            The file associated with the report.
        appear_anonymous (bool): 
            Flag indicating if the report should appear anonymous.

    Methods:
        __str__(): Returns the title of the report.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.CharField(max_length=255, default='N/A')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    upvotes = models.ManyToManyField(User, related_name='upvoted_reports', default=0)
    downvotes = models.ManyToManyField(User, related_name='downvoted_reports', default=0)

    reported_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reports', 
        null=True, 
        blank=True)

    STATUS_CHOICES = (
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('appealed', 'Appealed')
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True, null=True)
    
    file = models.FileField(
        storage=S3Boto3Storage(),
        upload_to=create_new_file_name,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'jpg', 'jpeg'])],
        null=True,  # Allows the field to be null if no file is uploaded
        blank=True,  # Allows the form to be submitted without a file
    )

    publication_status = models.CharField(
        max_length=20,
        choices=(
            ('In Progress', 'In Progress'),
            ('Published', 'Published'),
            ('Denied', 'Denied'),
        ),
        default='In Progress'
    )
    PUBLICATION_STATUS_CHOICES = (
        ('In_Progress', 'In Progress'),
        ('Published', 'Published'),
        ('Denied', 'Denied'),
    )

    appear_anonymous = models.BooleanField(
        default=False) 
    
    def __str__(self):
        return self.title
    

class Appeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True)
    reasons = models.TextField()
    evidence = models.FileField(
        storage=S3Boto3Storage(),
        upload_to=create_new_file_name,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'txt', 'jpg', 'jpeg'])],
        null=True,  # Allows the field to be null if no file is uploaded
        blank=True,  # Allows the form to be submitted without a file
    )

# class Appeal(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     report = models.ForeignKey(Report, on_delete=models.CASCADE)
#     # status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")])
#     reasons = models.TextField()
#     evidence = models.FileField(
#         upload_to=create_new_file_name,
#         null=True,  # Allows the field to be null if no file is uploaded
#         blank=True  # Allows the form to be submitted without a file
#     )