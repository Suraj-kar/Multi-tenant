import os
import django
import sys
from django.db import connection

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def create_public_schema():
    with connection.cursor() as cursor:
        try:
            print("Attempting to create public schema...")
            cursor.execute("CREATE SCHEMA IF NOT EXISTS public;")
            print("Schema 'public' ensured.")
        except Exception as e:
            print(f"Error creating schema: {e}")

if __name__ == "__main__":
    create_public_schema()
