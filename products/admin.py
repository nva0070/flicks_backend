from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
import csv
import pandas as pd
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from .models import Manufacturer, Product, Distributor


def setup_groups():
    staff_group, created = Group.objects.get_or_create(name='Staff')
    
    content_type = ContentType.objects.get_for_model(Product)
    product_permissions = Permission.objects.filter(content_type=content_type)
    staff_group.permissions.set(product_permissions)

    manufacturer_content_type = ContentType.objects.get_for_model(Manufacturer)
    manufacturer_permissions = Permission.objects.filter(content_type=manufacturer_content_type)
    staff_group.permissions.add(*manufacturer_permissions)

class FileUploadForm(forms.Form):
    file = forms.FileField(
        label='Select a file',
        help_text='Allowed formats: .csv, .xlsx'
    )

    def clean_file(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1].lower()
        if ext not in ['csv', 'xlsx']:
            raise forms.ValidationError('Only CSV and XLSX files are allowed')
        return file


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone']
    change_form_template = 'admin/manufacturer_change_form.html'
    
    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('upload-csv/<int:manufacturer_id>/', self.upload_csv, name='upload-csv'),
        ]
        return new_urls + urls

    def upload_csv(self, request, manufacturer_id):
        if request.method == "POST":
            try:
                manufacturer = Manufacturer.objects.get(id=manufacturer_id)
                uploaded_file = request.FILES["file"]
                ext = uploaded_file.name.split('.')[-1].lower()

                if ext == 'csv':
                    decoded_file = uploaded_file.read().decode('utf-8').splitlines()
                    data = list(csv.DictReader(decoded_file))
                else:  # xlsx
                    data = pd.read_excel(uploaded_file).to_dict('records')

                for row in data:
                    Product.objects.create(
                        manufacturer=manufacturer,
                        title=row['Title'],
                        product_category=row['Product Category'],
                        age_group=row['Age Group'],
                        brand=row['Brand'],
                        gender=row['Gender'],
                        description=row['SEO Description'],
                        price=row['Variant Price']
                    )
                
                self.message_user(request, "File imported successfully")
            except Exception as e:
                self.message_user(request, f"Error importing file: {str(e)}", level='ERROR')
            return redirect("admin:products_manufacturer_change", manufacturer_id)
        
        form = FileUploadForm()
        return render(request, "admin/csv_upload.html", {'form': form})

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'product_category')
    list_filter = ('product_category', 'brand', 'gender')
    search_fields = ('title', 'brand', 'description')

@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'email', 'phone']
    filter_horizontal = ['manufacturers']
    search_fields = ['name', 'location', 'email']

default_app_config = 'products.apps.ProductsConfig'

def ready():
    setup_groups()