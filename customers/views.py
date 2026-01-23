from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse
from .models import Customer, KYCLog

def tenant_auth_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # 1. Allow if authenticated via session (e.g., Backoffice User)
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        
        # 2. Allow if authenticated via headers (Verified by OrganizationStatusMiddleware)
        # We check for presence of any auth header. Middleware handles the verification.
        has_auth = any(k in request.headers for k in ['X-ISS-ID', 'X-API-TOKEN', 'Authorization'])
        
        if hasattr(request, 'tenant') and request.tenant.schema_name != 'public' and has_auth:
            return view_func(request, *args, **kwargs)
            
        # Otherwise redirect or error
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({"error": "Unauthorized. Please provide valid API credentials."}, status=401)
        return redirect('login')
    return _wrapped_view

@login_required
def tenant_dashboard(request):
    customers = Customer.objects.all() # Automatically filtered by TenantManager
    context = {
        'tenant': connection.tenant,
        'tenant_name': connection.tenant.name,
        'schema_name': connection.schema_name,
        'customers_count': customers.count(),
        'kyc_count': KYCLog.objects.count()
    }
    return render(request, 'customers/dashboard.html', context)

def tenant_home(request):
    return render(request, 'customers/home.html', {
        'tenant_name': connection.tenant.name, 
        'tenant': connection.tenant
    })

@login_required
def api_demo(request):
    return render(request, 'customers/api_demo.html', {
        'tenant': connection.tenant,
        'api_token': connection.tenant.api_token
    })

@tenant_auth_required
def kyc_log_list(request):
    logs = KYCLog.objects.all().order_by('-created_at')
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            "logs": list(logs.values('id', 'customer__name', 'document_type', 'created_at'))
        })
    
    customers = Customer.objects.all()
    return render(request, 'customers/kyc_logs.html', {
        'logs': logs,
        'customers': customers,
        'tenant': connection.tenant
    })

@tenant_auth_required
def kyc_log_create(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        
        doc_type = request.POST.get('document_type')
        notes = request.POST.get('notes', '')
        image = request.FILES.get('document_image')
        
        log = KYCLog.objects.create(
            customer=customer,
            document_type=doc_type,
            notes=notes,
            document_image=image
        )
        
        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({"message": "KYC Log created", "id": log.id, "org_id": str(log.org_id)})
            
        return redirect('kyc_log_list')
        
    return JsonResponse({"error": "POST required"}, status=400)

@tenant_auth_required
def kyc_log_detail(request, pk):
    try:
        log = KYCLog.objects.get(pk=pk)
        
        if request.headers.get('Accept') == 'application/json' or request.path.startswith('/api/'):
            return JsonResponse({
                "id": log.id,
                "customer": log.customer.name,
                "doc_type": log.document_type,
                "org_id": str(log.org_id)
            })
            
        return render(request, 'customers/kyc_log_detail.html', {
            'log': log,
            'tenant': connection.tenant
        })
    except KYCLog.DoesNotExist:
        return JsonResponse({"error": "Not Found"}, status=404)

@tenant_auth_required
def module_list(request):
    return render(request, 'customers/modules.html', {
        'tenant': connection.tenant
    })

@tenant_auth_required
def customer_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Customer.objects.create(name=name)
        return redirect('kyc_log_list')
    return JsonResponse({"error": "POST required"}, status=400)
