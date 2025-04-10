from rest_framework import serializers
from .models import (
    ShopUser, Manufacturer, Distributor, Product, Shop, 
    Subscription, ProductGallery, FlicksAnalytics, ViewSession
)

class ShopUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = ShopUser.objects.create_user(**validated_data)
        return user


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'


class DistributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distributor
        fields = '__all__'

class ProductGallerySerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductGallery
        fields = ['id', 'media_type', 'image', 'video', 'is_primary', 'alt_text', 'display_order', 'url']
    
    def get_url(self, obj):
        if obj.media_type == 'image' and obj.image:
            return obj.image.url
        elif obj.media_type == 'video' and obj.video:
            return obj.video.url
        return None
        
class ProductSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    gallery_items = ProductGallerySerializer(many=True, read_only=True, source='gallery.all')
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'brand', 'product_category', 'age_group', 
                  'gender', 'description', 'manufacturer_name', 'image_url', 
                  'video_url', 'gallery_items']
    
    def get_manufacturer_name(self, obj):
        return obj.manufacturer.name if obj.manufacturer else None
    
    def get_image_url(self, obj):
        # Get primary image from gallery
        primary_item = obj.gallery.filter(is_primary=True, media_type='image').first()
        if primary_item and primary_item.image:
            return primary_item.image.url
        # Fallback to flicks field if no primary image
        if obj.flicks:
            return obj.flicks.url
        return None
        
    def get_video_url(self, obj):
        # Return the flicks field
        if obj.flicks:
            return obj.flicks.url
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    gallery = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'brand', 'product_category', 'age_group', 
                 'gender', 'description', 'manufacturer_name', 
                 'image_url', 'video_url', 'gallery']
    
    def get_manufacturer_name(self, obj):
        return obj.manufacturer.name if obj.manufacturer else None
    
    def get_image_url(self, obj):
        primary = obj.gallery.filter(is_primary=True, media_type='image').first()
        if primary and primary.image:
            return primary.image.url
        return None
        
    def get_video_url(self, obj):
        # Just return the main flicks field
        if obj.flicks:
            return obj.flicks.url
        return None
        
    def get_gallery(self, obj):
        """Get all gallery items with their metadata"""
        result = []
        for item in obj.gallery.all():
            item_data = {
                'id': item.id,
                'type': item.media_type,
                'is_primary': item.is_primary,
                'alt_text': item.alt_text,
                'display_order': item.display_order,
            }
            
            if item.media_type == 'image' and item.image:
                item_data['url'] = item.image.url
            elif item.media_type == 'video' and item.video:
                item_data['url'] = item.video.url
                item_data['duration'] = item.video_duration
                
            result.append(item_data)
            
        return result

class ShopSerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.username')
    helper_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Shop
        fields = [
            'id', 'name', 'description', 'address', 'phone', 'email', 
            'banner', 'owner', 'owner_name', 'helpers', 'helper_count'
        ]
    
    def get_helper_count(self, obj):
        return obj.helpers.count()

class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'plan_name', 'start_date', 'end_date', 'is_active', 'features']
    
    def get_plan_name(self, obj):
        return obj.get_plan_display()

class FlicksAnalyticsSerializer(serializers.ModelSerializer):
    average_watch_time = serializers.SerializerMethodField()
    
    class Meta:
        model = FlicksAnalytics
        fields = ['views', 'total_watch_time', 'average_watch_time']
    
    def get_average_watch_time(self, obj):
        return obj.average_watch_time

class ViewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewSession
        fields = ['id', 'session_id', 'start_time', 'end_time', 'duration', 'completed']