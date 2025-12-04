from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Dataset
import os

class DatasetModelTest(TestCase):
    def setUp(self):
        # Create a sample dataset for testing
        self.dataset = Dataset.objects.create(
            title="Test Dataset",
            author="Test Author",
            description="Test Description",
            file=SimpleUploadedFile("test.csv", b"col1,col2\nval1,val2", content_type="text/csv"),
            file_size=20,
            file_type="csv"
        )
    
    def test_dataset_creation(self):
        """Test that a dataset can be created"""
        self.assertTrue(isinstance(self.dataset, Dataset))
        self.assertEqual(self.dataset.title, "Test Dataset")
        self.assertIsNotNone(self.dataset.doi)
        self.assertTrue(self.dataset.doi.startswith("10."))
    
    def test_dataset_string_representation(self):
        """Test the string representation of a dataset"""
        expected = f"{self.dataset.title} ({self.dataset.doi})"
        self.assertEqual(str(self.dataset), expected)
    
    def test_dataset_ordering(self):
        """Test that datasets are ordered by upload date (newest first)"""
        dataset2 = Dataset.objects.create(
            title="Second Dataset",
            author="Another Author",
            description="Another Description",
            file=SimpleUploadedFile("test2.csv", b"col1,col2\nval3,val4", content_type="text/csv"),
            file_size=20,
            file_type="csv"
        )
        
        datasets = Dataset.objects.all()
        self.assertEqual(datasets[0], dataset2)  # Most recent should be first
        self.assertEqual(datasets[1], self.dataset)

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.dataset = Dataset.objects.create(
            title="Test Dataset",
            author="Test Author",
            description="Test Description",
            file=SimpleUploadedFile("test.csv", b"col1,col2\nval1,val2", content_type="text/csv"),
            file_size=20,
            file_type="csv"
        )
    
    def test_home_page(self):
        """Test that the home page loads correctly"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Research Data Repository")
    
    def test_dataset_preview(self):
        """Test that the dataset preview page loads correctly"""
        # Login required for preview
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dataset_preview', args=[self.dataset.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.dataset.title)
    
    def test_search_datasets(self):
        """Test that the search functionality works"""
        response = self.client.get(reverse('search_datasets'), {'query': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.dataset.title)
    
    def test_upload_page_redirect(self):
        """Test that accessing upload without POST redirects to home"""
        # Login required for upload
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('upload_dataset'))
        self.assertRedirects(response, reverse('home'))
    
    def test_download_dataset(self):
        """Test that the download functionality works"""
        # Login required for download
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('download_dataset', args=[self.dataset.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('application', response['Content-Type'])

class DOIModelTest(TestCase):
    def test_doi_generation(self):
        """Test that DOIs are generated correctly"""
        dataset = Dataset.objects.create(
            title="DOI Test",
            author="DOI Author",
            description="DOI Description",
            file=SimpleUploadedFile("test.csv", b"col1,col2\nval1,val2", content_type="text/csv"),
            file_size=20,
            file_type="csv"
        )
        
        # Check DOI format
        self.assertTrue(dataset.doi.startswith("10."))
        self.assertIn("/", dataset.doi)
        self.assertEqual(len(dataset.doi.split("/")[-1]), 8)  # Random suffix length
        
        # Check uniqueness
        dataset2 = Dataset.objects.create(
            title="DOI Test 2",
            author="DOI Author 2",
            description="DOI Description 2",
            file=SimpleUploadedFile("test2.csv", b"col1,col2\nval3,val4", content_type="text/csv"),
            file_size=20,
            file_type="csv"
        )
        
        self.assertNotEqual(dataset.doi, dataset2.doi)