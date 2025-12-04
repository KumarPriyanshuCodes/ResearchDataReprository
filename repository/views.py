from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Dataset
import os
import pandas as pd
import mimetypes
from django.http import FileResponse
from django.utils.encoding import smart_str

def home(request):
    """Display the main page with upload form and repository view"""
    datasets_list = Dataset.objects.all()
    
    # Pagination
    paginator = Paginator(datasets_list, 10)  # Show 10 datasets per page
    page_number = request.GET.get('page')
    datasets = paginator.get_page(page_number)
    
    return render(request, 'repository/home.html', {'datasets': datasets})

@login_required
def upload_dataset(request):
    """Handle dataset upload""" 
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        author = request.POST.get('author')
        description = request.POST.get('description')
        file = request.FILES.get('file')
        
        # Validate form data
        if not all([title, author, description, file]):
            messages.error(request, 'All fields are required.')
            return redirect('home')
        
        # Check file type
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension not in ['.csv', '.xlsx', '.pdf', '.doc', '.docx']:
            messages.error(request, 'Only CSV, XLSX, PDF, DOC, and DOCX files are allowed.')
            return redirect('home')
        
        # Check file size (500MB limit)
        if file.size > 500 * 1024 * 1024:
            messages.error(request, 'File size must be less than 500MB.')
            return redirect('home')
        
        try:
            # Create dataset object
            dataset = Dataset(
                title=title,
                author=author,
                description=description,
                file=file,
                file_size=file.size,
                file_type=file_extension.replace('.', '')
            )
            
            # Save to database
            dataset.save()
            
            messages.success(request, f'Dataset uploaded successfully! DOI: {dataset.doi}')
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f'Error uploading dataset: {str(e)}')
            return redirect('home')
    
    return redirect('home')

@login_required
def dataset_preview(request, dataset_id):
    """Display a preview of the dataset"""
    try:
        dataset = get_object_or_404(Dataset, id=dataset_id)
        file_path = dataset.file.path
        
        # For non-CSV/XLSX files, show file info instead of data preview
        if dataset.file_type not in ['csv', 'xlsx']:
            context = {
                'dataset': dataset,
                'preview_data': None,
            }
            return render(request, 'repository/preview.html', context)
        
        # Load data using pandas for CSV/XLSX files
        if dataset.file_type == 'csv':
            df = pd.read_csv(file_path)
        elif dataset.file_type == 'xlsx':
            df = pd.read_excel(file_path)
        else:
            messages.error(request, 'Unsupported file type for preview.')
            return redirect('home')
        
        # Get first 10 rows for preview
        preview_data = df.head(10)
        
        context = {
            'dataset': dataset,
            'preview_data': preview_data.to_html(classes='table table-hover table-bordered', index=False, table_id='preview-table'),
        }
        
        return render(request, 'repository/preview.html', context)
        
    except Dataset.DoesNotExist:
        messages.error(request, 'Dataset not found.')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Error loading dataset preview: {str(e)}')
        return redirect('home')

def search_datasets(request):
    """Search datasets by title or author"""
    query = request.GET.get('query', '')
    datasets_list = Dataset.objects.all()
    
    if query:
        datasets_list = datasets_list.filter(
            title__icontains=query
        ) | datasets_list.filter(
            author__icontains=query
        )
    
    # Pagination
    paginator = Paginator(datasets_list, 10)  
    page_number = request.GET.get('page')
    datasets = paginator.get_page(page_number)
    
    return render(request, 'repository/home.html', {
        'datasets': datasets,
        'search_query': query
    })

@login_required
def download_dataset(request, dataset_id):
    """Download a dataset file"""
    try:
        dataset = get_object_or_404(Dataset, id=dataset_id)
        file_path = dataset.file.path
        
        # Determine MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=mime_type,
            as_attachment=True,
            filename=os.path.basename(file_path)
        )
        response['Content-Disposition'] = f'attachment; filename="{smart_str(os.path.basename(file_path))}"'
        return response
        
    except Dataset.DoesNotExist:
        messages.error(request, 'Dataset not found.')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Error downloading dataset: {str(e)}')
        return redirect('home')