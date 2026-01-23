import requests
import os
import django
import sys

# Setup django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Client

def test_feature_access():
    print("--- Starting Task 3: Feature Access Verification ---")
    
    # 1. Setup Test Data
    t1 = Client.objects.get(schema_name='aa')
    
    # Configure features for Org A: Enable OCR, Disable FACE_SEARCH
    t1.enabled_features = ['DOC_OCR']
    t1.status = 'ACTIVE'
    t1.save()
    
    print(f"Testing for Organization: {t1.schema_name}")
    print(f"Enabled Features: {t1.enabled_features}")

    base_url = "http://localhost:8001"
    headers = {
        "X-ISS-ID": t1.iss_id,
        "X-API-TOKEN": t1.api_token,
        "Accept": "application/json"
    }

    # Scenario 1: Using an Enabled Feature (DOC_OCR)
    print("\n[Scenario 1] Calling enabled feature: DOC_OCR")
    resp = requests.get(f"{base_url}/document-extract-information/", headers=headers)
    if resp.status_code == 200:
        print(f"  ✅ SUCCESS: Got response: {resp.json().get('message')}")
    else:
        print(f"  ❌ FAILED: Unexpected status {resp.status_code}")
        print(f"  Response: {resp.text}")

    # Scenario 2: Accessing a Disabled Feature (FACE_1_N)
    print("\n[Scenario 2] Calling disabled feature: FACE_1_N")
    resp = requests.get(f"{base_url}/face-search/", headers=headers)
    if resp.status_code == 403:
        data = resp.json()
        if data.get('error') == 'FEATURE_NOT_ENABLED':
             print(f"  ✅ SUCCESS: Got 403 Forbidden with code: {data.get('error')}")
        else:
             print(f"  ❌ FAILED: Got 403 but wrong error code: {data.get('error')}")
    else:
        print(f"  ❌ FAILED: Expected 403 but got {resp.status_code}")
        print(f"  Response: {resp.text}")

if __name__ == "__main__":
    test_feature_access()
