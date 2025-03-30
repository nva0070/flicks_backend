from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
import csv
import pandas as pd
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from .models import Manufacturer, Product, Distributor, ShopUser, Shop, ProductImage, FeaturedProduct
from django.utils.safestring import mark_safe

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
    list_display = ['name', 'email', 'phone', 'has_banner']
    readonly_fields = ['banner_preview']
    change_form_template = 'admin/manufacturer_change_form.html'
    
    def has_banner(self, obj):
        return bool(obj.banner)
    has_banner.boolean = True
    
    def banner_preview(self, obj):
        if obj.banner:
            return mark_safe(f'<img src="{obj.banner.url}" width="400" />')
        return "No banner image uploaded"
    banner_preview.short_description = "Banner Preview"
    
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone', 'address')
        }),
        ('Banner', {
            'fields': ('banner', 'banner_preview')
        }),
    )
    
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
                else:
                    data = pd.read_excel(uploaded_file).to_dict('records')

                for row in data:
                    # Map gender display value to database value
                    gender_value = row['Gender']
                    if gender_value.lower() == 'unisex':
                        gender_value = 'U'
                    elif gender_value.lower() == 'male':
                        gender_value = 'M'
                    elif gender_value.lower() == 'female':
                        gender_value = 'F'
                    else:
                        gender_value = 'U'  # Default to unisex
                    
                    Product.objects.create(
                        manufacturer=manufacturer,
                        title=row['Title'],
                        product_category=row['Product Category'],
                        age_group=row['Age Group'],
                        brand=row['Brand'],
                        gender=gender_value,  # Now using the correct database value
                        description=row['SEO Description']
                    )
                
                self.message_user(request, "File imported successfully")
            except Exception as e:
                self.message_user(request, f"Error importing file: {str(e)}", level='ERROR')
            return redirect("admin:products_manufacturer_change", manufacturer_id)
        
        form = FileUploadForm()
        return render(request, "admin/csv_upload.html", {'form': form})

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'is_primary', 'alt_text']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'product_category', 'has_media')
    list_filter = ('product_category', 'brand', 'gender')
    search_fields = ('title', 'brand', 'description')
    readonly_fields = ('image_preview', 'video_preview')
    inlines = [ProductImageInline]

    def has_media(self, obj):
        has_images = obj.images.exists()
        return bool(has_images or obj.flicks)
    has_media.boolean = True
    
    def image_preview(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return mark_safe(f'<img src="{primary.image.url}" width="300" />')
        return "No Image"
    image_preview.short_description = 'Image Preview'
    
    def video_preview(self, obj):
        if obj.flicks:
            return mark_safe(f'''
                <video width="320" height="240" controls>
                    <source src="{obj.flicks.url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            ''')
        return "No Video"
    video_preview.short_description = 'Video Preview'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'manufacturer', 'product_category', 'age_group', 'brand', 'gender')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Media', {
            'fields': ('image_preview', 'flicks', 'video_preview')  
        }),
    )

@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'email', 'phone']
    filter_horizontal = ['manufacturers']
    search_fields = ['name', 'location', 'email']

default_app_config = 'products.apps.ProductsConfig'

def ready():
    setup_groups()


class ShopAdminForm(forms.ModelForm):
    owner_username = forms.CharField(max_length=150, required=True)
    owner_email = forms.EmailField(required=True)
    owner_password = forms.CharField(widget=forms.PasswordInput, required=True)
    
    class Meta:
        model = Shop
        exclude = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields.pop('owner_username', None)
            self.fields.pop('owner_email', None)
            self.fields.pop('owner_password', None)

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    form = ShopAdminForm
    list_display = ['name', 'address', 'phone', 'email', 'owner', 'has_banner']
    readonly_fields = ['banner_preview']
    
    def has_banner(self, obj):
        return bool(obj.banner)
    has_banner.boolean = True
    
    def banner_preview(self, obj):
        if obj.banner:
            return mark_safe(f'<img src="{obj.banner.url}" width="400" />')
        return "No banner image uploaded"
    banner_preview.short_description = "Banner Preview"
    
    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return [
                (None, {'fields': ['name', 'description', 'address', 'phone', 'email']}),
                ('Shop Owner', {'fields': ['owner_username', 'owner_email', 'owner_password']}),
            ]
        return [
            (None, {'fields': ['name', 'description', 'address', 'phone', 'email']}),
            ('Banner', {'fields': ['banner', 'banner_preview']}),
            ('Shop Staff', {'fields': ['owner', 'helpers']}),
        ]
    
    # Keep the existing save_model and get_form methods
    def save_model(self, request, obj, form, change):
        if not change:
            owner = ShopUser.objects.create_user(
                username=form.cleaned_data['owner_username'],
                email=form.cleaned_data['owner_email'],
                password=form.cleaned_data['owner_password'],
                role=ShopUser.OWNER
            )
            obj.owner = owner
        super().save_model(request, obj, form, change)
        
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

@admin.register(ShopUser)
class ShopUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role']
    list_filter = ['role']

@admin.register(FeaturedProduct)
class FeaturedProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'featured_type', 'display_order']
    list_filter = ['featured_type']
    search_fields = ['product__title', 'product__brand', 'product__product_category']
    ordering = ['featured_type', 'display_order']
    list_editable = ['display_order'] 
    
    change_list_template = 'admin/change_list_with_manage_button.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('manage-featured/', self.admin_site.admin_view(self.manage_featured), 
                 name='manage-featured-products'),
            path('save-featured/', self.admin_site.admin_view(self.save_featured),
                 name='save-featured-products'),
        ]
        return custom_urls + urls
        
    def manage_featured(self, request):
        trending_items = FeaturedProduct.objects.filter(
            featured_type='trending'
        ).order_by('display_order')
        
        top_items = FeaturedProduct.objects.filter(
            featured_type='top'
        ).order_by('display_order')
        
        available_products = Product.objects.all().order_by('title')
        
        context = {
            'title': 'Manage Featured Products',
            'trending_items': trending_items,
            'top_items': top_items,
            'available_products': available_products,
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/manage_featured_products.html', context)
        
    def save_featured(self, request):
        if request.method != 'POST':
            return redirect('admin:products_featuredproduct_changelist')
            
        trending_ids = request.POST.get('trending_ids', '').split(',')
        top_ids = request.POST.get('top_ids', '').split(',')
        
        trending_ids = [id for id in trending_ids if id]
        top_ids = [id for id in top_ids if id]
        
        FeaturedProduct.objects.all().delete()
        
        for i, product_id in enumerate(trending_ids):
            FeaturedProduct.objects.create(
                product_id=product_id,
                featured_type='trending',
                display_order=i
            )
            
        for i, product_id in enumerate(top_ids):
            FeaturedProduct.objects.create(
                product_id=product_id,
                featured_type='top',
                display_order=i
            )
            
        self.message_user(request, 'Featured products updated successfully.')
        return redirect('admin:products_featuredproduct_changelist')