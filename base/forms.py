# base/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import (
    Organization, OrganizationMembership, UserProfile, Certification, Tag,
    Vendor, CompliancePolicy, ProcurementRequest, ProcurementAttachment,
    VendorSourceDocument, VendorAuditResult, ComplianceViolation, HumanReview,
    WorkflowCheckpoint, AgentRun, PerformanceMetric, APIIntegration,
    RequestComment, Notification, AuditLog
)

User = get_user_model()


# ============================================================================
# USER AUTHENTICATION FORMS
# ============================================================================

class CustomUserCreationForm(UserCreationForm):
    """Form for creating a new user with custom fields."""
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'role',
            'department', 'job_title', 'phone_number', 'can_approve_exceptions'
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job title'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91-XXXXXXXXXX'}),
            'can_approve_exceptions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CustomUserChangeForm(UserChangeForm):
    """Form for editing an existing user."""
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'role',
            'department', 'job_title', 'phone_number', 'can_approve_exceptions'
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'can_approve_exceptions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ============================================================================
# ORGANIZATION FORMS
# ============================================================================

class OrganizationForm(forms.ModelForm):
    """Form for creating/updating an organization."""
    
    class Meta:
        model = Organization
        fields = ['name', 'slug', 'domain', 'default_currency', 'annual_budget']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Organization name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'organization-slug'}),
            'domain': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'example.com'}),
            'default_currency': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('USD', 'USD - US Dollar'),
                ('INR', 'INR - Indian Rupee'),
                ('EUR', 'EUR - Euro'),
                ('GBP', 'GBP - British Pound'),
                ('AED', 'AED - UAE Dirham'),
                ('SGD', 'SGD - Singapore Dollar'),
            ]),
            'annual_budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
        }


class OrganizationMembershipForm(forms.ModelForm):
    """Form for managing organization memberships."""
    
    class Meta:
        model = OrganizationMembership
        fields = ['organization', 'user', 'role']
        widgets = {
            'organization': forms.Select(attrs={'class': 'form-select'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""
    
    class Meta:
        model = UserProfile
        fields = ['organization', 'timezone', 'notification_settings']
        widgets = {
            'organization': forms.Select(attrs={'class': 'form-select'}),
            'timezone': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('UTC', 'UTC'),
                ('Asia/Kolkata', 'Asia/Kolkata (IST)'),
                ('America/New_York', 'America/New_York (EST)'),
                ('Europe/London', 'Europe/London (GMT)'),
                ('Australia/Sydney', 'Australia/Sydney (AEST)'),
                ('Asia/Dubai', 'Asia/Dubai (GST)'),
                ('Asia/Singapore', 'Asia/Singapore (SGT)'),
                ('Asia/Tokyo', 'Asia/Tokyo (JST)'),
            ]),
            'notification_settings': forms.Textarea(attrs={
                'class': 'form-control json-editor',
                'rows': 3,
                'placeholder': '{"email": true, "sms": false, "whatsapp": true}'
            }),
        }


# ============================================================================
# MASTER DATA FORMS
# ============================================================================

class CertificationForm(forms.ModelForm):
    """Form for creating/updating certifications."""
    
    class Meta:
        model = Certification
        fields = ['name', 'issuing_body', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ISO 9001:2015'}),
            'issuing_body': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., International Organization for Standardization'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Certification description'}),
        }


class TagForm(forms.ModelForm):
    """Form for creating/updating tags."""
    
    class Meta:
        model = Tag
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tag name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'tag-slug'}),
        }


# ============================================================================
# VENDOR FORMS
# ============================================================================

class VendorForm(forms.ModelForm):
    """Form for creating/updating vendors."""
    
    class Meta:
        model = Vendor
        fields = [
            'name', 'website_url', 'headquarters_country', 'support_email',
            'status', 'certifications', 'metadata'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vendor name'}),
            'website_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'headquarters_country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country name'}),
            'support_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'support@example.com'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'certifications': forms.SelectMultiple(attrs={'class': 'form-control multi-select'}),
            'metadata': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3, 'placeholder': '{"key": "value"}'}),
        }


# ============================================================================
# COMPLIANCE FORMS
# ============================================================================

class CompliancePolicyForm(forms.ModelForm):
    """Form for creating/updating compliance policies."""
    
    class Meta:
        model = CompliancePolicy
        fields = ['organization', 'name', 'description', 'severity', 'is_active', 'rules_json']
        widgets = {
            'organization': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Policy name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Policy description'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'rules_json': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 5, 'placeholder': '{"rule": "value"}'}),
        }


class ComplianceViolationForm(forms.ModelForm):
    """Form for creating/updating compliance violations."""
    
    class Meta:
        model = ComplianceViolation
        fields = ['audit_result', 'policy', 'title', 'details', 'severity', 'resolution_status', 'evidence_json']
        widgets = {
            'audit_result': forms.Select(attrs={'class': 'form-select'}),
            'policy': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Violation title'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Violation details...'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'resolution_status': forms.Select(attrs={'class': 'form-select'}),
            'evidence_json': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3, 'placeholder': '{"evidence": "value"}'}),
        }


# ============================================================================
# PROCUREMENT REQUEST FORMS
# ============================================================================

class ProcurementRequestForm(forms.ModelForm):
    """Form for creating/updating a procurement request."""
    
    required_certifications = forms.ModelMultipleChoiceField(
        queryset=Certification.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control multi-select'}),
        required=False,
        label='Required Certifications'
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control multi-select'}),
        required=False,
        label='Tags'
    )

    class Meta:
        model = ProcurementRequest
        fields = [
            'organization', 'title', 'requirement_prompt', 'business_justification',
            'max_budget', 'currency', 'required_certifications', 'tags',
            'priority', 'assigned_manager'
        ]
        widgets = {
            'organization': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Request title'}),
            'requirement_prompt': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your requirements...'}),
            'business_justification': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Why is this procurement needed?'}),
            'max_budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'currency': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('USD', 'USD'),
                ('INR', 'INR'),
                ('EUR', 'EUR'),
                ('GBP', 'GBP'),
            ]),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_manager': forms.Select(attrs={'class': 'form-select'}),
        }


class ProcurementAttachmentForm(forms.ModelForm):
    """Form for uploading procurement attachments."""
    
    class Meta:
        model = ProcurementAttachment
        fields = ['request', 'file', 'original_filename', 'content_type', 'size_bytes']
        widgets = {
            'request': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'original_filename': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Original filename'}),
            'content_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'application/pdf'}),
            'size_bytes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
        }


# ============================================================================
# VENDOR SOURCE & AUDIT FORMS
# ============================================================================

class VendorSourceDocumentForm(forms.ModelForm):
    """Form for creating vendor source documents."""
    
    class Meta:
        model = VendorSourceDocument
        fields = ['request', 'vendor', 'source_type', 'url', 'raw_text', 'scraper_metadata']
        widgets = {
            'request': forms.Select(attrs={'class': 'form-select'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'source_type': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'raw_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Scraped content...'}),
            'scraper_metadata': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3, 'placeholder': '{"key": "value"}'}),
        }


class VendorAuditResultForm(forms.ModelForm):
    """Form for creating vendor audit results."""
    
    class Meta:
        model = VendorAuditResult
        fields = [
            'request', 'vendor', 'extracted_product_name', 'pricing_model',
            'annual_cost', 'currency', 'has_soc2', 'has_iso27001', 'has_gdpr',
            'has_hipaa', 'sla_uptime_percent', 'risk_level', 'compliance_score',
            'structured_json', 'pricing_matrix', 'compliance_failures',
            'final_markdown_report', 'extraction_confidence', 'is_recommended'
        ]
        widgets = {
            'request': forms.Select(attrs={'class': 'form-select'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'extracted_product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'pricing_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subscription/One-time'}),
            'annual_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'has_soc2': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_iso27001': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_gdpr': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_hipaa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sla_uptime_percent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'risk_level': forms.Select(attrs={'class': 'form-select'}),
            'compliance_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'structured_json': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3}),
            'pricing_matrix': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3}),
            'compliance_failures': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3}),
            'final_markdown_report': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'extraction_confidence': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_recommended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ============================================================================
# HUMAN REVIEW FORM
# ============================================================================

class HumanReviewForm(forms.ModelForm):
    """Form for human review of procurement requests."""
    
    class Meta:
        model = HumanReview
        fields = ['decision', 'reason', 'resume_payload']
        widgets = {
            'decision': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for decision...'}),
            'resume_payload': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 2, 'placeholder': '{"resume": "data"}'}),
        }


# ============================================================================
# WORKFLOW & AGENT FORMS
# ============================================================================

class WorkflowCheckpointForm(forms.ModelForm):
    """Form for managing workflow checkpoints."""
    
    class Meta:
        model = WorkflowCheckpoint
        fields = ['request', 'checkpoint_key', 'node_name', 'status', 'state_json_preview', 'interrupt_reason']
        widgets = {
            'request': forms.Select(attrs={'class': 'form-select'}),
            'checkpoint_key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'checkpoint_key'}),
            'node_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Node name'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'state_json_preview': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3}),
            'interrupt_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class AgentRunForm(forms.ModelForm):
    """Form for managing agent runs."""
    
    class Meta:
        model = AgentRun
        fields = [
            'request', 'celery_task_id', 'langgraph_run_id', 'status',
            'error_message', 'input_snapshot', 'output_snapshot'
        ]
        widgets = {
            'request': forms.Select(attrs={'class': 'form-select'}),
            'celery_task_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'celery_task_id'}),
            'langgraph_run_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'langgraph_run_id'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'error_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'input_snapshot': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3}),
            'output_snapshot': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3}),
        }


class PerformanceMetricForm(forms.ModelForm):
    """Form for tracking performance metrics."""
    
    class Meta:
        model = PerformanceMetric
        fields = [
            'request', 'agent_run', 'node_name', 'model_name',
            'execution_duration_ms', 'input_tokens', 'output_tokens',
            'retry_count', 'metadata'
        ]
        widgets = {
            'request': forms.Select(attrs={'class': 'form-select'}),
            'agent_run': forms.Select(attrs={'class': 'form-select'}),
            'node_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Node name'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Model name'}),
            'execution_duration_ms': forms.NumberInput(attrs={'class': 'form-control'}),
            'input_tokens': forms.NumberInput(attrs={'class': 'form-control'}),
            'output_tokens': forms.NumberInput(attrs={'class': 'form-control'}),
            'retry_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'metadata': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3}),
        }


# ============================================================================
# API INTEGRATION FORM
# ============================================================================

class APIIntegrationForm(forms.ModelForm):
    """Form for configuring API integrations."""
    
    class Meta:
        model = APIIntegration
        fields = ['organization', 'provider', 'name', 'base_url', 'is_active', 'config']
        widgets = {
            'organization': forms.Select(attrs={'class': 'form-select'}),
            'provider': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Integration name'}),
            'base_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://api.example.com'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'config': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3, 'placeholder': '{"api_key": "key", "timeout": 30}'}),
        }


# ============================================================================
# COMMENT & NOTIFICATION FORMS
# ============================================================================

class RequestCommentForm(forms.ModelForm):
    """Form for adding comments to procurement requests."""
    
    class Meta:
        model = RequestComment
        fields = ['body', 'is_internal']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment...'
            }),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class NotificationForm(forms.ModelForm):
    """Form for creating/updating notifications."""
    
    class Meta:
        model = Notification
        fields = ['recipient', 'request', 'notification_type', 'title', 'message', 'is_read']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-select'}),
            'request': forms.Select(attrs={'class': 'form-select'}),
            'notification_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Notification title'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notification message...'}),
            'is_read': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ============================================================================
# AUDIT LOG FORM (Read-Only)
# ============================================================================

class AuditLogForm(forms.ModelForm):
    """Form for viewing audit logs (read-only)."""
    
    class Meta:
        model = AuditLog
        fields = [
            'actor', 'organization', 'request', 'action',
            'object_type', 'object_id', 'ip_address', 'user_agent',
            'before', 'after'
        ]
        widgets = {
            'actor': forms.Select(attrs={'class': 'form-select'}),
            'organization': forms.Select(attrs={'class': 'form-select'}),
            'request': forms.Select(attrs={'class': 'form-select'}),
            'action': forms.TextInput(attrs={'class': 'form-control'}),
            'object_type': forms.TextInput(attrs={'class': 'form-control'}),
            'object_id': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control'}),
            'user_agent': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'before': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3}),
            'after': forms.Textarea(attrs={'class': 'form-control json-editor', 'rows': 3}),
        }