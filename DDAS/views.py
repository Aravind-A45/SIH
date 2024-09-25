from django.shortcuts import render
from pymongo import MongoClient
from django import forms
from django.shortcuts import render
from django.http import HttpResponse
from bson import ObjectId
from .models import *

# Create your views here.
def home(request):
  return render(request, "home.html")

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI if necessary
db = client['DDAS']  # MongoDB database name
fs = db['files']     # MongoDB collection name

# Django form for file upload
class FileUploadForm(forms.Form):
    file = forms.FileField()

# View to handle file upload
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            # Insert file into MongoDB
            file_id = fs.insert_one({'filename': file.name, 'data': file.read()}).inserted_id
            
            # Save file metadata in Django's SQLite database
            FileMeta.objects.create(file_id=str(file_id), filename=file.name)

            return HttpResponse("File uploaded successfully!")
    else:
        form = FileUploadForm()

    return render(request, 'upload.html', {'form': form})

def download_file(request, file_id):
    file_data = fs.find_one({'_id': ObjectId(file_id)})
    if file_data:
        response = HttpResponse(file_data['data'], content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={file_data["filename"]}'
        return response
    else:
        return HttpResponse("File not found.")  

def list_files(request):
    # Fetch all files from MongoDB (only _id and filename)
    files = fs.find({}, {'_id': 1, 'filename': 1})
    
    # Convert to list for easier manipulation in Django templates
    file_list = []
    for file in files:
        # Add file_id without the underscore
        file_list.append({
            'file_id': str(file['_id']),  # Convert ObjectId to string
            'filename': file['filename']
        })

    return render(request, 'file_list.html', {'files': file_list})        
