from django.db import models
from django.core.exceptions import ValidationError

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
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return self.title