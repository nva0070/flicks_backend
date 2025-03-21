from rest_framework import permissions

class IsOwnerOrHelper(permissions.BasePermission):
    """
    Permission to only allow owners or helpers of a shop to access it
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is the shop owner
        if obj.owner == request.user:
            return True
            
        # Check if user is a helper at this shop
        if request.user in obj.helpers.all():
            # For write operations, additional checks might be needed
            if request.method in permissions.SAFE_METHODS:
                return True
            # Implement specific helper permissions for non-safe methods
                
        return False


class IsShopOwner(permissions.BasePermission):
    """
    Permission to only allow shop owners to access
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is the shop owner
        return obj.shop.owner == request.user