import os
import django
import sys

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection
from tenants.models import Client

try:
    public_tenant = Client.objects.get(schema_name='public')
    connection.set_tenant(public_tenant)
    
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("Superuser 'admin' created with password 'admin'.")
    else:
        print("Superuser 'admin' already exists.")
except Exception as e:
    print(f"Error: {e}")
