import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Client

def fix_duplicates():
    print("Fetching all clients...")
    clients = Client.objects.all()
    for client in clients:
        print(f"Updating client: {client.schema_name}")
        client.org_id = uuid.uuid4()
        # Also ensure api_token and iss_id are unique/present if they are being made unique
        if not client.api_token:
            client.api_token = uuid.uuid4().hex
        if not client.iss_id:
            client.iss_id = f"iss-{client.schema_name}-{uuid.uuid4().hex[:8]}"
        client.save()
        print(f"  New org_id: {client.org_id}")
        print(f"  New iss_id: {client.iss_id}")
        print(f"  New api_token: {client.api_token}")

if __name__ == "__main__":
    fix_duplicates()
