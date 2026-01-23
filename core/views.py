from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponseForbidden
from tenants.models import Client, Domain

@login_required
def dashboard(request):
    tenants = Client.objects.all()
    return render(request, 'core/dashboard.html', {'tenants': tenants})

@login_required
def create_tenant(request):
    if request.method == 'POST':
        schema_name = request.POST['schema_name']
        name = request.POST['name']
        domain = request.POST['domain']
        email = request.POST['email']
        password = request.POST['password']
        status = request.POST['status']
        features = request.POST.getlist('features')
        
        client = Client(schema_name=schema_name, name=name, status=status, enabled_features=features)
        client.save()
        Domain.objects.create(domain=domain, tenant=client, is_primary=True)
        
        from django.contrib.auth.models import User
        from django_tenants.utils import schema_context
        with schema_context(schema_name):
            User.objects.create_superuser(username=email, email=email, password=password)
        
        return redirect('dashboard')
    return render(request, 'core/create_tenant.html')

@login_required
def update_tenant(request, pk):
    client = get_object_or_404(Client, pk=pk)
    domain_obj = client.domains.filter(is_primary=True).first()
    if request.method == 'POST':
        client.name = request.POST['name']
        client.legal_name = request.POST['legal_name']
        client.iss_id = request.POST['iss_id']
        client.api_token = request.POST['api_token']
        client.status = request.POST['status']
        paid_until = request.POST['paid_until']
        client.paid_until = paid_until if paid_until else None
        client.on_trial = 'on_trial_bool' in request.POST
        client.enabled_features = request.POST.getlist('features')
        client.save()
        
        new_domain = request.POST['domain']
        if domain_obj and domain_obj.domain != new_domain:
            domain_obj.domain = new_domain
            domain_obj.save()
        elif not domain_obj:
            Domain.objects.create(domain=new_domain, tenant=client, is_primary=True)
        return redirect('dashboard')
    return render(request, 'core/update_tenant.html', {'client': client, 'domain': domain_obj.domain if domain_obj else ''})

@login_required
def delete_tenant(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if client.schema_name == 'public':
        return HttpResponseForbidden("You cannot delete the public tenant!")
    if request.method == 'POST':
        client.delete()
        return redirect('dashboard')
    return render(request, 'core/delete_tenant_confirm.html', {'client': client})

def api_test(request):
    # The tenant is already identified and verified by OrganizationStatusMiddleware
    if not hasattr(request, 'tenant') or not request.tenant or request.tenant.schema_name == 'public':
        return JsonResponse({"error": "No API credentials provided or identified."}, status=401)
    
    # Return organization details for the verified tenant
    return JsonResponse({
        "message": "Success! You are authenticated and scoped correctly.",
        "organization_id": request.tenant.id,
        "organization_name": request.tenant.name,
        "legal_name": request.tenant.legal_name,
        "status": request.tenant.status,
        "schema": request.tenant.schema_name,
        "domain": request.get_host()
    })

def compare_face(request):
    return JsonResponse({
        "message": "Face comparison successful.",
        "organization": request.tenant.name if hasattr(request, 'tenant') else "Unknown",
        "status": "PROCESSED"
    })

from core.decorators import feature_required

def health_check(request):
    return JsonResponse({
        "status": "UP",
        "organization": request.tenant.name if hasattr(request, 'tenant') else "Unknown"
    })

@feature_required('DOC_OCR')
def document_extract(request):
    return JsonResponse({
        "message": "DOC_OCR feature is active. Extracting information...",
        "extracted_data": {"document_number": "ABC-12345", "name": "JOHN DOE", "expiry": "2030-01-01"}
    })

@feature_required('FACE_1_N')
def face_search(request):
    return JsonResponse({
        "message": "FACE_1_N feature is active. Searching for match...",
        "matches": [{"id": "user_99", "score": 0.98}]
    })

def logout_view(request):
    """
    Custom logout view to ensure session invalidation and cleanup.
    """
    logout(request)
    return redirect('login')
