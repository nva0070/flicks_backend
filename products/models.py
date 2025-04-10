from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, Group, Permission
from .utils.media_processors import (
    process_video, 
    process_product_image, 
    process_banner_image
)
from django.utils import timezone

def validate_image(file):
    """Validate that the file is an image."""
    if not file:
        return
        
    ext = file.name.split('.')[-1].lower()
    valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    
    if ext not in valid_extensions:
        raise ValidationError('Unsupported file format. Please upload JPG, JPEG, PNG, GIF or WEBP file.')
    
    # Check file size (5MB max)
    if file.size > 5 * 1024 * 1024:
        raise ValidationError('Image file too large. Please upload a file smaller than 5MB.')

def validate_video(file):
        """Validate that the file is a video in allowed format."""
        if not file:
            return
            
        ext = file.name.split('.')[-1].lower()
        valid_extensions = ['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm']
        
        if ext not in valid_extensions:
            raise ValidationError('Unsupported file format. Please upload MP4, MOV, AVI, WMV, FLV or WebM file.')
        
        # Check file size (10MB max)
        if file.size > 100 * 1024 * 1024:
            raise ValidationError('Video file too large. Please upload a file smaller than 10MB.')

class ShopUser(AbstractUser):
    OWNER = 'owner'
    HELPER = 'helper'
    
    ROLE_CHOICES = [
        (OWNER, 'Shop Owner'),
        (HELPER, 'Helper'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=HELPER,
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True,
        help_text="Phone number in international format"
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='products_user_set',
        related_query_name='products_user',
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='products_user_set',  
        related_query_name='products_user',
    )
   
    def __str__(self):
        return self.username

class Manufacturer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    banner = models.ImageField(
        upload_to='manufacturers/banners/', 
        blank=True, 
        null=True,
        validators=[validate_image],
        help_text="Upload a banner image (JPG, PNG, GIF, WEBP, max 5MB)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Process banner image to 1280x720
        if self.banner and hasattr(self.banner, 'file') and not kwargs.pop('no_process', False):
            self.banner = process_banner_image(self.banner)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Distributor(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    manufacturers = models.ManyToManyField(
        Manufacturer, 
        related_name='distributors',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        if not self.email and not self.phone:
            raise ValidationError('At least one contact method (email/phone) is required')

class Product(models.Model):
    GENDER_CHOICES=[
        ('M','Male'),
        ('F','Female'),
        ('U','Unisex'),
    ]

    title=models.CharField(max_length=200)
    manufacturer = models.ForeignKey(
        Manufacturer, 
        on_delete=models.CASCADE, 
        related_name='products',
        null=True,
        blank=True
    )
    product_category=models.CharField(max_length=100)
    age_group = models.CharField(max_length=20)

    STANDARD_AGE_CHOICES = [
        ("0-18 Months", "0-18 Months"),
        ("18-36 Months", "18-36 Months"),
        ("3-5 Years", "3-5 Years"),
        ("5-7 Years", "5-7 Years"),
        ("7-12 Years", "7-12 Years"),
        ("12+ Years", "12+ Years"),
    ]
    standardized_age = models.CharField(
        max_length=20, 
        choices=STANDARD_AGE_CHOICES,
        blank=True
    )
    
    brand=models.CharField(max_length=100)
    gender=models.CharField(max_length=1,choices=GENDER_CHOICES,default='U')
    description=models.TextField()
    flicks = models.FileField(
        upload_to='products/flicks/', 
        blank=True, 
        null=True,
        validators=[validate_video],
        help_text="Upload video file (MP4, MOV, AVI, WMV, FLV or WebM, max 10MB)"
    )
    video_duration = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Duration of the video in seconds"
    )

    def primary_image(self):
        """Get primary image from the ProductImage model"""
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image
        # Fallback to legacy image field
        return self.image

    def primary_image(self):
        """Get primary image from the ProductGallery model"""
        primary = self.gallery.filter(is_primary=True, media_type='image').first()
        if primary and primary.image:
            return primary.image
        return None

    # Remove the primary_video method if you don't want that concept
    # Or replace it with a method that just returns the flicks field
    def get_video(self):
        """Get the product video"""
        return self.flicks

    def all_gallery_items(self):
        """Get all gallery items, ordered by display priority"""
        return self.gallery.all()

    def gallery_images(self):
        """Get all images from gallery"""
        return self.gallery.filter(media_type='image')

    def gallery_videos(self):
        """Get all videos from gallery"""
        return self.gallery.filter(media_type='video')

    def save(self, *args, **kwargs):
        if self.flicks and hasattr(self.flicks, 'file') and not kwargs.pop('no_process', False):
            self.flicks, duration = process_video(self.flicks)
            if duration:
                self.video_duration = duration
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ProductGallery(models.Model):
    """Gallery items for product (images and videos)"""
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    product = models.ForeignKey(
        'Product',  
        on_delete=models.CASCADE,
        related_name='gallery'
    )
    media_type = models.CharField(
        max_length=5,
        choices=MEDIA_TYPE_CHOICES,
        default='image'
    )
    image = models.ImageField(
        upload_to='products/photos/',
        validators=[validate_image],
        null=True,
        blank=True,
        help_text="Upload a product image (JPG, PNG, GIF, WEBP, max 5MB)"
    )
    video = models.FileField(
        upload_to='products/videos/',
        validators=[validate_video],
        null=True,
        blank=True,
        help_text="Upload a product video (MP4, MOV, AVI, WMV, FLV or WebM, max 10MB)"
    )
    video_duration = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Duration of the video in seconds"
    )
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=100, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'display_order', 'created_at']
        verbose_name = 'Product Gallery Item'
        verbose_name_plural = 'Product Gallery'
    
    def __str__(self):
        media_type_str = 'Video' if self.media_type == 'video' else 'Image'
        primary_str = 'Primary' if self.is_primary else 'Secondary'
        return f"{media_type_str} for {self.product.title} ({primary_str})"
    
    def clean(self):
        """Validate that only one media type is provided"""
        if self.media_type == 'image' and not self.image:
            raise ValidationError('Image file is required for image media type')
        if self.media_type == 'video' and not self.video:
            raise ValidationError('Video file is required for video media type')
        
        if self.media_type == 'image' and self.video:
            # If switching from video to image, clear video field
            self.video = None
            self.video_duration = None
        elif self.media_type == 'video' and self.image:
            # If switching from image to video, clear image field
            self.image = None
    
    def save(self, *args, **kwargs):
        # Process image if provided
        if self.media_type == 'image' and self.image and hasattr(self.image, 'file') and not kwargs.pop('no_process', False):
            from .media_processor import process_product_image
            self.image = process_product_image(self.image)
        
        # Process video if provided
        if self.media_type == 'video' and self.video and hasattr(self.video, 'file') and not kwargs.pop('no_process', False):
            try:
                from .media_processor import process_video
                result = process_video(self.video)
                
                # Make sure we have a tuple of length 2
                if isinstance(result, tuple) and len(result) == 2:
                    processed_video, duration = result
                    self.video = processed_video
                    if duration is not None:
                        self.video_duration = duration
                else:
                    # Log unexpected result format
                    print(f"Warning: process_video returned unexpected format: {result}")
            except Exception as e:
                # Log exception
                print(f"Error while processing video in ProductGallery: {str(e)}")
        
        # Handle primary flag (ensure only one primary media per product)
        if self.is_primary:
            # First, ensure we're only competing with the same media type
            ProductGallery.objects.filter(
                product=self.product, 
                media_type=self.media_type,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        
        # Make first gallery item primary by default
        if not self.pk and not ProductGallery.objects.filter(
            product=self.product, 
            media_type=self.media_type
        ).exists():
            self.is_primary = True
            
        super().save(*args, **kwargs)

class Shop(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    banner = models.ImageField(
        upload_to='shops/banners/', 
        blank=True, 
        null=True,
        validators=[validate_image],
        help_text="Upload a banner image (JPG, PNG, GIF, WEBP, max 5MB)"
    )
    owner = models.ForeignKey(
        ShopUser,
        on_delete=models.CASCADE,
        related_name='shops'
    )
    helpers = models.ManyToManyField(
        ShopUser,
        related_name='helper_at_shops',
        blank=True,
        limit_choices_to={'role': ShopUser.HELPER}
    )
    
    def save(self, *args, **kwargs):
        if self.banner and hasattr(self.banner, 'file') and not kwargs.pop('no_process', False):
            self.banner = process_banner_image(self.banner)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    FREE = 'free'
    BASIC = 'basic'
    PREMIUM = 'premium'
    
    PLAN_CHOICES = [
        (FREE, 'Free'),
        (BASIC, 'Basic'),
        (PREMIUM, 'Premium'),
    ]
    
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default=FREE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    features = models.JSONField(default=list)  # Store features as a JSON array
    
    def __str__(self):
        return f"{self.shop.name} - {self.get_plan_display()}"

class FeaturedProduct(models.Model):
    FEATURED_TYPE_CHOICES = [
        ('trending', 'Trending Products'),
        ('top', 'Top Products'),
    ]
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='featured_placements'
    )
    featured_type = models.CharField(
        max_length=10, 
        choices=FEATURED_TYPE_CHOICES
    )
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['featured_type', 'display_order']
        unique_together = ['product', 'featured_type']
    
    def __str__(self):
        return f"{self.product.title} - {self.get_featured_type_display()}"


class FlicksAnalytics(models.Model):
    """Aggregate analytics for product flicks/videos"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='flicks_analytics')
    views = models.PositiveIntegerField(default=0)
    total_watch_time = models.PositiveIntegerField(default=0)  # in seconds
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def average_watch_time(self):
        """Calculate average watch time in seconds"""
        return round(self.total_watch_time / self.views, 2) if self.views > 0 else 0

    def __str__(self):
        return f"Analytics for {self.product.title}"

class ViewSession(models.Model):
    """Individual viewing sessions"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='view_sessions')
    user = models.ForeignKey(ShopUser, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.JSONField(default=dict, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(default=0)  # in seconds
    completed = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"Session {self.id} for {self.product.title}"