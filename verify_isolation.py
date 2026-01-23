import requests
import os
import django
import sys
import json

# Setup django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Client
from customers.models import Customer, KYCLog
from django_tenants.utils import tenant_context

def test_kyc_record_leakage():
    print("--- Starting Task 2: Data Isolation Verification ---")
    
    # 1. Setup Test Data for two tenants
    t1 = Client.objects.get(schema_name='aa')
    t2 = Client.objects.get(schema_name='prixa')
    
    # Ensure they are ACTIVE for testing
    t1.status = Client.STATUS_ACTIVE
    t1.save()
    t2.status = Client.STATUS_ACTIVE
    t2.save()
    
    print(f"Tenant 1 (Bank A): {t1.schema_name} (OrgID: {t1.org_id}, Status: {t1.status})")
    print(f"Tenant 2 (Bank B): {t2.schema_name} (OrgID: {t2.org_id}, Status: {t2.status})")

    # Access base URL (assuming dev server is running on 8001)
    base_url = "http://localhost:8001"
    
    # Credentials for T1
    headers1 = {
        "X-ISS-ID": t1.iss_id,
        "X-API-TOKEN": t1.api_token,
        "Accept": "application/json"
    }

    # Credentials for T2
    headers2 = {
        "X-ISS-ID": t2.iss_id,
        "X-API-TOKEN": t2.api_token,
        "Accept": "application/json"
    }

    # Step 1: Create a Customer and KYCLog in T1
    print("\n[Step 1] Creating data in Bank A (Tenant 1)")
    with tenant_context(t1):
        # We need to ensure we have a customer to link the log to
        c1, _ = Customer.objects.get_or_create(name="Customer of Bank A")
        log1 = KYCLog.objects.create(customer=c1, document_type="Passport", notes="Bank A private data")
        log1_id = log1.id
        print(f"  Created KYCLog ID: {log1_id} in Bank A")

    # Step 2: Attempt to access T1's Log from Bank A's context (Success)
    print("\n[Step 2] Accessing Bank A data using Bank A credentials")
    resp = requests.get(f"{base_url}/kyc-logs/{log1_id}/", headers=headers1)
    if resp.status_code == 200:
        print(f"  ✅ SUCCESS: Got data: {resp.json().get('doc_type')}")
    else:
        print(f"  ❌ FAILED: Status {resp.status_code}")

    # Step 3: Attempt to access T1's Log from Bank B's context (STRICT ISOLATION)
    # Scenario 1 & 2: Should return 404 because TenantManager filters by org_id
    print("\n[Step 3] Accessing Bank A data using Bank B credentials (STRICT ISOLATION)")
    resp = requests.get(f"{base_url}/kyc-logs/{log1_id}/", headers=headers2)
    if resp.status_code == 404:
        print("  ✅ SUCCESS: Got 404 Not Found. Bank B cannot see Bank A's data.")
    else:
        print(f"  ❌ FAILED: Bank B accessed Bank A's data! Status {resp.status_code}")
        print(f"  Response: {resp.text}")

    # Step 4: Verify Media Path Separation (Scenario 3)
    print("\n[Step 4] Verifying Media Path Separation")
    # This usually requires a file upload, but we can check if TenantFileSystemStorage is active
    from core import settings
    if settings.DEFAULT_FILE_STORAGE == 'django_tenants.storage.TenantFileSystemStorage':
        print("  ✅ SUCCESS: TenantFileSystemStorage is configured.")
    else:
        print("  ❌ FAILED: TenantFileSystemStorage is NOT configured.")

if __name__ == "__main__":
    test_kyc_record_leakage()
