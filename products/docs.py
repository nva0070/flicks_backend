from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.urls import reverse

@api_view(['GET'])
@permission_classes([AllowAny])
def api_documentation(request):
    """
    Comprehensive API documentation for all active endpoints
    """
    base_url = request.build_absolute_uri('/api')
    
    # Authentication endpoints
    auth_endpoints = {
        'Login': {
            'url': f"{base_url}/auth/login/",
            'method': 'POST',
            'description': 'Authenticate user and get JWT tokens',
            'parameters': {
                'username': 'Username',
                'password': 'Password'
            },
            'response': {
                'refresh': 'JWT refresh token',
                'access': 'JWT access token',
                'username': 'Username of authenticated user',
                'role': 'Role (owner or helper)'
            }
        },
        'Register Shop with Owner': {
            'url': f"{base_url}/auth/register/shop/",
            'method': 'POST',
            'description': 'Register a new shop along with owner account',
            'parameters': {
                'shop_name': 'Name of the shop',
                'shop_address': 'Physical address of the shop',
                'shop_phone': 'Contact phone number for the shop',
                'shop_email': 'Contact email for the shop',
                'shop_description': 'Optional description of the shop',
                'owner_username': 'Username for shop owner account',
                'owner_email': 'Email for shop owner account',
                'owner_password': 'Password for shop owner account',
                'owner_first_name': 'First name of shop owner',
                'owner_last_name': 'Last name of shop owner',
                'banner': 'Optional shop banner image (file upload)'
            },
            'response': {
                'message': 'Success message',
                'shop': 'Shop details',
                'owner': 'Owner account details',
                'tokens': 'JWT tokens for authentication'
            }
        },
        'Register Shop Helper': {
            'url': f"{base_url}/auth/register/helper/",
            'method': 'POST',
            'description': 'Register as a helper for an existing shop',
            'parameters': {
                'username': 'Username for helper account',
                'email': 'Email for helper account',
                'password': 'Password for helper account',
                'first_name': 'First name of helper',
                'last_name': 'Last name of helper',
                'shop_id': 'ID of the shop to associate with',
                'invitation_code': 'Invitation code from shop owner'
            },
            'response': {
                'message': 'Success message',
                'user': 'Helper account details',
                'shop': 'Associated shop details',
                'tokens': 'JWT tokens for authentication'
            }
        }
    }
    
    # Store management endpoints
    store_endpoints = {
        'Store Info': {
            'url': f"{base_url}/store/",
            'method': 'GET',
            'description': 'Get information about the current user\'s store',
            'authentication': 'Required',
            'response': {
                'id': 'Shop ID',
                'name': 'Shop name',
                'description': 'Shop description',
                'address': 'Physical address',
                'phone': 'Contact phone',
                'email': 'Contact email',
                'banner_url': 'URL to shop banner image',
                'owner': 'Shop owner details',
                'subscription': 'Subscription details if active',
                'is_owner': 'Whether current user is the shop owner'
            }
        },
        'Shop Banner': {
            'url': f"{base_url}/store/banner/",
            'method': 'GET',
            'description': 'Get the banner for the current user\'s shop',
            'authentication': 'Required',
            'response': {
                'banner_url': 'URL to shop banner image',
                'shop_name': 'Name of the shop'
            }
        },
        'Inventory': {
            'url': f"{base_url}/inventory/",
            'method': 'GET',
            'description': 'Get inventory list',
            'authentication': 'Required',
            'response': 'List of inventory items'
        },
        'Staff': {
            'url': f"{base_url}/staff/",
            'method': 'GET',
            'description': 'Get staff details',
            'authentication': 'Required',
            'response': 'List of staff members'
        },
        'Subscription': {
            'url': f"{base_url}/subscription/",
            'method': 'GET',
            'description': 'Get subscription details',
            'authentication': 'Required',
            'response': 'Subscription details'
        }
    }
    
    # Product endpoints
    product_endpoints = {
        'All Products': {
            'url': f"{base_url}/products/",
            'method': 'GET',
            'description': 'Get all products with pagination',
            'parameters': {
                'page': 'Page number (default: 1)',
                'page_size': 'Number of results per page (default: 10)'
            },
            'response': {
                'results': 'List of products',
                'count': 'Total number of products',
                'total_pages': 'Total number of pages',
                'current_page': 'Current page number'
            }
        },
        'Product Detail': {
            'url': f"{base_url}/products/{{product_id}}/",
            'method': 'GET',
            'description': 'Get detailed information about a specific product',
            'parameters': {
                'product_id': 'ID of the product (in URL path)'
            },
            'response': 'Detailed product information including gallery items'
        },
        'Trending Products': {
            'url': f"{base_url}/products/trending/",
            'method': 'GET',
            'description': 'Get list of trending products',
            'response': 'List of trending products'
        },
        'Top Products': {
            'url': f"{base_url}/products/top/",
            'method': 'GET',
            'description': 'Get list of top products',
            'response': 'List of top products'
        },
        'Search Products': {
            'url': f"{base_url}/products/search/",
            'method': 'GET',
            'description': 'Search products by keywords',
            'parameters': {
                'q': 'Search query (min 2 characters)',
                'page': 'Page number (default: 1)',
                'page_size': 'Number of results per page (default: 10)'
            },
            'response': {
                'results': 'List of products matching search',
                'count': 'Total number of matching products',
                'has_more': 'Whether there are more pages',
                'page': 'Current page number',
                'page_size': 'Current page size',
                'query': 'Search query used'
            }
        },
        'Filter Products': {
            'url': f"{base_url}/products/filter/",
            'method': 'GET',
            'description': 'Filter products by gender, age, and category',
            'parameters': {
                'gender': 'Filter by gender (M, F, U)',
                'age_group': 'Filter by age group',
                'category': 'Filter by product category'
            },
            'response': 'List of filtered products'
        },
        'Product Categories': {
            'url': f"{base_url}/products/categories/",
            'method': 'GET',
            'description': 'Get the top 6 most common product categories',
            'response': 'List of category names'
        }
    }
    
    # Additional endpoints
    other_endpoints = {
        'Flicks Feed': {
            'url': f"{base_url}/feed/",
            'method': 'GET',
            'description': 'Get content for the Flicks Feed',
            'response': 'List of feed items'
        },
        'Distributors': {
            'url': f"{base_url}/distributors/",
            'method': 'GET',
            'description': 'Get list of distributors',
            'response': 'List of distributors'
        },
        'Brands': {
            'url': f"{base_url}/brands/",
            'method': 'GET',
            'description': 'Get list of brands',
            'response': 'List of brands'
        },
        'User Profile': {
            'url': f"{base_url}/profile/",
            'method': 'GET',
            'description': 'Get current user profile information',
            'authentication': 'Required',
            'response': 'User profile data'
        },
        'Update Profile': {
            'url': f"{base_url}/profile/",
            'method': 'PUT',
            'description': 'Update user profile',
            'authentication': 'Required',
            'parameters': {
                'first_name': 'User\'s first name',
                'last_name': 'User\'s last name',
                'email': 'User\'s email',
                'store_name': 'Store name (for owners)',
                'store_address': 'Store address (for owners)',
                'store_phone': 'Store phone (for owners)',
                'store_email': 'Store email (for owners)'
            },
            'response': {
                'message': 'Success message'
            }
        }
    }
    
    # Analytics endpoints
    analytics_endpoints = {
        'Start View Session': {
            'url': f"{base_url}/analytics/start-view/",
            'method': 'POST',
            'description': 'Start tracking when a product video becomes visible',
            'parameters': {
                'product_id': 'ID of the product being viewed'
            },
            'response': {
                'session_id': 'Unique session identifier',
                'start_time': 'Timestamp when view started',
                'product_duration': 'Duration of the product video in seconds'
            }
        },
        'End View Session': {
            'url': f"{base_url}/analytics/end-view/",
            'method': 'POST',
            'description': 'End tracking when product video is no longer visible',
            'parameters': {
                'session_id': 'Session ID from start-view',
                'duration': 'How long the video was watched (seconds)',
                'percent_watched': 'Percentage of video watched (0-100)'
            },
            'response': {
                'status': 'Success status',
                'duration': 'Recorded watch duration',
                'completed': 'Whether the view is considered complete'
            }
        }
    }
    
    # Combine all documentation
    full_docs = {
        'Authentication': auth_endpoints,
        'Store Management': store_endpoints,
        'Products': product_endpoints,
        'Analytics': analytics_endpoints,
        'Other': other_endpoints,
        'API Overview': {
            'url': f"{base_url}/",
            'method': 'GET',
            'description': 'Get overview of available endpoints',
            'response': 'List of endpoint categories and their paths'
        }
    }
    
    return Response(full_docs)
