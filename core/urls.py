from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.contrib.auth import views as auth_views
from core import views

def public_home(request):
    return HttpResponse("Public Schema Homepage test")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', public_home),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create_tenant/', views.create_tenant, name='create_tenant'),
    path('update_tenant/<int:pk>/', views.update_tenant, name='update_tenant'),
    path('delete_tenant/<int:pk>/', views.delete_tenant, name='delete_tenant'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api-test/', views.api_test, name='api_test'),
    path('compare-face/', views.compare_face, name='compare_face'),
    path('health-check/', views.health_check, name='health_check'),
    path('document-extract-information/', views.document_extract, name='document_extract'),
    path('face-search/', views.face_search, name='face_search'),
]
