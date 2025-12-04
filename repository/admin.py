from django.contrib import admin
from .models import Dataset

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'doi', 'file_type', 'upload_date')
    list_filter = ('file_type', 'upload_date')
    search_fields = ('title', 'author', 'doi')
    readonly_fields = ('doi', 'upload_date', 'last_modified')
    ordering = ('-upload_date',)
    
    fieldsets = (
        ('Dataset Information', {
            'fields': ('title', 'author', 'description')
        }),
        ('File Information', {
            'fields': ('file', 'file_size', 'file_type')
        }),
        ('System Information', {
            'fields': ('doi', 'upload_date', 'last_modified'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Make DOI readonly only for existing objects
        if obj:
            return self.readonly_fields + ('file_size',)
        return self.readonly_fields