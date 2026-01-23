from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from core.views import api_test, compare_face, health_check, document_extract, face_search, logout_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Public Home
    path('', views.tenant_home, name='tenant_home'),
    
    # Login handled by Django's built-in view but using our template
    path('login/', auth_views.LoginView.as_view(template_name='customers/login.html', next_page='tenant_dashboard'), name='login'),
    
    # Protected Dashboard
    path('dashboard/', views.tenant_dashboard, name='tenant_dashboard'),
    
    # API Demo and Test
    path('api-demo/', views.api_demo, name='api_demo'),
    path('api-test/', api_test, name='api_test'),
    path('compare-face/', compare_face, name='compare_face'),
    path('health-check/', health_check, name='health_check'),       
    path('modules/', views.module_list, name='module_list'),
    path('document-extract-information/', document_extract, name='document_extract'),
    path('face-search/', face_search, name='face_search'),
    
    # KYC Logs
    path('customers/create/', views.customer_create, name='customer_create'),
    path('kyc-logs/', views.kyc_log_list, name='kyc_log_list'),
    path('kyc-logs/create/', views.kyc_log_create, name='kyc_log_create'),
    path('kyc-logs/<int:pk>/', views.kyc_log_detail, name='kyc_log_detail'),
    
    # Logout
    path('logout/', logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
