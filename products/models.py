from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Group, Permission

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
    
    def clean(self):
        if self.owner and self.owner.role != ShopUser.OWNER:
            raise ValidationError("The shop owner must have the 'Shop Owner' role.")
            
        if self.pk and self.helpers.filter(pk=self.owner.pk).exists():
            raise ValidationError("The shop owner cannot be a helper at the same time.")

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
    def validate_video(file):
        """Validate that the file is a video in allowed format."""
        if not file:
            return
            
        ext = file.name.split('.')[-1].lower()
        valid_extensions = ['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm']
        
        if ext not in valid_extensions:
            raise ValidationError('Unsupported file format. Please upload MP4, MOV, AVI, WMV, FLV or WebM file.')
        
        # Check file size (10MB max)
        if file.size > 10 * 1024 * 1024:
            raise ValidationError('Video file too large. Please upload a file smaller than 10MB.')

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
    age_group=models.CharField(max_length=20)
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

    def primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image
        # Fallback to legacy image field
        return self.image

    def all_images(self):
        return self.images.all()

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(
        'Product',  
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='products/photos/',
        validators=[validate_image]
    )
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.title} ({'Primary' if self.is_primary else 'Secondary'})"
    
    def save(self, *args, **kwargs):
        # If this is marked as primary, unmark other images
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, 
                is_primary=True
            ).update(is_primary=False)
        
        # If this is the first image, make it primary
        if not self.pk and not ProductImage.objects.filter(product=self.product).exists():
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