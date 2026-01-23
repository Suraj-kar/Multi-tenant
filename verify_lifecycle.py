import requests
import os
import django
import sys

# Setup django to read model data
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Client

def test_lifecycle():
    print("--- Starting Lifecycle Verification ---")
    
    # We need a tenant to test with. Let's find or create one.
    # We'll use the 'aa' tenant if it exists, or create a 'test-org'
    tenant = Client.objects.filter(schema_name='aa').first()
    if not tenant:
        print("Tenant 'aa' not found. Please ensure a tenant exists.")
        return

    base_url = "http://localhost:8001"
    headers = {
        "X-ISS-ID": tenant.iss_id,
        "X-API-TOKEN": tenant.api_token,
        "Accept": "application/json"
    }

    scenarios = [
        (Client.STATUS_ACTIVE, "/compare-face/", 200, "Active Org Access"),
        (Client.STATUS_SUSPENDED, "/compare-face/", 403, "Suspended Org Access (Blocked)"),
        (Client.STATUS_ONBOARDING, "/compare-face/", 403, "Onboarding Org Restricted Access (Blocked)"),
        (Client.STATUS_ONBOARDING, "/health-check/", 200, "Onboarding Org Allowed Access (HealthCheck)"),
        (Client.STATUS_TERMINATED, "/compare-face/", 401, "Terminated Org Access (Blocked)"),
    ]

    original_status = tenant.status
    
    try:
        for status, path, expected_code, description in scenarios:
            tenant.status = status
            tenant.save()
            print(f"\nScenario: {description} (Status: {status})")
            
            response = requests.get(f"{base_url}{path}", headers=headers)
            print(f"  URL: {path}")
            print(f"  Expected: {expected_code}, Got: {response.status_code}")
            if response.status_code == expected_code:
                print("  ✅ PASSED")
            else:
                print("  ❌ FAILED")
                print(f"  Response: {response.text}")

    finally:
        # Restore original status
        tenant.status = original_status
        tenant.save()
        print(f"\nRestored tenant status to: {original_status}")

if __name__ == "__main__":
    test_lifecycle()
