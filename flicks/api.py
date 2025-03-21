from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status




@api_view(['GET'])
def api_overview(request):
    """Provide an overview of available API endpoints"""
    api_urls = {
        'Overview': '/api/',
        'Products List': '/api/products/',
        'Product Detail': '/api/products/<id>/',
    }
    return Response(api_urls)

