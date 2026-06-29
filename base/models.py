import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class UUIDTimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYEE = "EMPLOYEE", "Employee"
        MANAGER = "MANAGER", "Manager"
        COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER", "Compliance Officer"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(max_length=40, choices=Role.choices, default=Role.EMPLOYEE)
    department = models.CharField(max_length=120, blank=True)
    job_title = models.CharField(max_length=120, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    can_approve_exceptions = models.BooleanField(default=False)

    # Fix the reverse accessor clash with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='base_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='base_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.get_full_name() or self.username


class Organization(UUIDTimeStampedModel):
    name = models.CharField(max_length=180, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    domain = models.CharField(max_length=180, blank=True)
    default_currency = models.CharField(max_length=3, default="USD")
    annual_budget = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="OrganizationMembership",
        related_name="organizations",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class OrganizationMembership(UUIDTimeStampedModel):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        MEMBER = "MEMBER", "Member"
        VIEWER = "VIEWER", "Viewer"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.MEMBER)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"],
                name="unique_user_per_organization",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.organization}"


class UserProfile(UUIDTimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles",
    )
    timezone = models.CharField(max_length=80, default="UTC")
    notification_settings = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Profile of {self.user}"


class Certification(UUIDTimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    issuing_body = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Tag(UUIDTimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Vendor(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        DISCOVERED = "DISCOVERED", "Discovered"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        ARCHIVED = "ARCHIVED", "Archived"

    name = models.CharField(max_length=180)
    website_url = models.URLField(max_length=500, blank=True)
    headquarters_country = models.CharField(max_length=100, blank=True)
    support_email = models.EmailField(blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DISCOVERED)
    certifications = models.ManyToManyField(Certification, blank=True, related_name="vendors")
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "website_url"],
                name="unique_vendor_name_website",
            )
        ]

    def __str__(self):
        return self.name


class CompliancePolicy(UUIDTimeStampedModel):
    class Severity(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="policies",
    )
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)
    is_active = models.BooleanField(default=True)
    rules_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Machine-readable policy rules for compliance evaluation.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_policy_per_organization",
            )
        ]

    def __str__(self):
        return f"{self.organization} - {self.name}"


class ProcurementRequest(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING = "PENDING", "Pending"
        SCRAPING = "SCRAPING", "Scraping"
        EXTRACTING = "EXTRACTING", "Extracting"
        AUDITING = "AUDITING", "Auditing"
        WAITING_REVIEW = "WAITING_REVIEW", "Awaiting Human Review"
        APPROVED_EXCEPTION = "APPROVED_EXCEPTION", "Exception Approved"
        REJECTED = "REJECTED", "Rejected"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        NORMAL = "NORMAL", "Normal"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="procurement_requests",
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="submitted_requests",
    )
    assigned_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_requests",
    )

    title = models.CharField(max_length=220)
    requirement_prompt = models.TextField()
    business_justification = models.TextField(blank=True)

    max_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3, default="USD")

    required_certifications = models.ManyToManyField(
        Certification,
        blank=True,
        related_name="procurement_requests",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="procurement_requests")

    status = models.CharField(max_length=40, choices=Status.choices, default=Status.PENDING)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL)

    celery_task_id = models.CharField(max_length=255, blank=True, db_index=True)
    langgraph_thread_id = models.CharField(max_length=255, blank=True, db_index=True)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)

    input_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["submitted_by", "status"]),
            models.Index(fields=["priority", "created_at"]),
        ]

    def __str__(self):
        return self.title

    @property
    def requires_human_review(self):
        return self.status == self.Status.WAITING_REVIEW


class ProcurementAttachment(UUIDTimeStampedModel):
    request = models.ForeignKey(
        ProcurementRequest,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_attachments",
    )
    file = models.FileField(upload_to="procurement/attachments/%Y/%m/")
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=120, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return self.original_filename


class VendorSourceDocument(UUIDTimeStampedModel):
    class SourceType(models.TextChoices):
        WEBSITE = "WEBSITE", "Website"
        PRICING_PAGE = "PRICING_PAGE", "Pricing Page"
        SLA = "SLA", "Service Level Agreement"
        SECURITY_PAGE = "SECURITY_PAGE", "Security Page"
        DOCUMENT = "DOCUMENT", "Document"
        MANUAL = "MANUAL", "Manual Entry"

    request = models.ForeignKey(
        ProcurementRequest,
        on_delete=models.CASCADE,
        related_name="source_documents",
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="source_documents",
    )
    source_type = models.CharField(max_length=40, choices=SourceType.choices)
    url = models.URLField(max_length=800, blank=True)
    raw_text = models.TextField(blank=True)
    content_hash = models.CharField(max_length=128, blank=True, db_index=True)
    scraped_at = models.DateTimeField(null=True, blank=True)
    scraper_metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.vendor} - {self.source_type}"


class VendorAuditResult(UUIDTimeStampedModel):
    class RiskLevel(models.TextChoices):
        UNKNOWN = "UNKNOWN", "Unknown"
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    request = models.ForeignKey(
        ProcurementRequest,
        on_delete=models.CASCADE,
        related_name="audit_results",
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="audit_results",
    )

    extracted_product_name = models.CharField(max_length=220, blank=True)
    pricing_model = models.CharField(max_length=120, blank=True)

    annual_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3, default="USD")

    has_soc2 = models.BooleanField(default=False)
    has_iso27001 = models.BooleanField(default=False)
    has_gdpr = models.BooleanField(default=False)
    has_hipaa = models.BooleanField(default=False)

    sla_uptime_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.UNKNOWN)
    compliance_score = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    structured_json = models.JSONField(default=dict, blank=True)
    pricing_matrix = models.JSONField(default=dict, blank=True)
    compliance_failures = models.JSONField(default=list, blank=True)
    final_markdown_report = models.TextField(blank=True)

    extraction_confidence = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    is_recommended = models.BooleanField(default=False)

    class Meta:
        ordering = ["-compliance_score", "annual_cost"]
        constraints = [
            models.UniqueConstraint(
                fields=["request", "vendor"],
                name="unique_vendor_audit_per_request",
            )
        ]
        indexes = [
            models.Index(fields=["request", "risk_level"]),
            models.Index(fields=["vendor", "risk_level"]),
            models.Index(fields=["is_recommended"]),
        ]

    def __str__(self):
        return f"{self.vendor} audit for {self.request}"


class ComplianceViolation(UUIDTimeStampedModel):
    class ResolutionStatus(models.TextChoices):
        OPEN = "OPEN", "Open"
        APPROVED_EXCEPTION = "APPROVED_EXCEPTION", "Approved Exception"
        REJECTED = "REJECTED", "Rejected"
        RESOLVED = "RESOLVED", "Resolved"

    audit_result = models.ForeignKey(
        VendorAuditResult,
        on_delete=models.CASCADE,
        related_name="violations",
    )
    policy = models.ForeignKey(
        CompliancePolicy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="violations",
    )
    title = models.CharField(max_length=220)
    details = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=CompliancePolicy.Severity.choices,
        default=CompliancePolicy.Severity.MEDIUM,
    )
    resolution_status = models.CharField(
        max_length=40,
        choices=ResolutionStatus.choices,
        default=ResolutionStatus.OPEN,
    )
    evidence_json = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title


class HumanReview(UUIDTimeStampedModel):
    class Decision(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVE_EXCEPTION = "APPROVE_EXCEPTION", "Approve Exception"
        REJECT = "REJECT", "Reject"
        REQUEST_MORE_INFO = "REQUEST_MORE_INFO", "Request More Info"

    request = models.OneToOneField(
        ProcurementRequest,
        on_delete=models.CASCADE,
        related_name="human_review",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_human_reviews",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="completed_human_reviews",
    )
    decision = models.CharField(max_length=40, choices=Decision.choices, default=Decision.PENDING)
    reason = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resume_payload = models.JSONField(default=dict, blank=True)

    def complete_review(self, reviewer, decision, reason=""):
        self.reviewed_by = reviewer
        self.decision = decision
        self.reason = reason
        self.reviewed_at = timezone.now()
        self.save(update_fields=["reviewed_by", "decision", "reason", "reviewed_at", "updated_at"])

    def __str__(self):
        return f"Review for {self.request}"


class WorkflowCheckpoint(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        PAUSED = "PAUSED", "Paused"
        RESUMED = "RESUMED", "Resumed"
        EXPIRED = "EXPIRED", "Expired"

    request = models.ForeignKey(
        ProcurementRequest,
        on_delete=models.CASCADE,
        related_name="workflow_checkpoints",
    )
    checkpoint_key = models.CharField(max_length=255, db_index=True)
    node_name = models.CharField(max_length=120, db_index=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.ACTIVE)

    state_blob = models.BinaryField(null=True, blank=True)
    state_json_preview = models.JSONField(default=dict, blank=True)
    interrupt_reason = models.TextField(blank=True)
    resumed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["request", "checkpoint_key"],
                name="unique_checkpoint_per_request",
            )
        ]

    def __str__(self):
        return f"{self.request} - {self.node_name}"


class AgentRun(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        RUNNING = "RUNNING", "Running"
        PAUSED = "PAUSED", "Paused"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    request = models.ForeignKey(
        ProcurementRequest,
        on_delete=models.CASCADE,
        related_name="agent_runs",
    )
    celery_task_id = models.CharField(max_length=255, blank=True, db_index=True)
    langgraph_run_id = models.CharField(max_length=255, blank=True, db_index=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.QUEUED)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    input_snapshot = models.JSONField(default=dict, blank=True)
    output_snapshot = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.request} - {self.status}"


class PerformanceMetric(UUIDTimeStampedModel):
    request = models.ForeignKey(
        ProcurementRequest,
        on_delete=models.CASCADE,
        related_name="performance_metrics",
    )
    agent_run = models.ForeignKey(
        AgentRun,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performance_metrics",
    )
    node_name = models.CharField(max_length=120, db_index=True)
    model_name = models.CharField(max_length=120, blank=True)

    execution_duration_ms = models.PositiveIntegerField(default=0)
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    retry_count = models.PositiveSmallIntegerField(default=0)

    metadata = models.JSONField(default=dict, blank=True)

    def save(self, *args, **kwargs):
        self.total_tokens = self.input_tokens + self.output_tokens
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.node_name} metric"


class APIIntegration(UUIDTimeStampedModel):
    class Provider(models.TextChoices):
        OLLAMA = "OLLAMA", "Ollama"
        VLLM = "VLLM", "vLLM"
        INTERNAL_WEBHOOK = "INTERNAL_WEBHOOK", "Internal Webhook"
        CUSTOM = "CUSTOM", "Custom"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="api_integrations",
    )
    provider = models.CharField(max_length=40, choices=Provider.choices)
    name = models.CharField(max_length=160)
    base_url = models.URLField(max_length=500)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    last_health_check_at = models.DateTimeField(null=True, blank=True)
    last_health_status = models.CharField(max_length=80, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_integration_per_organization",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.provider})"


class RequestComment(UUIDTimeStampedModel):
    request = models.ForeignKey(
        ProcurementRequest,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="procurement_comments",
    )
    body = models.TextField()
    is_internal = models.BooleanField(default=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment on {self.request}"


class Notification(UUIDTimeStampedModel):
    class Type(models.TextChoices):
        REVIEW_REQUIRED = "REVIEW_REQUIRED", "Review Required"
        REQUEST_COMPLETED = "REQUEST_COMPLETED", "Request Completed"
        REQUEST_FAILED = "REQUEST_FAILED", "Request Failed"
        COMMENT_ADDED = "COMMENT_ADDED", "Comment Added"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    request = models.ForeignKey(
        ProcurementRequest,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    notification_type = models.CharField(max_length=40, choices=Type.choices)
    title = models.CharField(max_length=180)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at", "updated_at"])

    def __str__(self):
        return self.title


class AuditLog(UUIDTimeStampedModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    request = models.ForeignKey(
        ProcurementRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=120, db_index=True)
    object_type = models.CharField(max_length=120, blank=True)
    object_id = models.CharField(max_length=120, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.action