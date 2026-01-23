from functools import wraps
from django.http import JsonResponse
from django_tenants.utils import connection

def feature_required(feature_key):
    """
    Decorator to check if a specific feature is enabled for the current tenant.
    Usage:
        @feature_required('DOC_OCR')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # The tenant is already attached to the request by OrganizationStatusMiddleware
            tenant = getattr(request, 'tenant', None)
            
            if not tenant:
                # Should not happen if middleware is active, but be safe
                return JsonResponse({"error": "Unauthorized: No organization context found"}, status=401)
            
            # Check enabled_features list (or default empty list)
            enabled_features = getattr(tenant, 'enabled_features', []) or []
            
            if feature_key not in enabled_features:
                return JsonResponse({
                    "error": "FEATURE_NOT_ENABLED",
                    "feature": feature_key,
                    "message": f"The '{feature_key}' feature is not enabled for this organization."
                }, status=403)
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
