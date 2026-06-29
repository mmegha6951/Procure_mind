# base/serializers.py
from rest_framework import serializers
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
# BASE SERIALIZERS
# ============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'department', 'job_title', 'phone_number',
            'can_approve_exceptions', 'date_joined', 'last_login', 'is_active'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""
    
    member_count = serializers.IntegerField(source='members.count', read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'domain', 'default_currency',
            'annual_budget', 'member_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    """Serializer for Organization Membership model."""
    
    organization = OrganizationSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), source='organization', write_only=True
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = OrganizationMembership
        fields = [
            'id', 'organization', 'organization_id', 'user', 'user_id',
            'role', 'role_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for User Profile model."""
    
    user = UserSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), source='organization', write_only=True,
        required=False, allow_null=True
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'organization', 'organization_id',
            'timezone', 'notification_settings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CertificationSerializer(serializers.ModelSerializer):
    """Serializer for Certification model."""
    
    vendor_count = serializers.IntegerField(source='vendors.count', read_only=True)
    
    class Meta:
        model = Certification
        fields = [
            'id', 'name', 'issuing_body', 'description',
            'vendor_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    
    usage_count = serializers.IntegerField(source='procurement_requests.count', read_only=True)
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'usage_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# VENDOR & COMPLIANCE SERIALIZERS
# ============================================================================

class VendorSerializer(serializers.ModelSerializer):
    """Serializer for Vendor model."""
    
    certifications = CertificationSerializer(many=True, read_only=True)
    certification_ids = serializers.PrimaryKeyRelatedField(
        queryset=Certification.objects.all(), source='certifications',
        write_only=True, many=True, required=False
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    certification_count = serializers.IntegerField(source='certifications.count', read_only=True)
    
    class Meta:
        model = Vendor
        fields = [
            'id', 'name', 'website_url', 'headquarters_country', 'support_email',
            'status', 'status_display', 'certifications', 'certification_ids',
            'certification_count', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompliancePolicySerializer(serializers.ModelSerializer):
    """Serializer for Compliance Policy model."""
    
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), source='organization', write_only=True
    )
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = CompliancePolicy
        fields = [
            'id', 'organization', 'organization_id', 'name', 'description',
            'severity', 'severity_display', 'is_active', 'rules_json',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# PROCUREMENT REQUEST SERIALIZERS
# ============================================================================

class ProcurementAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for Procurement Attachment model."""
    
    uploaded_by = UserSerializer(read_only=True)
    uploaded_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='uploaded_by', write_only=True,
        required=False, allow_null=True
    )
    size_kb = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcurementAttachment
        fields = [
            'id', 'uploaded_by', 'uploaded_by_id', 'file', 'original_filename',
            'content_type', 'size_bytes', 'size_kb', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_size_kb(self, obj):
        return round(obj.size_bytes / 1024, 1) if obj.size_bytes else 0


class ProcurementRequestSerializer(serializers.ModelSerializer):
    """Serializer for Procurement Request model."""
    
    organization = OrganizationSerializer(read_only=True)
    submitted_by = UserSerializer(read_only=True)
    assigned_manager = UserSerializer(read_only=True)
    required_certifications = CertificationSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    attachments = ProcurementAttachmentSerializer(many=True, read_only=True)
    
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), source='organization', write_only=True
    )
    submitted_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='submitted_by', write_only=True
    )
    assigned_manager_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assigned_manager', write_only=True,
        required=False, allow_null=True
    )
    required_certification_ids = serializers.PrimaryKeyRelatedField(
        queryset=Certification.objects.all(), source='required_certifications',
        write_only=True, many=True, required=False
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), source='tags',
        write_only=True, many=True, required=False
    )
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = ProcurementRequest
        fields = [
            'id', 'organization', 'organization_id', 'submitted_by', 'submitted_by_id',
            'assigned_manager', 'assigned_manager_id', 'title', 'requirement_prompt',
            'business_justification', 'max_budget', 'currency', 'required_certifications',
            'required_certification_ids', 'tags', 'tag_ids', 'status', 'status_display',
            'priority', 'priority_display', 'attachments', 'celery_task_id',
            'langgraph_thread_id', 'started_at', 'completed_at', 'failure_reason',
            'input_payload', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'celery_task_id', 'langgraph_thread_id',
            'started_at', 'completed_at', 'failure_reason', 'created_at', 'updated_at'
        ]


# ============================================================================
# VENDOR SOURCE & AUDIT SERIALIZERS
# ============================================================================

class VendorSourceDocumentSerializer(serializers.ModelSerializer):
    """Serializer for Vendor Source Document model."""
    
    vendor = VendorSerializer(read_only=True)
    vendor_id = serializers.PrimaryKeyRelatedField(
        queryset=Vendor.objects.all(), source='vendor', write_only=True
    )
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    
    class Meta:
        model = VendorSourceDocument
        fields = [
            'id', 'vendor', 'vendor_id', 'source_type', 'source_type_display',
            'url', 'raw_text', 'content_hash', 'scraped_at', 'scraper_metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'content_hash', 'created_at', 'updated_at']


class VendorAuditResultSerializer(serializers.ModelSerializer):
    """Serializer for Vendor Audit Result model."""
    
    vendor = VendorSerializer(read_only=True)
    vendor_id = serializers.PrimaryKeyRelatedField(
        queryset=Vendor.objects.all(), source='vendor', write_only=True
    )
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    
    class Meta:
        model = VendorAuditResult
        fields = [
            'id', 'vendor', 'vendor_id', 'extracted_product_name', 'pricing_model',
            'annual_cost', 'currency', 'has_soc2', 'has_iso27001', 'has_gdpr',
            'has_hipaa', 'sla_uptime_percent', 'risk_level', 'risk_level_display',
            'compliance_score', 'structured_json', 'pricing_matrix',
            'compliance_failures', 'final_markdown_report', 'extraction_confidence',
            'is_recommended', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ComplianceViolationSerializer(serializers.ModelSerializer):
    """Serializer for Compliance Violation model."""
    
    audit_result = VendorAuditResultSerializer(read_only=True)
    audit_result_id = serializers.PrimaryKeyRelatedField(
        queryset=VendorAuditResult.objects.all(), source='audit_result', write_only=True
    )
    policy = CompliancePolicySerializer(read_only=True)
    policy_id = serializers.PrimaryKeyRelatedField(
        queryset=CompliancePolicy.objects.all(), source='policy', write_only=True,
        required=False, allow_null=True
    )
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    resolution_status_display = serializers.CharField(source='get_resolution_status_display', read_only=True)
    
    class Meta:
        model = ComplianceViolation
        fields = [
            'id', 'audit_result', 'audit_result_id', 'policy', 'policy_id',
            'title', 'details', 'severity', 'severity_display',
            'resolution_status', 'resolution_status_display', 'evidence_json',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# HUMAN REVIEW SERIALIZER
# ============================================================================

class HumanReviewSerializer(serializers.ModelSerializer):
    """Serializer for Human Review model."""
    
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assigned_to', write_only=True,
        required=False, allow_null=True
    )
    reviewed_by = UserSerializer(read_only=True)
    reviewed_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewed_by', write_only=True,
        required=False, allow_null=True
    )
    decision_display = serializers.CharField(source='get_decision_display', read_only=True)
    
    class Meta:
        model = HumanReview
        fields = [
            'id', 'assigned_to', 'assigned_to_id', 'reviewed_by', 'reviewed_by_id',
            'decision', 'decision_display', 'reason', 'reviewed_at', 'resume_payload',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reviewed_at', 'created_at', 'updated_at']


# ============================================================================
# WORKFLOW & AGENT SERIALIZERS
# ============================================================================

class WorkflowCheckpointSerializer(serializers.ModelSerializer):
    """Serializer for Workflow Checkpoint model."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = WorkflowCheckpoint
        fields = [
            'id', 'checkpoint_key', 'node_name', 'status', 'status_display',
            'state_blob', 'state_json_preview', 'interrupt_reason', 'resumed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AgentRunSerializer(serializers.ModelSerializer):
    """Serializer for Agent Run model."""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AgentRun
        fields = [
            'id', 'celery_task_id', 'langgraph_run_id', 'status', 'status_display',
            'started_at', 'finished_at', 'error_message',
            'input_snapshot', 'output_snapshot', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PerformanceMetricSerializer(serializers.ModelSerializer):
    """Serializer for Performance Metric model."""
    
    agent_run = AgentRunSerializer(read_only=True)
    agent_run_id = serializers.PrimaryKeyRelatedField(
        queryset=AgentRun.objects.all(), source='agent_run', write_only=True,
        required=False, allow_null=True
    )
    
    class Meta:
        model = PerformanceMetric
        fields = [
            'id', 'agent_run', 'agent_run_id', 'node_name', 'model_name',
            'execution_duration_ms', 'input_tokens', 'output_tokens',
            'total_tokens', 'retry_count', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_tokens', 'created_at', 'updated_at']


# ============================================================================
# API INTEGRATION SERIALIZER
# ============================================================================

class APIIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for API Integration model."""
    
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), source='organization', write_only=True
    )
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = APIIntegration
        fields = [
            'id', 'organization', 'organization_id', 'provider', 'provider_display',
            'name', 'base_url', 'is_active', 'config', 'last_health_check_at',
            'last_health_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# COMMENT & NOTIFICATION SERIALIZERS
# ============================================================================

class RequestCommentSerializer(serializers.ModelSerializer):
    """Serializer for Request Comment model."""
    
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='author', write_only=True,
        required=False, allow_null=True
    )
    
    class Meta:
        model = RequestComment
        fields = [
            'id', 'author', 'author_id', 'body', 'is_internal',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    
    recipient = UserSerializer(read_only=True)
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='recipient', write_only=True
    )
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_id', 'notification_type',
            'notification_type_display', 'title', 'message', 'is_read',
            'read_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'read_at', 'created_at', 'updated_at']


# ============================================================================
# AUDIT LOG SERIALIZER
# ============================================================================

class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for Audit Log model."""
    
    actor = UserSerializer(read_only=True)
    actor_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='actor', write_only=True,
        required=False, allow_null=True
    )
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(), source='organization', write_only=True,
        required=False, allow_null=True
    )
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'actor', 'actor_id', 'organization', 'organization_id',
            'action', 'object_type', 'object_id', 'ip_address', 'user_agent',
            'before', 'after', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']