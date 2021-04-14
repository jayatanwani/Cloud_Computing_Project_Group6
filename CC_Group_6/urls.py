"""cloud_based_file_storage_application URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from cloud_based_file_storage_system import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.authorize,name='authorize'),
    path('login/',views.loginuser,name='loginuser'),
    path('signup/',views.signupuser,name='signupuser'),
    path('logout/',views.logoutuser,name='logoutuser'),
    path('home/',views.home,name='home'),
    path('addBucket/',views.addBucket,name='addBucket'),
    path('showBuckets/',views.showBuckets,name='showBuckets'),
    path('deleteBucket/<int:pk>',views.deleteBucket,name='deleteBucket'),
    path('addFiles/<int:pk>',views.addFiles,name='addFiles'),
    path('viewFiles/<int:pk>',views.viewFiles,name='viewFiles'),
    path('deleteFile/<int:pk>',views.deleteFile,name='deleteFile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
