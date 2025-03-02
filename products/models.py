from django.db import models

# Create your models here.

class Product(models.Model):
    GENDER_CHOICES=[
        ('M','Male'),
        ('F','Female'),
        ('U','Unisex'),
    ]


    title=models.CharField(max_length=200)
    product_category=models.CharField(max_length=100)
    age_group=models.CharField(max_length=20)
    brand=models.CharField(max_length=100)
    gender=models.CharField(max_length=1,choices=GENDER_CHOICES,default='U')
    description=models.TextField()
    
    def __str__(self):
        return self.title