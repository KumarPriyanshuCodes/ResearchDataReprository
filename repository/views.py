from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Dataset
import os
import pandas as pd

def home(request):
    """Display the main page with upload form and repository view"""
    datasets = Dataset.objects.all()
    return render(request, 'repository/home.html', {'datasets': datasets})

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
        if file_extension not in ['.csv', '.xlsx']:
            messages.error(request, 'Only CSV and XLSX files are allowed.')
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

def dataset_preview(request, dataset_id):
    """Display a preview of the dataset"""
    try:
        dataset = Dataset.objects.get(id=dataset_id)
        file_path = dataset.file.path
        
        # Load data using pandas
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
    if query:
        datasets = Dataset.objects.filter(
            title__icontains=query
        ) | Dataset.objects.filter(
            author__icontains=query
        )
    else:
        datasets = Dataset.objects.all()
    
    return render(request, 'repository/home.html', {
        'datasets': datasets,
        'search_query': query
    })