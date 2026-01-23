from django.http import JsonResponse, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from tenants.models import Client
from django_tenants.utils import connection, get_tenant_model, get_public_schema_name
from django.db import connection as db_connection

class OrganizationStatusMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 1. IDENTIFY: Try to identify tenant via multiple header formats
        iss_id = request.headers.get('X-ISS-ID') or request.headers.get('HTTP_X_ISS_ID')
        api_token = request.headers.get('X-API-TOKEN') or request.headers.get('HTTP_X_API_TOKEN')
        
        # Handle "Authorization: Bearer <token>"
        auth_header = request.headers.get("Authorization")
        bearer_token = None
        if auth_header and auth_header.startswith("Bearer "):
            bearer_token = auth_header.split(" ")[1]
            
        token_to_verify = api_token or bearer_token

        # 2. ENFORCE: If credentials provided, they must match the subdomain context
        current_tenant = getattr(request, 'tenant', None)
        public_schema = get_public_schema_name()

        if (iss_id and api_token) or bearer_token:
            try:
                # Lookup source tenant from credentials
                if iss_id and api_token:
                    header_tenant = Client.objects.get(iss_id=iss_id, api_token=api_token)
                else:
                    header_tenant = Client.objects.get(api_token=bearer_token)
                
                # STRICT SCOPING: If on a subdomain (e.g., kk.localhost), token MUST match kk
                if current_tenant and current_tenant.schema_name != public_schema:
                    if header_tenant != current_tenant:
                        return JsonResponse({
                            "error": "Cross-tenant access prohibited.",
                            "details": f"Token for '{header_tenant.name}' cannot be used on domain '{request.get_host()}'."
                        }, status=403)
                else:
                    # On public domain (localhost), headers define the tenant context
                    request.tenant = header_tenant
                    db_connection.set_tenant(request.tenant)
                    from django.conf import settings
                    request.urlconf = settings.ROOT_URLCONF
            except Client.DoesNotExist:
                return JsonResponse({"error": "Invalid API credentials."}, status=401)

        # Skip if no tenant is set (public schema or error)
        if not hasattr(request, 'tenant') or not request.tenant:
            return None
        
        # Public tenant usually has full access (SaaS Admin)
        if request.tenant.schema_name == get_public_schema_name():
            return None

        status = request.tenant.status
        path = request.path

        from django.shortcuts import render

        # 1. TERMINATED: Hard-lock. All incoming requests return 401 Unauthorized.
        if status == Client.STATUS_TERMINATED:
            if request.headers.get('Accept') == 'application/json' or path.startswith('/api/'):
                return JsonResponse({"error": "Account Terminated. Access is no longer available."}, status=401)
            return render(request, 'core/lifecycle_error.html', {
                'title': 'Account Terminated',
                'heading': 'Account Terminated',
                'message': 'This organization account has been permanently terminated. Access is no longer available.',
                'icon': '🚫',
                'state_class': 'terminated'
            }, status=401)

        # 2. SUSPENDED: Block all API and Backoffice access. Return 403 Forbidden.
        if status == Client.STATUS_SUSPENDED:
            if request.headers.get('Accept') == 'application/json' or path.startswith('/api/'):
                return JsonResponse({"error": "Account Suspended. Please contact support."}, status=403)
            return render(request, 'core/lifecycle_error.html', {
                'title': 'Account Suspended',
                'heading': 'Account Suspended',
                'message': 'This organization account has been suspended. Please contact support for assistance.',
                'icon': '⚠️',
                'state_class': 'suspended'
            }, status=403)

        # 3. ONBOARDING: Restricted state. Only HealthCheck and specific setup APIs allowed.
        if status == Client.STATUS_ONBOARDING:
            # Allow specific endpoints
            allowed_paths = ['/health-check/', '/setup/', '/api/health-check/']
            is_allowed = any(path.startswith(p) for p in allowed_paths)
            
            if not is_allowed:
                 if request.headers.get('Accept') == 'application/json' or path.startswith('/api/'):
                     return JsonResponse({"error": "Organization is in ONBOARDING state. Restricted access."}, status=403)
                 return render(request, 'core/lifecycle_error.html', {
                    'title': 'Setup Required',
                    'heading': 'Complete Setup',
                    'message': 'This organization is currently in onboarding mode. Please complete the setup process to gain full access.',
                    'icon': '🚀',
                    'state_class': 'onboarding',
                    'action_text': 'Start Setup',
                    'action_url': '/setup/'  # Placeholder
                 }, status=403)

        # 4. ACTIVE: Full access to APIs and Backoffice.
        return None
