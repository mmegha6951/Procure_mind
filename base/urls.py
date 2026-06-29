# base/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Organization URLs
    path('organizations/', views.organization_list, name='organization_list'),
    path('organizations/<uuid:pk>/', views.organization_detail, name='organization_detail'),
    path('organizations/create/', views.organization_create, name='organization_create'),
    path('organizations/<uuid:pk>/update/', views.organization_update, name='organization_update'),
    path('organizations/<uuid:pk>/delete/', views.organization_delete, name='organization_delete'),
    
    # Vendor URLs
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/<uuid:pk>/', views.vendor_detail, name='vendor_detail'),
    path('vendors/create/', views.vendor_create, name='vendor_create'),
    path('vendors/<uuid:pk>/update/', views.vendor_update, name='vendor_update'),
    path('vendors/<uuid:pk>/delete/', views.vendor_delete, name='vendor_delete'),
    
    # Policy URLs
    path('policies/', views.policy_list, name='policy_list'),
    path('policies/create/', views.policy_create, name='policy_create'),
    path('policies/<uuid:pk>/update/', views.policy_update, name='policy_update'),
    path('policies/<uuid:pk>/delete/', views.policy_delete, name='policy_delete'),
    
    # Procurement Request URLs
    path('requests/', views.procurementrequest_list, name='procurementrequest_list'),
    path('requests/<uuid:pk>/', views.procurementrequest_detail, name='procurementrequest_detail'),
    path('requests/create/', views.procurementrequest_create, name='procurementrequest_create'),
    path('requests/<uuid:pk>/update/', views.procurementrequest_update, name='procurementrequest_update'),
    path('requests/<uuid:pk>/delete/', views.procurementrequest_delete, name='procurementrequest_delete'),
    
    # Human Review
    path('reviews/update/', views.human_review_update, name='human_review_update'),
    
    # Comments
    path('comments/add/<uuid:request_id>/', views.comment_create, name='comment_create'),
    
    # Certifications
    path('certifications/', views.certification_list, name='certification_list'),
    path('certifications/create/', views.certification_create, name='certification_create'),
    path('certifications/<uuid:pk>/update/', views.certification_update, name='certification_update'),
    path('certifications/<uuid:pk>/delete/', views.certification_delete, name='certification_delete'),
    
    # Tags
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/create/', views.tag_create, name='tag_create'),
    path('tags/<uuid:pk>/update/', views.tag_update, name='tag_update'),
    path('tags/<uuid:pk>/delete/', views.tag_delete, name='tag_delete'),
    
    # User Profile
    path('profile/', views.userprofile_update, name='userprofile_update'),
    
    # API Integrations
    path('api-integrations/', views.apiintegration_list, name='apiintegration_list'),
    path('api-integrations/create/', views.apiintegration_create, name='apiintegration_create'),
    path('api-integrations/<uuid:pk>/update/', views.apiintegration_update, name='apiintegration_update'),
    path('api-integrations/<uuid:pk>/delete/', views.apiintegration_delete, name='apiintegration_delete'),
    
    # API Endpoints
    path('api/organizations/', views.api_organization_list_create, name='api_organization_list_create'),
    path('api/organizations/<uuid:pk>/', views.api_organization_detail, name='api_organization_detail'),
    path('api/vendors/', views.api_vendor_list_create, name='api_vendor_list_create'),
    path('api/vendors/<uuid:pk>/', views.api_vendor_detail, name='api_vendor_detail'),
    path('api/procurement-requests/', views.api_procurement_list_create, name='api_procurement_list_create'),
    path('api/procurement-requests/<uuid:pk>/', views.api_procurement_detail, name='api_procurement_detail'),
    path('api/procurement-requests/<uuid:pk>/submit/', views.api_procurement_submit, name='api_procurement_submit'),
    path('api/comments/<uuid:request_id>/', views.api_comment_list_create, name='api_comment_list_create'),
    path('api/certifications/', views.api_certification_list, name='api_certification_list'),
    path('api/tags/', views.api_tag_list, name='api_tag_list'),
    path('api/policies/', views.api_policy_list, name='api_policy_list'),
    path('api/notifications/<uuid:pk>/mark-read/', views.api_notification_mark_read, name='api_notification_mark_read'),
]