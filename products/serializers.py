from rest_framework import serializers
from .models import Order, OrderItem, Reward, ShopUser, Manufacturer, Distributor, Product, Shop, Subscription, UserReward


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


class ProductSerializer(serializers.ModelSerializer):
    manufacturer_name = serializers.ReadOnlyField(source='manufacturer.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'manufacturer', 'manufacturer_name', 'product_category', 
            'age_group', 'brand', 'gender', 'description', 'image', 'flicks'
        ]


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



class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'customer_name', 'status', 'total', 'created_at', 'items']
    
    def get_items(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.title')
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price']

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = ['id', 'name', 'description', 'points_required', 'valid_on', 'is_active']

class UserRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReward
        fields = ['id', 'type', 'description', 'points', 'date']

class SubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'plan_name', 'start_date', 'end_date', 'is_active', 'features']
    
    def get_plan_name(self, obj):
        return obj.get_plan_display()