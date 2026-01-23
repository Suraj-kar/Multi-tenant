from django.db import models
from tenants.models import TenantBaseModel

class Customer(TenantBaseModel):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class KYCLog(TenantBaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='logs')
    document_type = models.CharField(max_length=50)
    document_image = models.ImageField(upload_to='kyc/documents/')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"KYC Log for {self.customer.name} - {self.document_type}"
