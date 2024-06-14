"""
URL configuration for proj1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from prji.views import upload_csv 
from prji.views import upload_success
from prji.views import barchart
from prji.views import all_data
from prji.views import combined_pie_charts
from prji.views import analyze_graph
from prji.views import google_form
from prji.views import visualize_student_heatmap
from prji.views import homepage
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('',homepage , name='root'),
    path('admin/', admin.site.urls),
    path('homepage/', homepage, name='homepage'),
    path('upload_csv/', upload_csv, name='upload_csv'),
    path('upload_success/', upload_success, name='upload_success'),
    path('barchart/', barchart, name='barchart'),
    path('all_data/', all_data, name='all_data'),
    path('combined_pie_charts/', combined_pie_charts, name='combined_pie_charts'),
    path('analyze_graph/', analyze_graph, name='analyze_graph'),
    path('google_form/', google_form, name='google_form'),
    path('visualize_student_heatmap/', visualize_student_heatmap, name='visualize_student_heatmap'), 

    
]
    
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    

 