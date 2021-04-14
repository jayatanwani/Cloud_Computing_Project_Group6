from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import UserBuckets,UserFiles
from django.conf import settings
from django.core.files.storage import FileSystemStorage

import boto3
import uuid
from decouple import config
import os

ACCESS_KEY = config('ACCESS_KEY')
SECRET_KEY = config('SECRET_KEY_AWS')
REGION_NAME = config('REGION')

s3_client = boto3.client('s3',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,region_name=REGION_NAME)
s3_resource = boto3.resource('s3',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,region_name=REGION_NAME)

def create_bucket_name(bucket_prefix):
	return ''.join([bucket_prefix,str(uuid.uuid4())])

def create_bucket(bucket_prefix, s3_connection):
	bucket_name = create_bucket_name(bucket_prefix)
	location = {'LocationConstraint':REGION_NAME}
	bucket_response = s3_connection.create_bucket(Bucket=bucket_name,CreateBucketConfiguration=location)
	return bucket_name, bucket_response

def authorize(request):
    return render(request,'cloud_based_file_storage_system/home.html')

def home(request):
	buckets = UserBuckets.objects.filter(user=request.user)
	return render(request,'cloud_based_file_storage_system/dashboard.html',{"user":request.user,"buckets":buckets})

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'cloud_based_file_storage_system/loginuser.html', {'form':AuthenticationForm()})
    else:
        print('login ', request.POST['username'])
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'cloud_based_file_storage_system/loginuser.html', {'form':AuthenticationForm(), 'error':'Username and password did not match'})
        else:
            login(request, user)
            return redirect('home')

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'cloud_based_file_storage_system/signupuser.html', {'form':UserCreationForm()})
    else:
        if " " not in request.POST['username'] and request.POST['username'].isalpha():
            if request.POST['password1'] == request.POST['password2']:
                try:
                    user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                    user.save()
                    login(request, user)
                    return redirect('home')
                except IntegrityError:
                    return render(request, 'cloud_based_file_storage_system/signupuser.html', {'form':UserCreationForm(), 'error':'That username has already been taken. Please choose a new username'})
            else:
                return render(request, 'cloud_based_file_storage_system/signupuser.html', {'form':UserCreationForm(), 'error':'Passwords did not match'})
        else:
            return render(request, 'cloud_based_file_storage_system/signupuser.html', {'form':UserCreationForm(), 'error':'username should not contain any spaces, special symbols & numbers!'})

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('authorize')

@login_required
def addBucket(request):
	username = str(request.user).lower()
	bucket_name, bucket_response = create_bucket(bucket_prefix=username,s3_connection=s3_resource.meta.client)
	print(bucket_name,bucket_response)
	bucket = UserBuckets(Bucket_name=bucket_name,Bucket_Creation_time_stamp=timezone.now(),user=request.user)
	bucket.save()
	return render(request,'cloud_based_file_storage_system/dashboard.html',{'buckets':UserBuckets.objects.filter(user=request.user),'success':"Your bucket has been created with the name "+bucket_name})

@login_required
def showBuckets(request):
	buckets = UserBuckets.objects.filter(user=request.user)
	return render(request,'cloud_based_file_storage_system/userstorage.html',{'buckets':buckets})

@login_required
def deleteBucket(request,pk):
	bucket = UserBuckets.objects.get(pk=pk)
	bucket_name = bucket.Bucket_name
	files_in_bucket = UserFiles.objects.filter(bucket_id=pk)
	if files_in_bucket is None:
		s3_resource.Bucket(bucket_name).delete()
		bucket.delete()
	else:
		s3_resource.Bucket(bucket_name).objects.delete()
		s3_resource.Bucket(bucket_name).delete()
		bucket.delete()
		for file in files_in_bucket:
			file.delete()
	buckets = UserBuckets.objects.filter(user=request.user)
	return render(request,'cloud_based_file_storage_system/userstorage.html',{'buckets':buckets,'error':"Your bucket "+bucket_name+" has been deleted successfully!"})


@login_required
def addFiles(request,pk):
	if request.method=="GET":
		return render(request,'cloud_based_file_storage_system/addfiles.html')
	else:
		if request.method == 'POST' and request.FILES['myfile']:
			bucket = UserBuckets.objects.get(pk=pk)
			bucket_name = bucket.Bucket_name
			myfile = request.FILES['myfile']
			fs = FileSystemStorage()
			filename = fs.save(myfile.name, myfile)
			uploaded_file_url = fs.url(filename)
			file_size = os.path.getsize('media/'+filename)
			print("File Size is :", file_size, "bytes")
			s3_url = "https://"+bucket_name+".s3.ap-south-1.amazonaws.com/"+filename
			s3_client.upload_file('media/'+filename,bucket_name,filename,ExtraArgs={'ACL':'public-read'})
			user_file = UserFiles(File_name=filename,File_Creation_time_stamp=timezone.now(),File_description=request.POST['filedescription'],File_url=s3_url,File_size=file_size,bucket_id=pk)
			user_file.save()
			return render(request, 'cloud_based_file_storage_system/addfiles.html', {'uploaded_file_url': s3_url,"success":"Your file "+filename+" has been added in your folder "+bucket_name + "\n Redirecting to the home page!"})

@login_required
def viewFiles(request,pk):
	user_bucket_files = UserFiles.objects.filter(bucket_id=pk)
	return render(request,"cloud_based_file_storage_system/viewfiles.html",{'bucket_files':user_bucket_files})

@login_required
def deleteFile(request,pk):
	file = UserFiles.objects.get(pk=pk)
	filename = file.File_name
	bucket_file = file.bucket_id
	bucket = UserBuckets.objects.get(pk=bucket_file)
	bucket_name = bucket.Bucket_name
	s3_resource.Object(bucket_name, filename).delete()
	file.delete()
	user_bucket_files = UserFiles.objects.filter(bucket_id=bucket_file)
	return render(request,"cloud_based_file_storage_system/viewfiles.html",{'bucket_files':user_bucket_files,'danger':"Your file "+filename+" has been deleted successfully from the "+bucket_name+" folder."})
