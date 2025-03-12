from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Group, Permission

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
    image = models.ImageField(upload_to='media/', blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    
class Shop(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
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