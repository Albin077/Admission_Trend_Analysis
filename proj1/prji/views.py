
from django.shortcuts import render, redirect
import pandas as pd
from .forms import UploadCSVForm
from .models import CSVModel
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Count
import qrcode
from django.conf import settings
import os
import geopandas as gpd



from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError



def upload_csv(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']

            # Read CSV into a Pandas DataFrame
            df = pd.read_csv(csv_file)

            # Get list of Campus IDs from the CSV file
            csv_campus_ids = df['Campus_id'].tolist()

            # Check if any Campus IDs from the CSV file already exist in the database
            existing_entries = CSVModel.objects.filter(Campus_id__in=csv_campus_ids)
            
            # If any existing Campus IDs found, render a message
            if existing_entries.exists():
                existing_campus_ids = existing_entries.values_list('Campus_id', flat=True)
                return render(request, 'upload_duplicate.html', {'existing_entries': existing_campus_ids})

            # If no existing Campus IDs found, save DataFrame rows to the database
            for _, row in df.iterrows():
                CSVModel.objects.create(
                    Campus_id=row['Campus_id'],
                    Name=row.get('Name'),
                    Age=row['Age'],
                    Gender=row.get('Gender'),
                    Address=row.get('Address'),
                    PUC_Background=row.get('PUC_Background'),
                    PUC_Marks=row['PUC_Marks'],
                    Batch=row['Batch'],
                    Course=row.get('Course')
                )

            return redirect('upload_success')
    else:
        form = UploadCSVForm()

    return render(request, 'upload_form.html', {'form': form})

def upload_success(request):
    return render(request, 'upload_success.html')

def barchart(request):
    # Retrieve data from the PostgreSQL database
    queryset = CSVModel.objects.all()
    df = pd.DataFrame(list(queryset.values()))

    # Clean the 'course' column to remove leading/trailing whitespaces
    df['Course'] = df['Course'].str.strip()

    # Group the data by 'cource' and 'entry_academic_period' and count the number of students for each group
    course_year_counts = df.groupby(['Course', 'Batch']).size().reset_index(name='count')

    # Pivot the table for better visualization
    pivot_table = course_year_counts.pivot(index='Batch', columns='Course', values='count')

    # Plotting the bar chart
    pivot_table.plot(kind='bar', figsize=(12, 8))
    plt.title('Number of Students Joined Each Course Every Year')
    plt.xlabel('Academic Period')
    plt.ylabel('Number of Students')
    plt.xticks(rotation=45)
    plt.legend(title='Course')

    # Save the chart to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    # Encode the BytesIO object to base64 for display in HTML
    chart_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Render the result in a template
    return render(request, 'bar_chart.html', {'chart_base64': chart_base64})


def combined_pie_charts(request):
    # Retrieve data from the PostgreSQL database
    queryset = CSVModel.objects.all()
    df = pd.DataFrame(list(queryset.values()))

    # Count the occurrences of each gender
    gender_counts = df['Gender'].value_counts()

    # Count the occurrences of each place
    place_counts = df['Address'].value_counts()

    # Count the occurrences of each PUC background
    puc_background_counts = df['PUC_Background'].value_counts()

    #count the occurence of each course
    course_counts = df['Course'].value_counts()
    #count the occurence of age
    age_counts = df['Age'].value_counts()
    #count the occurence of puc mark
    puc_mark_counts = df['PUC_Marks'].value_counts()

    # Create a pie chart for gender
    plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('Gender Distribution')
    gender_buffer = BytesIO()
    plt.savefig(gender_buffer, format='png')
    plt.close()

    # Create a pie chart for place
    plt.pie(place_counts, labels=place_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('Place Distribution')
    place_buffer = BytesIO()
    plt.savefig(place_buffer, format='png')
    plt.close()

    # Create a pie chart for PUC background
    plt.pie(puc_background_counts, labels=puc_background_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('PUC Background Distribution')
    puc_background_buffer = BytesIO()
    plt.savefig(puc_background_buffer, format='png')
    plt.close()

    #create pie chart for cource

    plt.pie(course_counts, labels=course_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('Course')
    course_buffer = BytesIO()
    plt.savefig(course_buffer, format='png')
    plt.close()

    #create pie chart for age

    plt.pie(age_counts, labels=age_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('Age')
    age_buffer = BytesIO()
    plt.savefig(age_buffer, format='png')
    plt.close()


    #create pie chart for cource

    plt.pie(puc_mark_counts, labels=puc_mark_counts.index, autopct='%1.1f%%', startangle=90)
    plt.title('PUC_Marks')
    puc_mark_buffer = BytesIO()
    plt.savefig(puc_mark_buffer, format='png')
    plt.close()

    # Encode the BytesIO objects to base64 for display in HTML
    gender_chart_base64 = base64.b64encode(gender_buffer.getvalue()).decode('utf-8')
    place_chart_base64 = base64.b64encode(place_buffer.getvalue()).decode('utf-8')
    puc_background_chart_base64 = base64.b64encode(puc_background_buffer.getvalue()).decode('utf-8')
    course_chart_base64 = base64.b64encode(course_buffer.getvalue()).decode('utf-8')
    age_chart_base64 = base64.b64encode(age_buffer.getvalue()).decode('utf-8')
    puc_mark_chart_base64 = base64.b64encode(puc_mark_buffer.getvalue()).decode('utf-8')

    # Render the result in a template
    return render(request, 'combined_pie_charts.html', {
        'gender_chart_base64': gender_chart_base64,
        'place_chart_base64': place_chart_base64,
        'puc_background_chart_base64': puc_background_chart_base64,
        'course_chart_base64': course_chart_base64,
        'age_chart_base64': age_chart_base64,
        'puc_mark_chart_base64': puc_mark_chart_base64,
    })

from django.http import JsonResponse
from django.template.loader import render_to_string

def all_data(request):
    # Fetch all data from CSVModel
    data = CSVModel.objects.all()

    # Sorting options
    sort_by = request.GET.get('sort_by')

    # Sort data based on the selected field
    if sort_by:
        data = data.order_by(sort_by)

    context = {
        'data': data,
        'sort_by': sort_by
    }
    return render(request, 'all_data.html', context)


def analyze_graph(request):
    # Retrieve data from the PostgreSQL database
    queryset = CSVModel.objects.all()
    df = pd.DataFrame(list(queryset.values()))

    # Clean the 'cource' column to remove leading/trailing whitespaces
    df['Course'] = df['Course'].str.strip()

    # Get unique academic periods and courses
    academic_periods = df['Batch'].unique()
    courses = df['Course'].unique()

    # Create a DataFrame with all combinations of academic periods and courses
    index = pd.MultiIndex.from_product([academic_periods, courses], names=['Batch', 'Course'])
    course_year_counts = df.groupby(['Batch', 'Course']).size().reindex(index, fill_value=0).reset_index(name='count')

    # Pivot the table for better visualization
    pivot_table = course_year_counts.pivot(index='Batch', columns='Course', values='count').fillna(0)

    # Plotting the line graph
    pivot_table.plot(kind='line', figsize=(12, 8))
    plt.title('Courses Year-wise Progress')
    plt.xlabel('Academic Period')
    plt.ylabel('Number of Students')
    plt.xticks(rotation=45)
    plt.legend(title='Course')

    # Save the chart to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    # Encode the BytesIO object to base64 for display in HTML
    graph_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Render the result in a template
    return render(request, 'analyze_graph.html', {'graph_base64': graph_base64}) 

import io
def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

def google_form(request):
    google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfpmPoX49pbjly211UGUEo00CO_aJZyaVsHUmR7jCjCmZu8Ug/viewform?usp=sf_link"

    # Generate QR code for the Google Form URL
    qr_code_img_base64 = generate_qr_code(google_form_url)

    context = {
        'google_form_url': google_form_url,
        'qr_code_img_base64': qr_code_img_base64,
    }
    return render(request, 'google_form.html', context)


import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from io import BytesIO
import base64
from django.shortcuts import render
from .models import CSVModel
from django.conf import settings
import geopandas as gpd

def visualize_student_heatmap(request):
    # Manually assign latitude and longitude for Kerala, Tamil Nadu, and Karnataka
    places = {
        'kerala': (10.8505, 76.2711),
        'tamilnadu': (11.1271, 78.6569),
        'karnataka': (15.3173, 75.7139)
    }
    
    # Count the number of students from each place
    place_counts = {
        'kerala': 0,
        'tamilnadu': 0,
        'karnataka': 0
    }
    
    # Assuming 'CSVModel' is your Django model
    queryset = CSVModel.objects.all()
    for obj in queryset:
        if obj.Address in place_counts:
            place_counts[obj.Address] += 1

    # Plot the heatmap
    fig, ax = plt.subplots(figsize=(10, 8))

    # Specify the path to the India shapefile using the settings
    shapefile_path = os.path.join(settings.SHAPEFILES_DIR, 'Political_map_2019.shp')

    # Read India map data
    india_map = gpd.read_file(shapefile_path)
    india_map.plot(ax=ax, color='lightgrey')

    max_count = max(place_counts.values())
    min_count = min(place_counts.values())
    norm = Normalize(vmin=min_count, vmax=max_count)
    
    # Create a custom colormap from green to red
    colors = [(0, 1, 0), (1, 0, 0)]  # Green to Red
    colormap = LinearSegmentedColormap.from_list('green_red', colors)
    
    for place, (lat, lon) in places.items():
        count = place_counts.get(place, 0)
        color = colormap(norm(count))
        ax.scatter(lon, lat, color=color, s=100, label=place)

    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Student Density')

    ax.legend()
    ax.set_title('Student Heatmap by Place')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    # Encode the plot image to base64
    chart_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render(request, 'student_heatmap.html', {'chart_base64': chart_base64})

def homepage(request):
    return render(request, 'homepage.html')