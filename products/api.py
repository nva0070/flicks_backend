from django.http import JsonResponse
from products.models import Shop, ShopUser, Product
from products.serializers import (
    ProductSerializer, ProductDetailSerializer 
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
import json

# Authentication endpoints
@api_view(['POST'])
@permission_classes([AllowAny]) 
def register_user(request):
    """Register a new user"""
    try:
        data = request.data
        serializer = ShopUserSerializer(data=data)
        
        if serializer.is_valid():
            # Create ShopUser with role
            user = serializer.save(role=request.data.get('role', ShopUser.HELPER))
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'User registered successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': user.role
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login a user"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'role': user.role
        })
    
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def store_info(request):
    """Get store information for the logged-in user"""
    user = request.user
    
    # Find the shop associated with this user (either as owner or helper)
    shop = None
    if hasattr(user, 'shops'):
        shop_queryset = user.shops.all()
        if shop_queryset.exists():
            shop = shop_queryset.first()
    
    # If not found as owner, check as helper
    if not shop and hasattr(user, 'helper_at_shops'):
        helper_shops = user.helper_at_shops.all()
        if helper_shops.exists():
            shop = helper_shops.first()
    
    if not shop:
        return Response(
            {"error": "No shop found for this user"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Try to get subscription info
    subscription_data = None
    try:
        # Notice the relationship - shop has a OneToOneField to Subscription called 'subscription'
        subscription = Subscription.objects.filter(shop=shop, is_active=True).first()
        if subscription:
            subscription_data = {
                'plan': subscription.get_plan_display(),
                'days_remaining': (subscription.end_date - timezone.now().date()).days,
                'start_date': subscription.start_date.strftime('%Y-%m-%d'),
                'end_date': subscription.end_date.strftime('%Y-%m-%d')
            }
    except Exception as e:
        # Log the error but don't fail the entire request
        print(f"Error retrieving subscription: {e}")
    
    # Build the response
    store_data = {
        'id': shop.id,
        'name': shop.name,
        'description': shop.description,
        'address': shop.address,
        'phone': shop.phone,
        'email': shop.email,
        'banner_url': request.build_absolute_uri(shop.banner.url) if shop.banner else None,
        'owner': {
            'id': shop.owner.id,
            'username': shop.owner.username,
            'name': f"{shop.owner.first_name} {shop.owner.last_name}".strip() or shop.owner.username
        },
        'subscription': subscription_data,
        'is_owner': shop.owner == user
    }
    
    return Response(store_data)

@api_view(['GET', 'PUT'])
def inventory_list(request):
    """Get or update inventory items"""
    if request.method == 'GET':
        # Replace with actual model query
        items = [
            {
                'id': 1,
                'name': 'MECHANIX Building Set',
                'price': 1299.00,
                'stock': 25,
                'category': 'Educational',
                'age_group': '7-12 Years',
                'image': 'https://example.com/mechanix.jpg'
            },
            {
                'id': 2,
                'name': 'Building Blocks',
                'price': 899.00,
                'stock': 40,
                'category': 'Creative',
                'age_group': '3-5 Years',
                'image': 'https://example.com/blocks.jpg'
            }
        ]
        return Response(items)
    elif request.method == 'PUT':
        # Update inventory logic would go here
        return Response({"message": "Inventory updated successfully"})

@api_view(['GET', 'POST'])
def staff_details(request):
    """Get or add staff members"""
    if request.method == 'GET':
        # Replace with actual model query
        staff = [
            {
                'id': 1,
                'name': 'John Doe',
                'role': 'Manager',
                'email': 'john@example.com',
                'phone': '9876543210'
            },
            {
                'id': 2,
                'name': 'Jane Smith',
                'role': 'Sales Associate',
                'email': 'jane@example.com',
                'phone': '8765432109'
            }
        ]
        return Response(staff)
    elif request.method == 'POST':
        # Logic to add new staff member
        return Response({"message": "Staff member added successfully"}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def subscription_details(request):
    """Get or update subscription details"""
    if request.method == 'GET':
        # Replace with actual model query
        subscription = {
            'plan': 'Premium',
            'start_date': '2024-01-01',
            'end_date': '2024-04-15',
            'days_remaining': 45,
            'features': ['Unlimited Products', 'Analytics', 'Priority Support']
        }
        return Response(subscription)
    elif request.method == 'POST':
        # Logic to update subscription
        return Response({"message": "Subscription updated successfully"})

@api_view(['GET'])
def trending_products(request):
    """Get trending products"""
    # Use a field that exists in your Product model
    # Based on the error, you have id, title, brand, etc. but no created_at
    products = Product.objects.all().order_by('-id')[:10]  # Using ID as a fallback
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def top_products(request):
    """Get top products"""
    # Get top products (in a real app, you'd sort by sales/popularity)
    products = Product.objects.all().order_by('-id')[:10]
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def filter_products(request):
    """Filter products by gender, age, and category"""
    gender = request.query_params.get('gender')
    age_group = request.query_params.get('age_group')
    product_category = request.query_params.get('category')
    
    # Start with all products
    products = Product.objects.all()
    
    # Apply filters
    if gender:
        products = products.filter(gender=gender)
    if age_group:
        products = products.filter(age_group=age_group)
    if product_category:
        products = products.filter(product_category=product_category)
        
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_detail(request, product_id):
    """Get detailed information about a specific product"""
    try:
        product = Product.objects.get(id=product_id)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(
            {"error": "Product not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_shop_banner(request):
    """Get the banner for the current user's shop"""
    user = request.user
    
    shop = None
    if hasattr(user, 'shops') and user.shops.exists():
        shop = user.shops.first()
    elif hasattr(user, 'helper_at_shops') and user.helper_at_shops.exists():
        shop = user.helper_at_shops.first()
    
    if shop and shop.banner:
        return Response({
            'banner_url': request.build_absolute_uri(shop.banner.url),
            'shop_name': shop.name
        })
    else:
        return Response({
            'banner_url': None,
            'shop_name': shop.name if shop else None
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def redeem_reward(request):
    """Redeem a reward"""
    reward_id = request.data.get('reward_id')
    
    # In a real application, you would check if the user has enough points
    # and update the database accordingly
    
    # Mock response
    return Response({
        'success': True,
        'message': 'Reward redeemed successfully',
        'coupon_code': 'REWARD123',
        'points_deducted': 1000,
        'remaining_points': 1500
    })

# Flicks Feed endpoints
@api_view(['GET'])
def flicks_feed(request):
    """Get content for the Flicks Feed"""
    # Replace with actual model query
    feed_items = [
        {
            'id': 1,
            'type': 'product',
            'title': 'New Arrival',
            'product_id': 1,
            'product_name': 'MECHANIX Ultimate Set',
            'description': 'Check out our latest addition!',
            'image': 'https://example.com/mechanix_ultimate.jpg'
        },
        {
            'id': 2,
            'type': 'promotion',
            'title': 'Summer Sale',
            'description': 'Get up to 50% off on selected toys',
            'image': 'https://example.com/summer_sale.jpg',
            'valid_until': '2024-06-30'
        },
        {
            'id': 3,
            'type': 'video',
            'title': 'Product Demo',
            'description': 'Watch how to build the airplane model',
            'thumbnail': 'https://example.com/video_thumbnail.jpg',
            'video_url': 'https://example.com/videos/demo.mp4'
        }
    ]
    return Response(feed_items)

# Distributor and Brand endpoints
@api_view(['GET'])
def distributors_list(request):
    """Get list of distributors"""
    # Replace with actual model query
    distributors = [
        {
            'id': 1,
            'name': 'Global Toys Distributor',
            'contact_person': 'Rajesh Kumar',
            'email': 'rajesh@globaltoys.com',
            'phone': '9876543210',
            'address': 'Mumbai, Maharashtra'
        },
        {
            'id': 2,
            'name': 'Educational Toys Inc.',
            'contact_person': 'Sunita Sharma',
            'email': 'sunita@edutoys.com',
            'phone': '8765432109',
            'address': 'Delhi, NCR'
        }
    ]
    return Response(distributors)

@api_view(['GET'])
def brands_list(request):
    """Get list of brands"""
    # Replace with actual model query
    brands = [
        {
            'id': 1,
            'name': 'MECHANIX',
            'logo': 'https://example.com/mechanix_logo.jpg',
            'description': 'Leading brand for construction toys',
            'product_count': 25
        },
        {
            'id': 2,
            'name': 'CreativeBlocks',
            'logo': 'https://example.com/creativeblocks_logo.jpg',
            'description': 'Specializing in creative building blocks',
            'product_count': 18
        },
        {
            'id': 3,
            'name': 'SoftBuddies',
            'logo': 'https://example.com/softbuddies_logo.jpg',
            'description': 'Premium soft toys for all ages',
            'product_count': 32
        }
    ]
    return Response(brands)

# User Profile endpoints
@api_view(['GET', 'PUT'])
def user_profile(request):
    """Get or update user profile"""
    if request.method == 'GET':
        # Replace with actual model query
        profile = {
            'username': request.user.username,
            'email': request.user.email,
            'full_name': 'John Doe',  # Would be fetched from user profile model
            'phone': '9876543210',
            'address': '123 Main St, Mumbai',
            'store_name': 'Kids Toys Store',
            'membership_since': '2023-05-15'
        }
        return Response(profile)
    elif request.method == 'PUT':
        # Logic to update user profile
        data = request.data
        # Update logic would go here
        return Response({'message': 'Profile updated successfully'})

# API overview endpoint
@api_view(['GET'])
def api_overview(request):
    """Provide an overview of available API endpoints"""
    api_urls = {
        'Authentication': {
            'Register': '/api/auth/register/',
            'Login': '/api/auth/login/',
        },
        'Store Management': {
            'Store Info': '/api/store/',
            'Inventory': '/api/inventory/',
            'Staff': '/api/staff/',
            'Orders': '/api/orders/',
            'Subscription': '/api/subscription/',
        },
        'Products': {
            'Trending Products': '/api/products/trending/',
            'Top Products': '/api/products/top/',
            'Filter Products': '/api/products/filter/',
            'Product Detail': '/api/products/<id>/',
        },
        'Rewards': {
            'Rewards Summary': '/api/rewards/',
            'Rewards History': '/api/rewards/history/',
            'Redeem Reward': '/api/rewards/redeem/',
        },
        'Flicks Feed': {
            'Feed Items': '/api/feed/',
        },
        'Distributors & Brands': {
            'Distributors': '/api/distributors/',
            'Brands': '/api/brands/',
        },
        'User Profile': {
            'User Profile': '/api/profile/',
        }
    }
    return Response(api_urls)