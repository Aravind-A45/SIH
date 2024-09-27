from django.shortcuts import render
from pymongo import MongoClient
from django import forms
from django.shortcuts import render
from django.http import HttpResponse
from bson import ObjectId
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group, auth
from  django.contrib import messages

# Create your views here.
def home(request):
  is_admin = request.user.groups.filter(name='admin').exists()
  return render(request, "home.html", {"is_admin":is_admin})

def login(request):
    if request.user.is_authenticated :
      return redirect('upload_file')

    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        try:
            user=auth.authenticate(username=username,password=password, email=email) 
            if user != None:
                auth.login(request,user)
                return redirect('home')
            else:
                messages.info(request, "Invalid credentials")
                return redirect('signup')
        except:
            return redirect('login')
 
    return render(request,'credentials/login.html')

def signup(request):
    details = User.objects.all()

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        con_password = request.POST.get('con_password')
        email = request.POST.get('email')
        
        if password == con_password:
            if User.objects.filter(username=username).exists():
                messages.info(request, f"Username already exists")
                return redirect('signup')

            if User.objects.filter(email=email).exists():
                messages.info(request, f"Email already exists")
                return redirect('signup')

            user = User.objects.create_user(username=username, password=password, email=email)
            user = authenticate(username=username, password=password, email=email)
            member_group = Group.objects.get(name='member')
            user.groups.add(member_group)

            info_id = request.session.get('info_id')
            if info_id:
                info = Info.objects.get(id=info_id)
                info.user = user
                info.save()
                del request.session['info_id']
            messages.success(request, "Account created successfully.")

            if user is not None:
                return redirect('login')
            else:
                messages.error(request, "Invalid username or password.")
        else:
          messages.error(request, "Password and Confirm Password are not matching")
    return render(request, 'credentials/signup.html')

def logout(request):
  auth.logout(request)
  return redirect('login')   

# Connect to MongoDB
client = MongoClient('mongodb+srv://admin:admin@ddas.bsvnf.mongodb.net/?retryWrites=true&w=majority&appName=DDAS')  # Replace with your MongoDB URI if necessary
db = client['DDAS']  # MongoDB database name
fs = db['files']     # MongoDB collection name

# Django form for file upload
class FileUploadForm(forms.Form):
    file = forms.FileField()

# View to handle file upload
def upload_file(request):
    is_admin = request.user.groups.filter(name='admin').exists()  # Check if user is admin
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']  # Access the uploaded file

            # Insert file into MongoDB
            file_id = fs.insert_one({'filename': file.name, 'data': file.read()}).inserted_id

            # Save file metadata in Django's SQLite database (FileMeta is a Django model)
            FileMeta.objects.create(file_id=str(file_id), filename=file.name)

            return render(request, 'upload.html', {'form': form, 'is_admin': is_admin, 'upload_success': True})
    else:
        form = FileUploadForm()

    return render(request, 'upload.html', {'form': form, 'is_admin': is_admin})


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