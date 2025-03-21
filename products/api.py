# flicks/api.py
from django.http import JsonResponse
from products.models import Order, Reward, Shop, UserReward, ShopUser
from products.serializers import OrderSerializer, RewardSerializer, ShopUserSerializer
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

# Store Management endpoints
@api_view(['GET'])
def store_info(request):
    """Get store information for the logged-in user"""
    # Replace with actual model data
    store_data = {
        'name': 'Kids Toys Store',
        'logo': 'https://example.com/logo.png',
        'subscription': {
            'plan': 'Premium',
            'days_remaining': 45,
            'start_date': '2024-01-01',
            'end_date': '2024-04-15'
        }
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

@api_view(['GET'])
def orders_list(request):
    """Get orders for the logged-in user's store"""
    # Get the user's shop
    try:
        shop = Shop.objects.get(owner=request.user)
    except Shop.DoesNotExist:
        # Check if user is a helper at any shop
        shops = request.user.helper_at_shops.all()
        if not shops:
            return Response({"error": "No shop found"}, status=status.HTTP_404_NOT_FOUND)
        shop = shops.first()
    
    orders = Order.objects.filter(shop=shop).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)



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

# Product Catalog endpoints
@api_view(['GET'])
def trending_products(request):
    """Get trending products"""
    # Replace with actual model query with sorting by popularity
    products = [
        {
            'id': 1,
            'name': 'MECHANIX Building Set',
            'price': 1299.00,
            'category': 'Educational',
            'age_group': '7-12 Years',
            'image': 'https://example.com/mechanix.jpg',
            'rating': 4.8
        },
        {
            'id': 2,
            'name': 'Building Blocks',
            'price': 899.00,
            'category': 'Creative',
            'age_group': '3-5 Years',
            'image': 'https://example.com/blocks.jpg',
            'rating': 4.6
        }
    ]
    return Response(products)

@api_view(['GET'])
def top_products(request):
    """Get top 10 products by sales"""
    # Replace with actual model query sorted by sales
    products = [
        {
            'id': 1,
            'name': 'MECHANIX Building Set',
            'price': 1299.00,
            'category': 'Educational',
            'age_group': '7-12 Years',
            'image': 'https://example.com/mechanix.jpg',
            'sold': 150
        },
        {
            'id': 2,
            'name': 'Building Blocks',
            'price': 899.00,
            'category': 'Creative',
            'age_group': '3-5 Years',
            'image': 'https://example.com/blocks.jpg',
            'sold': 120
        }
    ]
    return Response(products)

@api_view(['GET'])
def filter_products(request):
    """Filter products by gender, age, and category"""
    gender = request.query_params.get('gender', None)
    age = request.query_params.get('age', None)
    category = request.query_params.get('category', None)
    
    # In a real application, you would filter your database query
    # This is just a mock response
    products = [
        {
            'id': 1,
            'name': 'MECHANIX Building Set',
            'price': 1299.00,
            'category': 'Educational',
            'gender': 'All',
            'age_group': '7-12 Years',
            'image': 'https://example.com/mechanix.jpg'
        },
        {
            'id': 2,
            'name': 'Building Blocks',
            'price': 899.00,
            'category': 'Creative',
            'gender': 'All',
            'age_group': '3-5 Years',
            'image': 'https://example.com/blocks.jpg'
        }
    ]
    
    # Apply filters
    filtered_products = products
    if gender and gender != 'All':
        filtered_products = [p for p in filtered_products if p['gender'] == gender]
    if age:
        filtered_products = [p for p in filtered_products if p['age_group'] == age]
    if category:
        filtered_products = [p for p in filtered_products if p['category'] == category]
        
    return Response(filtered_products)

@api_view(['GET'])
def product_detail(request, product_id):
    """Get detailed information about a specific product"""
    # Replace with actual model query
    product = {
        'id': product_id,
        'name': 'MECHANIX Building Set',
        'price': 1299.00,
        'description': 'A detailed construction set that helps children develop fine motor skills and spatial reasoning. Includes 250+ pieces to build various models.',
        'category': 'Educational',
        'age_group': '7-12 Years',
        'gender': 'All',
        'brand': 'MECHANIX',
        'in_stock': True,
        'stock_count': 25,
        'rating': 4.8,
        'reviews': [
            {'user': 'Rahul S.', 'rating': 5, 'comment': 'My son loves it!'},
            {'user': 'Priya M.', 'rating': 4, 'comment': 'Great quality, but missing instructions'}
        ],
        'images': [
            'https://example.com/mechanix1.jpg',
            'https://example.com/mechanix2.jpg'
        ]
    }
    return Response(product)

@api_view(['GET'])
def rewards_summary(request):
    """Get rewards summary for the logged-in user"""
    user = request.user
    
    # Calculate points
    earned_points = UserReward.objects.filter(user=user, type=UserReward.EARN).aggregate(
        total=sum('points')
    )['total'] or 0
    
    used_points = UserReward.objects.filter(user=user, type=UserReward.REDEEM).aggregate(
        total=sum('points')
    )['total'] or 0
    
    available_points = earned_points + used_points  # used_points will be negative
    
    # Get available rewards
    rewards = Reward.objects.filter(is_active=True)
    
    data = {
        'available_points': available_points,
        'points_earned': earned_points,
        'points_used': abs(used_points),
        'available_rewards': RewardSerializer(rewards, many=True).data
    }
    
    return Response(data)

@api_view(['GET'])
def rewards_history(request):
    """Get rewards transaction history for the logged-in user"""
    # Replace with actual model query
    history = [
        {
            'id': 1,
            'type': 'REDEEM',
            'description': '₹500 Off Coupon',
            'points': -2000,
            'date': '2024-02-15'
        },
        {
            'id': 2,
            'type': 'EARN',
            'description': 'Order #12345',
            'points': 500,
            'date': '2024-02-10'
        },
        {
            'id': 3,
            'type': 'REDEEM',
            'description': 'Free Delivery Coupon',
            'points': -1000,
            'date': '2024-02-05'
        }
    ]
    return Response(history)

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