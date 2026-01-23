from django.core.management.base import BaseCommand
from tenants.models import Client, Domain

class Command(BaseCommand):
    help = "Create a new tenant with a domain"

    def add_arguments(self, parser):
        parser.add_argument('schema_name', type=str, help='Tenant schema name (e.g., tenant1)')
        parser.add_argument('tenant_name', type=str, help='Tenant full name (e.g., Tenant One)')
        parser.add_argument('domain', type=str, help='Domain name for tenant (e.g., tenant1.localhost)')

    def handle(self, *args, **options):
        schema_name = options['schema_name']
        tenant_name = options['tenant_name']
        domain_name = options['domain']

        # Create tenant
        tenant = Client(schema_name=schema_name, name=tenant_name)
        tenant.save()
        self.stdout.write(self.style.SUCCESS(f'Tenant "{tenant_name}" created with schema "{schema_name}"'))

        # Create domain
        domain = Domain(domain=domain_name, tenant=tenant, is_primary=True)
        domain.save()
        self.stdout.write(self.style.SUCCESS(f'Domain "{domain_name}" added for tenant "{tenant_name}"'))
