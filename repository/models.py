from django.db import models
import uuid
from datetime import datetime
import os

class Dataset(models.Model):
    # Generate a unique ID for the dataset
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Dataset metadata
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField()
    
    # File information
    file = models.FileField(upload_to='datasets/')
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=10)  # csv, xlsx, pdf, doc, docx
    
    # Mock DOI - automatically generated
    doi = models.CharField(max_length=100, unique=True, editable=False)
    
    # Timestamps
    upload_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Generate mock DOI if not already set
        if not self.doi:
            # Format: 10.{year}{month}{day}/{random_string}
            date_str = datetime.now().strftime("%Y%m%d")
            random_suffix = uuid.uuid4().hex[:8].upper()
            self.doi = f"10.{date_str}/{random_suffix}"
        
        # Set file type if not already set
        if not self.file_type and self.file:
            _, ext = os.path.splitext(self.file.name)
            self.file_type = ext.lower().replace('.', '')
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} ({self.doi})"
    
    class Meta:
        ordering = ['-upload_date']
        verbose_name = "Dataset"
        verbose_name_plural = "Datasets"