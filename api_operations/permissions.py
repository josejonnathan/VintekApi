from rest_framework import permissions

class IsOrderOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an order to view it
    """

    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner of the order
        return obj.user == request.user
    

class IsUserProfileOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a UserProfile to view or modify it
    """

    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner of the UserProfile
        return obj.user == request.user
    
    
class IsShoppingCartOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a ShoppingCart to view or modify it
    """

    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner of the ShoppingCart
        return obj.user == request.user
    

from rest_framework import permissions

class IsProductOwnerOrReadOnly(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the Product.
        return obj.user == request.user
    


class IsCustomUserOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a CustomUser to view or modify it.
    """

    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner of the CustomUser.
        return obj == request.user