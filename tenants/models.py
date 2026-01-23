from django_tenants.models import TenantMixin, DomainMixin
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django_tenants.utils import connection

class TenantManager(models.Manager):
    def get_queryset(self):
        # Automatically filter for the current tenant's org_id
        # This provides Scenario 2 logical isolation
        tenant = getattr(connection, 'tenant', None)
        if tenant and tenant.schema_name != 'public' and hasattr(tenant, 'org_id'):
            return super().get_queryset().filter(org_id=tenant.org_id)
        return super().get_queryset()

class TenantBaseModel(models.Model):
    org_id = models.UUIDField(editable=False, db_index=True, null=True, blank=True)
    
    objects = TenantManager()
    
    class Meta:
        abstract = True

    def save(self, *args, **kwargs): 
        if not self.org_id:
            tenant = getattr(connection, 'tenant', None)
            if tenant and tenant.schema_name != 'public':
                self.org_id = tenant.org_id
        super().save(*args, **kwargs)

class Client(TenantMixin):
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_SUSPENDED = 'SUSPENDED'
    STATUS_ONBOARDING = 'ONBOARDING'
    STATUS_TERMINATED = 'TERMINATED'

    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_SUSPENDED, 'Suspended'),
        (STATUS_ONBOARDING, 'Onboarding'),
        (STATUS_TERMINATED, 'Terminated'),
    )

    org_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    legal_name = models.CharField(max_length=255)
    iss_id = models.CharField(max_length=50, unique=True)
    api_token = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ONBOARDING)
    enabled_features = models.JSONField(default=list, blank=True)
    
    name = models.CharField(max_length=100)
    paid_until = models.DateField(null=True, blank=True)
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)

    auto_create_schema = True
    auto_drop_schema = True

    def save(self, *args, **kwargs):
        if not self.iss_id:
             # Simple auto-generation for iss_id if not provided, using schema_name as base
             self.iss_id = f"iss-{self.schema_name}-{uuid.uuid4().hex[:8]}"
        if not self.api_token:
             self.api_token = uuid.uuid4().hex
        super().save(*args, **kwargs)
    auto_drop_schema = True

class Domain(DomainMixin):
    pass

