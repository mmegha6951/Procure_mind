# base/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import (
    Organization, OrganizationMembership, UserProfile, Certification, Tag,
    Vendor, CompliancePolicy, ProcurementRequest, ProcurementAttachment,
    VendorSourceDocument, VendorAuditResult, ComplianceViolation, HumanReview,
    WorkflowCheckpoint, AgentRun, PerformanceMetric, APIIntegration,
    RequestComment, Notification, AuditLog
)
from .forms import (
    OrganizationForm, UserProfileForm, CertificationForm, TagForm, 
    VendorForm, CompliancePolicyForm, ProcurementRequestForm,
    HumanReviewForm, RequestCommentForm, APIIntegrationForm
)
from .serializers import (
    OrganizationSerializer, OrganizationMembershipSerializer, UserProfileSerializer,
    CertificationSerializer, TagSerializer, VendorSerializer,
    CompliancePolicySerializer, ProcurementRequestSerializer,
    ProcurementAttachmentSerializer, VendorSourceDocumentSerializer,
    VendorAuditResultSerializer, ComplianceViolationSerializer,
    HumanReviewSerializer, WorkflowCheckpointSerializer, AgentRunSerializer,
    PerformanceMetricSerializer, APIIntegrationSerializer,
    RequestCommentSerializer, NotificationSerializer, AuditLogSerializer
)

User = get_user_model()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_paginated_data(request, queryset, per_page=20):
    """Helper function to paginate queryset."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def get_search_filter_organization(request, queryset):
    """Helper function to filter organizations."""
    name_filter = request.GET.get('name__icontains', '')
    if name_filter:
        queryset = queryset.filter(name__icontains=name_filter)
    return queryset


def get_search_filter_vendor(request, queryset):
    """Helper function to filter vendors."""
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(headquarters_country__icontains=search)
        )
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    return queryset


def get_search_filter_procurement(request, queryset):
    """Helper function to filter procurement requests."""
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(requirement_prompt__icontains=search)
        )
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if priority_filter:
        queryset = queryset.filter(priority=priority_filter)
    
    return queryset


# ============================================================================
# HOME VIEW
# ============================================================================

def home(request):
    """Home page - redirects to procurement request list."""
    return redirect('procurementrequest_list')


# ============================================================================
# ORGANIZATION VIEWS (Function-Based CRUD)
# ============================================================================

@login_required
def organization_list(request):
    """List all organizations with search and pagination."""
    queryset = Organization.objects.all().order_by('name')
    queryset = get_search_filter_organization(request, queryset)
    
    currency_filter = request.GET.get('default_currency', '')
    if currency_filter:
        queryset = queryset.filter(default_currency=currency_filter)
    
    organizations = get_paginated_data(request, queryset)
    
    context = {
        'organizations': organizations,
        'currency_filter': currency_filter,
    }
    return render(request, 'organization_list.html', context)


@login_required
def organization_detail(request, pk):
    """View organization details."""
    organization = get_object_or_404(Organization, pk=pk)
    context = {'organization': organization}
    return render(request, 'organization_detail.html', context)


@login_required
def organization_create(request):
    """Create a new organization."""
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save()
            messages.success(request, f'Organization "{organization.name}" created successfully!')
            return redirect('organization_detail', pk=organization.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = OrganizationForm()
    
    context = {'form': form, 'title': 'Create Organization'}
    return render(request, 'organization_form.html', context)


@login_required
def organization_update(request, pk):
    """Update an existing organization."""
    organization = get_object_or_404(Organization, pk=pk)
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            organization = form.save()
            messages.success(request, f'Organization "{organization.name}" updated successfully!')
            return redirect('organization_detail', pk=organization.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = OrganizationForm(instance=organization)
    
    context = {'form': form, 'organization': organization, 'title': 'Update Organization'}
    return render(request, 'organization_form.html', context)


@login_required
def organization_delete(request, pk):
    """Delete an organization."""
    organization = get_object_or_404(Organization, pk=pk)
    
    if request.method == 'POST':
        organization_name = organization.name
        organization.delete()
        messages.success(request, f'Organization "{organization_name}" deleted successfully!')
        return redirect('organization_list')
    
    context = {'object': organization}
    return render(request, 'organization_confirm_delete.html', context)


# ============================================================================
# VENDOR VIEWS (Function-Based CRUD)
# ============================================================================

@login_required
def vendor_list(request):
    """List all vendors with search and pagination."""
    queryset = Vendor.objects.all().order_by('name')
    queryset = get_search_filter_vendor(request, queryset)
    
    vendors = get_paginated_data(request, queryset)
    context = {'vendors': vendors}
    return render(request, 'vendor_list.html', context)


@login_required
def vendor_detail(request, pk):
    """View vendor details."""
    vendor = get_object_or_404(Vendor, pk=pk)
    context = {'vendor': vendor}
    return render(request, 'vendor_detail.html', context)


@login_required
def vendor_create(request):
    """Create a new vendor."""
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            vendor = form.save()
            messages.success(request, f'Vendor "{vendor.name}" created successfully!')
            return redirect('vendor_detail', pk=vendor.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VendorForm()
    
    context = {'form': form, 'title': 'Create Vendor'}
    return render(request, 'vendor_form.html', context)


@login_required
def vendor_update(request, pk):
    """Update an existing vendor."""
    vendor = get_object_or_404(Vendor, pk=pk)
    
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            vendor = form.save()
            messages.success(request, f'Vendor "{vendor.name}" updated successfully!')
            return redirect('vendor_detail', pk=vendor.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VendorForm(instance=vendor)
    
    context = {'form': form, 'vendor': vendor, 'title': 'Update Vendor'}
    return render(request, 'vendor_form.html', context)


@login_required
def vendor_delete(request, pk):
    """Delete a vendor."""
    vendor = get_object_or_404(Vendor, pk=pk)
    
    if request.method == 'POST':
        vendor_name = vendor.name
        vendor.delete()
        messages.success(request, f'Vendor "{vendor_name}" deleted successfully!')
        return redirect('vendor_list')
    
    context = {'object': vendor}
    return render(request, 'vendor_confirm_delete.html', context)


# ============================================================================
# COMPLIANCE POLICY VIEWS (Function-Based CRUD)
# ============================================================================

@login_required
def policy_list(request):
    """List all compliance policies with search and pagination."""
    queryset = CompliancePolicy.objects.all().select_related('organization').order_by('name')
    
    search = request.GET.get('search', '')
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(organization__name__icontains=search)
        )
    
    policies = get_paginated_data(request, queryset)
    context = {'policies': policies, 'search': search}
    return render(request, 'policy_list.html', context)


@login_required
def policy_create(request):
    """Create a new compliance policy."""
    if request.method == 'POST':
        form = CompliancePolicyForm(request.POST)
        if form.is_valid():
            policy = form.save()
            messages.success(request, f'Policy "{policy.name}" created successfully!')
            return redirect('policy_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CompliancePolicyForm()
    
    context = {'form': form, 'title': 'Create Policy'}
    return render(request, 'policy_form.html', context)


@login_required
def policy_update(request, pk):
    """Update an existing compliance policy."""
    policy = get_object_or_404(CompliancePolicy, pk=pk)
    
    if request.method == 'POST':
        form = CompliancePolicyForm(request.POST, instance=policy)
        if form.is_valid():
            policy = form.save()
            messages.success(request, f'Policy "{policy.name}" updated successfully!')
            return redirect('policy_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CompliancePolicyForm(instance=policy)
    
    context = {'form': form, 'policy': policy, 'title': 'Update Policy'}
    return render(request, 'policy_form.html', context)


@login_required
def policy_delete(request, pk):
    """Delete a compliance policy."""
    policy = get_object_or_404(CompliancePolicy, pk=pk)
    
    if request.method == 'POST':
        policy_name = policy.name
        policy.delete()
        messages.success(request, f'Policy "{policy_name}" deleted successfully!')
        return redirect('policy_list')
    
    context = {'object': policy}
    return render(request, 'policy_confirm_delete.html', context)


# ============================================================================
# PROCUREMENT REQUEST VIEWS (Function-Based CRUD)
# ============================================================================

@login_required
def procurementrequest_list(request):
    """List all procurement requests with search and pagination."""
    queryset = ProcurementRequest.objects.all().select_related(
        'organization', 'submitted_by', 'assigned_manager'
    ).order_by('-created_at')
    
    # Role-based filtering
    user = request.user
    if user.role == User.Role.MANAGER:
        queryset = queryset.filter(assigned_manager=user)
    elif user.role == User.Role.EMPLOYEE:
        queryset = queryset.filter(submitted_by=user)
    
    queryset = get_search_filter_procurement(request, queryset)
    
    requests = get_paginated_data(request, queryset, per_page=15)
    context = {'requests': requests}
    return render(request, 'procurementrequest_list.html', context)


@login_required
def procurementrequest_detail(request, pk):
    """View procurement request details."""
    request_obj = get_object_or_404(ProcurementRequest, pk=pk)
    context = {'request_obj': request_obj}
    return render(request, 'procurementrequest_detail.html', context)


@login_required
def procurementrequest_create(request):
    """Create a new procurement request."""
    if request.method == 'POST':
        form = ProcurementRequestForm(request.POST)
        if form.is_valid():
            procurement_request = form.save(commit=False)
            procurement_request.submitted_by = request.user
            
            # Set default organization from user profile if not provided
            if not procurement_request.organization and hasattr(request.user, 'profile'):
                procurement_request.organization = request.user.profile.organization
            
            procurement_request.save()
            form.save_m2m()  # Save many-to-many fields
            
            messages.success(request, f'Procurement request "{procurement_request.title}" created successfully!')
            return redirect('procurementrequest_detail', pk=procurement_request.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProcurementRequestForm()
    
    context = {'form': form, 'title': 'Create Procurement Request'}
    return render(request, 'procurementrequest_form.html', context)


@login_required
def procurementrequest_update(request, pk):
    """Update an existing procurement request."""
    procurement_request = get_object_or_404(ProcurementRequest, pk=pk)
    
    # Only allow editing of DRAFT or PENDING requests
    if procurement_request.status not in [ProcurementRequest.Status.DRAFT, ProcurementRequest.Status.PENDING]:
        messages.error(request, 'Only draft or pending requests can be edited.')
        return redirect('procurementrequest_detail', pk=pk)
    
    if request.method == 'POST':
        form = ProcurementRequestForm(request.POST, instance=procurement_request)
        if form.is_valid():
            procurement_request = form.save()
            messages.success(request, f'Request "{procurement_request.title}" updated successfully!')
            return redirect('procurementrequest_detail', pk=procurement_request.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProcurementRequestForm(instance=procurement_request)
    
    context = {'form': form, 'request_obj': procurement_request, 'title': 'Update Procurement Request'}
    return render(request, 'procurementrequest_form.html', context)


@login_required
def procurementrequest_delete(request, pk):
    """Delete a procurement request."""
    procurement_request = get_object_or_404(ProcurementRequest, pk=pk)
    
    if request.method == 'POST':
        request_title = procurement_request.title
        procurement_request.delete()
        messages.success(request, f'Request "{request_title}" deleted successfully!')
        return redirect('procurementrequest_list')
    
    context = {'object': procurement_request}
    return render(request, 'procurementrequest_confirm_delete.html', context)


# ============================================================================
# HUMAN REVIEW VIEWS (Function-Based)
# ============================================================================

@login_required
def human_review_update(request):
    """Update human review for a procurement request."""
    request_id = request.GET.get('request_id')
    human_review = get_object_or_404(HumanReview, request__id=request_id)
    
    if request.method == 'POST':
        form = HumanReviewForm(request.POST, instance=human_review)
        if form.is_valid():
            human_review = form.save(commit=False)
            human_review.reviewed_by = request.user
            human_review.reviewed_at = timezone.now()
            human_review.save()
            
            # Update the procurement request status
            if human_review.decision == HumanReview.Decision.APPROVE_EXCEPTION:
                human_review.request.status = ProcurementRequest.Status.APPROVED_EXCEPTION
            elif human_review.decision == HumanReview.Decision.REJECT:
                human_review.request.status = ProcurementRequest.Status.REJECTED
            elif human_review.decision == HumanReview.Decision.REQUEST_MORE_INFO:
                human_review.request.status = ProcurementRequest.Status.PENDING
            human_review.request.save()
            
            messages.success(request, 'Review submitted successfully!')
            return redirect('procurementrequest_detail', pk=human_review.request.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HumanReviewForm(instance=human_review)
    
    context = {'form': form, 'review': human_review}
    return render(request, 'humanreview_form.html', context)


# ============================================================================
# COMMENT VIEWS (Function-Based)
# ============================================================================

@login_required
def comment_create(request, request_id):
    """Add a comment to a procurement request."""
    procurement_request = get_object_or_404(ProcurementRequest, pk=request_id)
    
    if request.method == 'POST':
        form = RequestCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.request = procurement_request
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('procurementrequest_detail', pk=request_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RequestCommentForm()
    
    context = {'form': form, 'request_id': request_id}
    return render(request, 'comment_form.html', context)


# ============================================================================
# CERTIFICATION VIEWS (Function-Based CRUD)
# ============================================================================

@login_required
def certification_list(request):
    """List all certifications with search and pagination."""
    queryset = Certification.objects.all().order_by('name')
    
    name_filter = request.GET.get('name__icontains', '')
    if name_filter:
        queryset = queryset.filter(name__icontains=name_filter)
    
    issuing_body_filter = request.GET.get('issuing_body__icontains', '')
    if issuing_body_filter:
        queryset = queryset.filter(issuing_body__icontains=issuing_body_filter)
    
    certifications = get_paginated_data(request, queryset)
    context = {
        'certifications': certifications,
        'name_filter': name_filter,
        'issuing_body_filter': issuing_body_filter,
    }
    return render(request, 'certification_list.html', context)


@login_required
def certification_create(request):
    """Create a new certification."""
    if request.method == 'POST':
        form = CertificationForm(request.POST)
        if form.is_valid():
            certification = form.save()
            messages.success(request, f'Certification "{certification.name}" created successfully!')
            return redirect('certification_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CertificationForm()
    
    context = {'form': form, 'title': 'Create Certification'}
    return render(request, 'certification_form.html', context)


@login_required
def certification_update(request, pk):
    """Update an existing certification."""
    certification = get_object_or_404(Certification, pk=pk)
    
    if request.method == 'POST':
        form = CertificationForm(request.POST, instance=certification)
        if form.is_valid():
            certification = form.save()
            messages.success(request, f'Certification "{certification.name}" updated successfully!')
            return redirect('certification_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CertificationForm(instance=certification)
    
    context = {'form': form, 'certification': certification, 'title': 'Update Certification'}
    return render(request, 'certification_form.html', context)


@login_required
def certification_delete(request, pk):
    """Delete a certification."""
    certification = get_object_or_404(Certification, pk=pk)
    
    if request.method == 'POST':
        cert_name = certification.name
        certification.delete()
        messages.success(request, f'Certification "{cert_name}" deleted successfully!')
        return redirect('certification_list')
    
    context = {'object': certification}
    return render(request, 'certification_confirm_delete.html', context)


# ============================================================================
# TAG VIEWS (Function-Based CRUD)
# ============================================================================

@login_required
def tag_list(request):
    """List all tags with search and pagination."""
    queryset = Tag.objects.all().order_by('name')
    
    name_filter = request.GET.get('name__icontains', '')
    if name_filter:
        queryset = queryset.filter(name__icontains=name_filter)
    
    tags = get_paginated_data(request, queryset)
    context = {'tags': tags, 'name_filter': name_filter}
    return render(request, 'tag_list.html', context)


@login_required
def tag_create(request):
    """Create a new tag."""
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save()
            messages.success(request, f'Tag "{tag.name}" created successfully!')
            return redirect('tag_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TagForm()
    
    context = {'form': form, 'title': 'Create Tag'}
    return render(request, 'tag_form.html', context)


@login_required
def tag_update(request, pk):
    """Update an existing tag."""
    tag = get_object_or_404(Tag, pk=pk)
    
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            tag = form.save()
            messages.success(request, f'Tag "{tag.name}" updated successfully!')
            return redirect('tag_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TagForm(instance=tag)
    
    context = {'form': form, 'tag': tag, 'title': 'Update Tag'}
    return render(request, 'tag_form.html', context)


@login_required
def tag_delete(request, pk):
    """Delete a tag."""
    tag = get_object_or_404(Tag, pk=pk)
    
    if request.method == 'POST':
        tag_name = tag.name
        tag.delete()
        messages.success(request, f'Tag "{tag_name}" deleted successfully!')
        return redirect('tag_list')
    
    context = {'object': tag}
    return render(request, 'tag_confirm_delete.html', context)


# ============================================================================
# USER PROFILE VIEWS (Function-Based)
# ============================================================================

@login_required
def userprofile_update(request):
    """Update user profile."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('procurementrequest_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {'form': form, 'profile': profile}
    return render(request, 'userprofile_form.html', context)


# ============================================================================
# API INTEGRATION VIEWS (Function-Based CRUD)
# ============================================================================

@login_required
def apiintegration_list(request):
    """List all API integrations with search and pagination."""
    queryset = APIIntegration.objects.all().select_related('organization').order_by('name')
    
    name_filter = request.GET.get('name__icontains', '')
    if name_filter:
        queryset = queryset.filter(name__icontains=name_filter)
    
    provider_filter = request.GET.get('provider', '')
    if provider_filter:
        queryset = queryset.filter(provider=provider_filter)
    
    integrations = get_paginated_data(request, queryset)
    context = {
        'integrations': integrations,
        'name_filter': name_filter,
        'provider_filter': provider_filter,
    }
    return render(request, 'apiintegration_list.html', context)


@login_required
def apiintegration_create(request):
    """Create a new API integration."""
    if request.method == 'POST':
        form = APIIntegrationForm(request.POST)
        if form.is_valid():
            integration = form.save()
            messages.success(request, f'API Integration "{integration.name}" created successfully!')
            return redirect('apiintegration_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = APIIntegrationForm()
    
    context = {'form': form, 'title': 'Create API Integration'}
    return render(request, 'apiintegration_form.html', context)


@login_required
def apiintegration_update(request, pk):
    """Update an existing API integration."""
    integration = get_object_or_404(APIIntegration, pk=pk)
    
    if request.method == 'POST':
        form = APIIntegrationForm(request.POST, instance=integration)
        if form.is_valid():
            integration = form.save()
            messages.success(request, f'API Integration "{integration.name}" updated successfully!')
            return redirect('apiintegration_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = APIIntegrationForm(instance=integration)
    
    context = {'form': form, 'integration': integration, 'title': 'Update API Integration'}
    return render(request, 'apiintegration_form.html', context)


@login_required
def apiintegration_delete(request, pk):
    """Delete an API integration."""
    integration = get_object_or_404(APIIntegration, pk=pk)
    
    if request.method == 'POST':
        integration_name = integration.name
        integration.delete()
        messages.success(request, f'API Integration "{integration_name}" deleted successfully!')
        return redirect('apiintegration_list')
    
    context = {'object': integration}
    return render(request, 'apiintegration_confirm_delete.html', context)


# ============================================================================
# API VIEWS (DRF - Function-Based)
# ============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_organization_list_create(request):
    """API endpoint to list and create organizations."""
    if request.method == 'GET':
        organizations = Organization.objects.all().order_by('name')
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def api_organization_detail(request, pk):
    """API endpoint to retrieve, update, and delete an organization."""
    try:
        organization = Organization.objects.get(pk=pk)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = OrganizationSerializer(organization, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        organization.delete()
        return Response({'message': 'Organization deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_vendor_list_create(request):
    """API endpoint to list and create vendors."""
    if request.method == 'GET':
        vendors = Vendor.objects.all().order_by('name')
        serializer = VendorSerializer(vendors, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def api_vendor_detail(request, pk):
    """API endpoint to retrieve, update, and delete a vendor."""
    try:
        vendor = Vendor.objects.get(pk=pk)
    except Vendor.DoesNotExist:
        return Response({'error': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = VendorSerializer(vendor)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = VendorSerializer(vendor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        vendor.delete()
        return Response({'message': 'Vendor deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_procurement_list_create(request):
    """API endpoint to list and create procurement requests."""
    if request.method == 'GET':
        requests = ProcurementRequest.objects.all().select_related(
            'organization', 'submitted_by', 'assigned_manager'
        ).order_by('-created_at')
        serializer = ProcurementRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ProcurementRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(submitted_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def api_procurement_detail(request, pk):
    """API endpoint to retrieve, update, and delete a procurement request."""
    try:
        procurement = ProcurementRequest.objects.get(pk=pk)
    except ProcurementRequest.DoesNotExist:
        return Response({'error': 'Procurement request not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ProcurementRequestSerializer(procurement)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ProcurementRequestSerializer(procurement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        procurement.delete()
        return Response({'message': 'Procurement request deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_procurement_submit(request, pk):
    """API endpoint to submit a procurement request for review."""
    try:
        procurement = ProcurementRequest.objects.get(pk=pk)
    except ProcurementRequest.DoesNotExist:
        return Response({'error': 'Procurement request not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if procurement.status == ProcurementRequest.Status.DRAFT:
        procurement.status = ProcurementRequest.Status.PENDING
        procurement.save()
        return Response({'status': 'submitted', 'message': 'Request submitted successfully'})
    return Response({'error': 'Only draft requests can be submitted'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_comment_list_create(request, request_id):
    """API endpoint to list and create comments for a procurement request."""
    try:
        procurement = ProcurementRequest.objects.get(pk=request_id)
    except ProcurementRequest.DoesNotExist:
        return Response({'error': 'Procurement request not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        comments = RequestComment.objects.filter(request=procurement).order_by('created_at')
        serializer = RequestCommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = RequestCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request=procurement, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_certification_list(request):
    """API endpoint to list certifications."""
    certifications = Certification.objects.all().order_by('name')
    serializer = CertificationSerializer(certifications, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_tag_list(request):
    """API endpoint to list tags."""
    tags = Tag.objects.all().order_by('name')
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_policy_list(request):
    """API endpoint to list compliance policies."""
    policies = CompliancePolicy.objects.all().select_related('organization')
    serializer = CompliancePolicySerializer(policies, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_notification_mark_read(request, pk):
    """API endpoint to mark a notification as read."""
    try:
        notification = Notification.objects.get(pk=pk, recipient=request.user)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
    notification.mark_as_read()
    return Response({'status': 'marked as read', 'message': 'Notification marked as read'})