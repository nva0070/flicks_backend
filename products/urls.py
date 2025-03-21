from django.urls import path
from . import api

urlpatterns = [

    path('auth/register/', api.register_user, name='register'),
    path('auth/login/', api.login_user, name='login'),
    
    path('store/', api.store_info, name='store-info'),
    path('inventory/', api.inventory_list, name='inventory'),
    path('staff/', api.staff_details, name='staff'),
    path('orders/', api.orders_list, name='orders'),
    path('subscription/', api.subscription_details, name='subscription'),
    

    path('products/trending/', api.trending_products, name='trending-products'),
    path('products/top/', api.top_products, name='top-products'),
    path('products/filter/', api.filter_products, name='filter-products'),
    path('products/<int:product_id>/', api.product_detail, name='product-detail'),
    

    path('rewards/', api.rewards_summary, name='rewards-summary'),
    path('rewards/history/', api.rewards_history, name='rewards-history'),
    path('rewards/redeem/', api.redeem_reward, name='redeem-reward'),
    

    path('feed/', api.flicks_feed, name='flicks-feed'),
    path('distributors/', api.distributors_list, name='distributors'),
    path('brands/', api.brands_list, name='brands'),
    path('profile/', api.user_profile, name='user-profile'),
    

    path('', api.api_overview, name='api-overview'),
]