from rest_framework import serializers
from .models import ShopUser, Manufacturer, Distributor, Product, Shop, Subscription, ProductImage, FlicksAnalytics, ViewSession


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

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'alt_text']
        
class ProductSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True, source='images.all')
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'brand', 'product_category', 'age_group', 
                  'gender', 'description', 'manufacturer_name', 'image_url', 'images', 'video_url']
    
    def get_manufacturer_name(self, obj):
        return obj.manufacturer.name if obj.manufacturer else None
    
    def get_image_url(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image.url
        return None

    def get_video_url(self, obj):
        if obj.flicks:
            return obj.flicks.url
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True, source='images.all')
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'brand', 'product_category', 'age_group', 
                 'gender', 'description', 'manufacturer_name', 
                 'image_url', 'video_url', 'images']
    
    def get_manufacturer_name(self, obj):
        return obj.manufacturer.name if obj.manufacturer else None
    
    def get_image_url(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image.image.url
        return None
        
    def get_video_url(self, obj):
        if obj.flicks:
            return obj.flicks.url
        return None


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