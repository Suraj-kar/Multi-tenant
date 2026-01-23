import os
import django
import sys

# Add the project root to the python path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tenants.models import Client, Domain

def create_public_tenant():
    if Client.objects.filter(schema_name='public').exists():
        print("Public tenant already exists.")
    else:
        try:
            tenant = Client(schema_name='public', name='Public Tenant')
            tenant.save()
            
            # modify domain if needed, e.g., to match what the user uses (localhost or 127.0.0.1)
            domain_url = 'localhost' 
            
            domain = Domain()
            domain.domain = domain_url
            domain.tenant = tenant
            domain.is_primary = True
            domain.save()
            print(f"Public tenant created successfully with domain {domain_url}.")
        except Exception as e:
            print(f"Error creating public tenant: {e}")

if __name__ == "__main__":
    create_public_tenant()
