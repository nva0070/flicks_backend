from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Product, ViewSession, FlicksAnalytics
from django.db.models import Sum, Avg, Count
import uuid

@api_view(['POST'])
@permission_classes([AllowAny])
def start_view_session(request):
    """Start tracking when a flick becomes visible in the viewport"""
    product_id = request.data.get('product_id')
    
    if not product_id:
        return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if product has a flick
    if not product.flicks:
        return Response({"error": "This product has no video"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Create new session
    session = ViewSession.objects.create(
        product=product,
        user=request.user if request.user.is_authenticated else None,
        session_id=session_id,
        ip_address=get_client_ip(request),
        device_info=get_device_info(request),
    )
    
    # Do not increment view count yet - we'll do that on end_view_session
    # when we know if they actually watched a meaningful amount
    
    return Response({
        "session_id": session.session_id,
        "start_time": session.start_time,
        "product_duration": product.video_duration or 30  # Fallback to 30 seconds if duration unknown
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def end_view_session(request):
    """End tracking when flick is scrolled away from viewport or finishes"""
    session_id = request.data.get('session_id')
    watch_duration = request.data.get('duration', 0)  # Duration in seconds
    percent_watched = request.data.get('percent_watched', 0)  # Percentage watched (0-100)
    
    if not session_id:
        return Response({"error": "Session ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        session = ViewSession.objects.get(session_id=session_id, end_time=None)
    except ViewSession.DoesNotExist:
        return Response({"error": "Active session not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Record end time
    session.end_time = timezone.now()
    session.duration = watch_duration
    
    # Consider it completed if watched over 80%
    session.completed = percent_watched >= 80
    session.save()
    
    # Only count as a view if watched at least 3 seconds or 25% of the video
    product_duration = getattr(session.product, 'video_duration', 30) or 30
    min_view_duration = min(3, product_duration * 0.25)
    
    if watch_duration >= min_view_duration:
        # Update analytics - count as a view
        analytics, created = FlicksAnalytics.objects.get_or_create(product=session.product)
        analytics.views += 1
        analytics.total_watch_time += watch_duration
        analytics.save()
    
    return Response({
        "status": "success",
        "duration": watch_duration,
        "completed": session.completed
    })

# Helper functions
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_device_info(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    return {
        'user_agent': user_agent
    }

def get_completion_rate(product):
    """Calculate percentage of views that were completed"""
    sessions = ViewSession.objects.filter(product=product)
    total_sessions = sessions.count()
    
    if total_sessions == 0:
        return 0
    
    completed_sessions = sessions.filter(completed=True).count()
    return round((completed_sessions / total_sessions) * 100, 2)

def format_time(seconds):
    """Format seconds into human-readable time"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"