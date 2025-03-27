from django.db import models
from django.utils import timezone
from django.core.validators import (
    MinValueValidator, MaxValueValidator, RegexValidator, URLValidator, EmailValidator
)
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
import uuid


# Custom Manager for System Configuration
class SystemConfigManager(models.Manager):
    def get_active_config(self):
        return self.filter(is_active=True).first()

    def by_version(self, version):
        return self.filter(version=version).first()


# System Configuration Model
class SystemConfig(models.Model):
    config_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Configuration Name"))
    version = models.CharField(max_length=20, unique=True, verbose_name=_("Version"), help_text=_("e.g., 'v1.0.0'"))
    is_active = models.BooleanField(default=False, verbose_name=_("Is Active"))
    settings = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Settings"),
        help_text=_("JSON string: '{\"maintenance_mode\": false, \"default_radius\": 5, \"ad_refresh_rate\": 300}'"),
        default=dict
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    maintenance_mode = models.BooleanField(default=False, verbose_name=_("Maintenance Mode"))
    default_currency = models.CharField(max_length=3, default='USD', verbose_name=_("Default Currency"))
    max_upload_size_mb = models.PositiveIntegerField(default=10, verbose_name=_("Max Upload Size (MB)"))
    supported_languages = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Supported Languages"),
        help_text=_("JSON string: '[\"en\", \"es\", \"fr\"]'"),
        default=list
    )

    objects = SystemConfigManager()

    class Meta:
        verbose_name = _("System Configuration")
        verbose_name_plural = _("System Configurations")
        ordering = ['-version']
        indexes = [
            models.Index(fields=['version']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.version})"

    def save(self, *args, **kwargs):
        if self.is_active:
            SystemConfig.objects.filter(is_active=True).exclude(config_id=self.config_id).update(is_active=False)
        super().save(*args, **kwargs)


# Advertisement Campaign Model
class AdCampaign(models.Model):
    campaign_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ad_campaigns',
        verbose_name=_("Campaign Owner")
    )
    name = models.CharField(max_length=255, verbose_name=_("Campaign Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'), ('pending', 'Pending Review'), ('active', 'Active'),
            ('paused', 'Paused'), ('completed', 'Completed'), ('rejected', 'Rejected')
        ],
        default='draft',
        verbose_name=_("Status")
    )
    start_date = models.DateTimeField(verbose_name=_("Start Date"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("End Date"))
    budget = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Budget")
    )
    currency = models.CharField(max_length=3, default='USD', verbose_name=_("Currency"))
    bid_strategy = models.CharField(
        max_length=20,
        choices=[
            ('cpm', 'Cost Per Mille (CPM)'), ('cpc', 'Cost Per Click (CPC)'),
            ('cpa', 'Cost Per Action (CPA)'), ('flat', 'Flat Rate')
        ],
        default='cpm',
        verbose_name=_("Bid Strategy")
    )
    bid_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Bid Amount")
    )
    target_audience = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Target Audience"),
        help_text=_("JSON string: '{\"roles\": [\"buyer\", \"agent\"], \"locations\": [\"NYC\"]}'"),
        default=dict
    )
    target_locations = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Target Locations"),
        help_text=_("JSON string: '[{\"lat\": 40.7128, \"lon\": -74.0060, \"radius_km\": 5}]'"),
        default=list
    )
    target_devices = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Target Devices"),
        help_text=_("JSON string: '[\"mobile\", \"desktop\", \"tablet\"]'"),
        default=list
    )
    target_languages = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Target Languages"),
        help_text=_("JSON string: '[\"en\", \"es\"]'"),
        default=list
    )
    frequency_cap = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1)],
        verbose_name=_("Frequency Cap"),
        help_text=_("Max impressions per user per day")
    )
    impressions_goal = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Impressions Goal")
    )
    clicks_goal = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Clicks Goal")
    )
    conversion_goal = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Conversion Goal")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    approval_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending',
        verbose_name=_("Approval Status")
    )
    rejection_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_("Rejection Reason")
    )
    total_spent = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0.0,
        verbose_name=_("Total Spent")
    )
    remaining_budget = models.DecimalField(
        max_digits=15, decimal_places=2,
        blank=True, null=True,
        verbose_name=_("Remaining Budget")
    )

    class Meta:
        verbose_name = _("Ad Campaign")
        verbose_name_plural = _("Ad Campaigns")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['approval_status']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.name} - {self.user.email}"

    def save(self, *args, **kwargs):
        if self.budget is not None and self.total_spent is not None:
            self.remaining_budget = self.budget - self.total_spent
        super().save(*args, **kwargs)


# Banner Model
class Banner(models.Model):
    banner_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        'AdCampaign',
        on_delete=models.CASCADE,
        related_name='banners',
        verbose_name=_("Campaign")
    )
    title = models.CharField(max_length=255, verbose_name=_("Banner Title"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    image = models.ImageField(
        upload_to='banners/%Y/%m/%d/',
        verbose_name=_("Banner Image")
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name=_("Alt Text"),
        help_text=_("For accessibility")
    )
    video = models.FileField(
        upload_to='banners/videos/%Y/%m/%d/',
        blank=True, null=True,
        verbose_name=_("Banner Video")
    )
    banner_type = models.CharField(
        max_length=20,
        choices=[
            ('static', 'Static Image'), ('video', 'Video'), ('carousel', 'Carousel'),
            ('html', 'HTML5'), ('gif', 'Animated GIF')
        ],
        default='static',
        verbose_name=_("Banner Type")
    )
    size = models.CharField(
        max_length=20,
        choices=[
            ('300x250', 'Medium Rectangle (300x250)'),
            ('728x90', 'Leaderboard (728x90)'),
            ('160x600', 'Skyscraper (160x600)'),
            ('320x50', 'Mobile Banner (320x50)'),
            ('custom', 'Custom')
        ],
        default='300x250',
        verbose_name=_("Banner Size")
    )
    custom_width = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Custom Width (px)"),
        help_text=_("If size is 'custom'")
    )
    custom_height = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Custom Height (px)"),
        help_text=_("If size is 'custom'")
    )
    target_url = models.URLField(
        validators=[URLValidator()],
        verbose_name=_("Target URL"),
        help_text=_("Where the banner links to")
    )
    call_to_action = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=_("Call to Action"),
        help_text=_("e.g., 'Learn More', 'Buy Now'")
    )
    placement = models.CharField(
        max_length=20,
        choices=[
            ('homepage', 'Homepage'), ('listing_page', 'Listing Page'),
            ('sidebar', 'Sidebar'), ('footer', 'Footer'), ('popup', 'Popup'),
            ('in_app', 'In-App'), ('email', 'Email Newsletter')
        ],
        verbose_name=_("Placement")
    )
    priority = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_("Priority"),
        help_text=_("Higher priority banners displayed first")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    impressions = models.PositiveIntegerField(default=0, verbose_name=_("Impressions"))
    clicks = models.PositiveIntegerField(default=0, verbose_name=_("Clicks"))
    conversions = models.PositiveIntegerField(default=0, verbose_name=_("Conversions"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    animation_duration = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Animation Duration (seconds)")
    )
    background_color = models.CharField(
        max_length=7,
        blank=True, null=True,
        validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$')],
        verbose_name=_("Background Color"),
        help_text=_("Hex code, e.g., '#FFFFFF'")
    )
    text_color = models.CharField(
        max_length=7,
        blank=True, null=True,
        validators=[RegexValidator(r'^#[0-9A-Fa-f]{6}$')],
        verbose_name=_("Text Color"),
        help_text=_("Hex code, e.g., '#000000'")
    )
    font_family = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=_("Font Family"),
        help_text=_("e.g., 'Arial', 'Roboto'")
    )
    font_size = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Font Size (px)")
    )
    html_content = models.TextField(
        blank=True, null=True,
        verbose_name=_("HTML Content"),
        help_text=_("For HTML5 banners")
    )
    carousel_items = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Carousel Items"),
        help_text=_("JSON string: '[{\"image\": \"url1\", \"text\": \"slide1\"}, ...]'"),
        default=list
    )

    class Meta:
        verbose_name = _("Banner")
        verbose_name_plural = _("Banners")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['campaign']),
            models.Index(fields=['is_active']),
            models.Index(fields=['placement']),
        ]

    def __str__(self):
        return f"{self.title} - {self.campaign.name}"


# Advertisement Request Model
class AdRequest(models.Model):
    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ad_requests',
        verbose_name=_("Requester")
    )
    campaign = models.ForeignKey(
        'AdCampaign',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ad_requests',
        verbose_name=_("Related Campaign")
    )
    title = models.CharField(max_length=255, verbose_name=_("Request Title"))
    description = models.TextField(verbose_name=_("Description"))
    request_type = models.CharField(
        max_length=20,
        choices=[
            ('new_ad', 'New Advertisement'), ('edit_ad', 'Edit Existing Ad'),
            ('priority_boost', 'Priority Boost'), ('extension', 'Campaign Extension'),
            ('custom_placement', 'Custom Placement')
        ],
        verbose_name=_("Request Type")
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'),
            ('in_progress', 'In Progress'), ('completed', 'Completed')
        ],
        default='pending',
        verbose_name=_("Status")
    )
    budget = models.DecimalField(
        max_digits=15, decimal_places=2,
        blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Proposed Budget")
    )
    start_date = models.DateTimeField(verbose_name=_("Requested Start Date"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Requested End Date"))
    target_audience = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Target Audience"),
        help_text=_("JSON string: '{\"roles\": [\"buyer\"], \"age_range\": [25, 45]}'"),
        default=dict
    )
    target_locations = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Target Locations"),
        help_text=_("JSON string: '[{\"city\": \"NYC\", \"radius_km\": 10}]'"),
        default=list
    )
    placement_preference = models.CharField(
        max_length=20,
        choices=[
            ('homepage', 'Homepage'), ('listing_page', 'Listing Page'),
            ('sidebar', 'Sidebar'), ('footer', 'Footer'), ('popup', 'Popup'),
            ('in_app', 'In-App'), ('email', 'Email Newsletter'), ('custom', 'Custom')
        ],
        blank=True, null=True,
        verbose_name=_("Placement Preference")
    )
    custom_placement_details = models.TextField(
        blank=True, null=True,
        verbose_name=_("Custom Placement Details")
    )
    priority_level = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_("Priority Level")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='ad_request_reviews',
        verbose_name=_("Reviewed By")
    )
    review_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Review Date"))
    rejection_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_("Rejection Reason")
    )
    additional_notes = models.TextField(
        blank=True, null=True,
        verbose_name=_("Additional Notes")
    )
    attached_files = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Attached Files"),
        help_text=_("JSON string: '[{\"url\": \"/media/file.pdf\", \"type\": \"pdf\"}]'"),
        default=list
    )

    class Meta:
        verbose_name = _("Ad Request")
        verbose_name_plural = _("Ad Requests")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['request_type']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"


# Ad Analytics Model
class AdAnalytics(models.Model):
    analytics_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    banner = models.ForeignKey(
        'Banner',
        on_delete=models.CASCADE,
        related_name='analytics',
        verbose_name=_("Banner")
    )
    date = models.DateField(verbose_name=_("Date"))
    impressions = models.PositiveIntegerField(default=0, verbose_name=_("Impressions"))
    clicks = models.PositiveIntegerField(default=0, verbose_name=_("Clicks"))
    conversions = models.PositiveIntegerField(default=0, verbose_name=_("Conversions"))
    click_through_rate = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Click-Through Rate (%)")
    )
    conversion_rate = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Conversion Rate (%)")
    )
    cost = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=0.0,
        verbose_name=_("Cost")
    )
    revenue = models.DecimalField(
        max_digits=15, decimal_places=2,
        blank=True, null=True,
        verbose_name=_("Revenue")
    )
    unique_visitors = models.PositiveIntegerField(default=0, verbose_name=_("Unique Visitors"))
    bounce_rate = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Bounce Rate (%)")
    )
    avg_time_spent_seconds = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("Avg Time Spent (seconds)")
    )
    device_breakdown = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Device Breakdown"),
        help_text=_("JSON string: '{\"mobile\": 50, \"desktop\": 30, \"tablet\": 20}'"),
        default=dict
    )
    location_breakdown = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Location Breakdown"),
        help_text=_("JSON string: '{\"NYC\": 40, \"LA\": 30, \"SF\": 20}'"),
        default=dict
    )
    demographic_breakdown = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Demographic Breakdown"),
        help_text=_("JSON string: '{\"age_18_24\": 20, \"male\": 60}'"),
        default=dict
    )

    class Meta:
        verbose_name = _("Ad Analytics")
        verbose_name_plural = _("Ad Analytics")
        ordering = ['-date']
        indexes = [
            models.Index(fields=['banner']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"Analytics for {self.banner.title} - {self.date}"

    def save(self, *args, **kwargs):
        if self.impressions and self.clicks:
            self.click_through_rate = (self.clicks / self.impressions) * 100
        if self.clicks and self.conversions:
            self.conversion_rate = (self.conversions / self.clicks) * 100
        super().save(*args, **kwargs)


# Transaction Model
class Transaction(models.Model):
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='purchases',
        verbose_name=_("Buyer")
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales',
        verbose_name=_("Seller")
    )
    listing = models.ForeignKey(
        'property.Listing',  # Assuming 'property' app exists
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name=_("Listing")
    )
    campaign = models.ForeignKey(
        'AdCampaign',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name=_("Ad Campaign")
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ('sale', 'Property Sale'), ('rent', 'Rental'), ('lease', 'Lease'),
            ('ad_payment', 'Ad Payment'), ('deposit', 'Deposit'), ('refund', 'Refund'),
            ('subscription', 'Subscription')
        ],
        verbose_name=_("Transaction Type")
    )
    amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Amount")
    )
    currency = models.CharField(max_length=3, default='USD', verbose_name=_("Currency"))
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'),
            ('cancelled', 'Cancelled'), ('disputed', 'Disputed'), ('refunded', 'Refunded')
        ],
        default='pending',
        verbose_name=_("Status")
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('credit_card', 'Credit Card'), ('bank_transfer', 'Bank Transfer'),
            ('paypal', 'PayPal'), ('crypto', 'Cryptocurrency'), ('cash', 'Cash'),
            ('check', 'Check'), ('invoice', 'Invoice')
        ],
        blank=True, null=True,
        verbose_name=_("Payment Method")
    )
    payment_gateway = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=_("Payment Gateway"),
        help_text=_("e.g., 'Stripe', 'PayPal'")
    )
    transaction_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Transaction Date"))
    completed_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Completed Date"))
    external_transaction_id = models.CharField(
        max_length=100,
        blank=True, null=True,
        unique=True,
        verbose_name=_("External Transaction ID")
    )
    fee = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Transaction Fee")
    )
    tax = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Tax")
    )
    receipt_url = models.URLField(
        blank=True, null=True,
        validators=[URLValidator()],
        verbose_name=_("Receipt URL")
    )
    invoice_number = models.CharField(
        max_length=50,
        blank=True, null=True,
        unique=True,
        verbose_name=_("Invoice Number")
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    escrow_enabled = models.BooleanField(default=False, verbose_name=_("Escrow Enabled"))
    escrow_release_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Escrow Release Date"))
    refund_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_("Refund Reason")
    )
    dispute_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_("Dispute Reason")
    )
    dispute_resolved_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Dispute Resolved At")
    )

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['buyer', 'seller']),
        ]

    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_type} - {self.amount} {self.currency}"


# Message Model
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_("Sender")
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name=_("Recipient")
    )
    subject = models.CharField(max_length=255, blank=True, verbose_name=_("Subject"))
    body = models.TextField(verbose_name=_("Message Body"))
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Sent At"))
    read_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Read At"))
    is_read = models.BooleanField(default=False, verbose_name=_("Is Read"))
    parent_message = models.ForeignKey(
        'self',
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='replies',
        verbose_name=_("Parent Message")
    )
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'), ('inquiry', 'Inquiry'), ('offer', 'Offer'),
            ('system', 'System'), ('alert', 'Alert'), ('ad_response', 'Ad Response')
        ],
        default='text',
        verbose_name=_("Message Type")
    )
    attachment = models.FileField(
        upload_to='messages/attachments/%Y/%m/%d/',
        blank=True, null=True,
        verbose_name=_("Attachment")
    )
    attachment_metadata = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Attachment Metadata"),
        help_text=_("JSON string: '{\"filename\": \"doc.pdf\", \"size\": 1024}'"),
        default=dict
    )
    is_flagged = models.BooleanField(default=False, verbose_name=_("Is Flagged"))
    flag_reason = models.TextField(blank=True, null=True, verbose_name=_("Flag Reason"))
    priority = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium',
        verbose_name=_("Priority")
    )
    delivery_status = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Delivery Status"),
        help_text=_("JSON string: '{\"email\": \"delivered\", \"sms\": \"pending\"}'"),
        default=dict
    )

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['sender', 'recipient']),
            models.Index(fields=['is_read']),
            models.Index(fields=['message_type']),
        ]

    def __str__(self):
        return f"{self.sender.email} -> {self.recipient.email}: {self.subject or self.body[:50]}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


# Support Ticket Model
class SupportTicket(models.Model):
    ticket_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_tickets',
        verbose_name=_("User")
    )
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    description = models.TextField(verbose_name=_("Description"))
    category = models.CharField(
        max_length=20,
        choices=[
            ('account', 'Account'), ('payment', 'Payment'), ('listing', 'Listing'),
            ('advertising', 'Advertising'), ('technical', 'Technical'), ('other', 'Other')
        ],
        default='other',
        verbose_name=_("Category")
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('open', 'Open'), ('in_progress', 'In Progress'), ('resolved', 'Resolved'),
            ('closed', 'Closed'), ('on_hold', 'On Hold')
        ],
        default='open',
        verbose_name=_("Status")
    )
    priority = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],
        default='medium',
        verbose_name=_("Priority")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Resolved At"))
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='assigned_tickets',
        verbose_name=_("Assigned To")
    )
    resolution_notes = models.TextField(blank=True, null=True, verbose_name=_("Resolution Notes"))
    attachments = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Attachments"),
        help_text=_("JSON string: '[{\"url\": \"/media/ticket1.jpg\", \"type\": \"image\"}]'"),
        default=list
    )
    ticket_source = models.CharField(
        max_length=20,
        choices=[('web', 'Website'), ('app', 'Mobile App'), ('email', 'Email'), ('phone', 'Phone')],
        default='web',
        verbose_name=_("Ticket Source")
    )
    escalation_level = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Escalation Level")
    )

    class Meta:
        verbose_name = _("Support Ticket")
        verbose_name_plural = _("Support Tickets")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"Ticket #{self.ticket_id} - {self.subject}"


# Feedback Model
class Feedback(models.Model):
    feedback_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name=_("User")
    )
    feedback_type = models.CharField(
        max_length=20,
        choices=[
            ('feature', 'Feature Request'), ('bug', 'Bug Report'), ('general', 'General Feedback'),
            ('ui', 'UI/UX'), ('performance', 'Performance'), ('advertising', 'Advertising')
        ],
        verbose_name=_("Feedback Type")
    )
    description = models.TextField(verbose_name=_("Description"))
    rating = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Rating")
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Submitted At"))
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'), ('reviewed', 'Reviewed'), ('in_progress', 'In Progress'),
            ('resolved', 'Resolved'), ('closed', 'Closed')
        ],
        default='pending',
        verbose_name=_("Status")
    )
    response = models.TextField(blank=True, null=True, verbose_name=_("Response"))
    response_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Response At"))
    attachment = models.FileField(
        upload_to='feedback/attachments/%Y/%m/%d/',
        blank=True, null=True,
        verbose_name=_("Attachment")
    )
    page_url = models.URLField(
        blank=True, null=True,
        verbose_name=_("Page URL"),
        help_text=_("Where the feedback was submitted")
    )
    device_info = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name=_("Device Info"),
        help_text=_("e.g., 'iPhone 14, iOS 17'")
    )

    class Meta:
        verbose_name = _("Feedback")
        verbose_name_plural = _("Feedbacks")
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['feedback_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.feedback_type} - {self.submitted_at}"


# System Log Model
class SystemLog(models.Model):
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    log_type = models.CharField(
        max_length=20,
        choices=[
            ('info', 'Info'), ('warning', 'Warning'), ('error', 'Error'),
            ('debug', 'Debug'), ('critical', 'Critical'), ('ad_event', 'Ad Event')
        ],
        verbose_name=_("Log Type")
    )
    message = models.TextField(verbose_name=_("Message"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='system_logs',
        verbose_name=_("Related User")
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP Address"))
    request_path = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Request Path"))
    stack_trace = models.TextField(blank=True, null=True, verbose_name=_("Stack Trace"))
    metadata = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Metadata"),
        help_text=_("JSON string: '{\"browser\": \"Chrome\", \"ad_id\": \"uuid123\"}'"),
        default=dict
    )
    severity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_("Severity")
    )

    class Meta:
        verbose_name = _("System Log")
        verbose_name_plural = _("System Logs")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['log_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.log_type} - {self.timestamp}"


# Announcement Model
class Announcement(models.Model):
    announcement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    content = models.TextField(verbose_name=_("Content"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='announcements',
        verbose_name=_("Created By")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    start_date = models.DateTimeField(verbose_name=_("Start Date"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("End Date"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    priority = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],
        default='medium',
        verbose_name=_("Priority")
    )
    target_audience = models.CharField(
        max_length=20,
        choices=[
            ('all', 'All Users'), ('buyers', 'Buyers'), ('sellers', 'Sellers'),
            ('agents', 'Agents'), ('admins', 'Admins'), ('advertisers', 'Advertisers')
        ],
        default='all',
        verbose_name=_("Target Audience")
    )
    custom_audience = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Custom Audience"),
        help_text=_("JSON string: '{\"user_ids\": [\"uuid1\", \"uuid2\"]}'"),
        default=dict
    )
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Views Count"))
    display_locations = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Display Locations"),
        help_text=_("JSON string: '[\"homepage\", \"dashboard\"]'"),
        default=list
    )
    image = models.ImageField(
        upload_to='announcements/%Y/%m/%d/',
        blank=True, null=True,
        verbose_name=_("Image")
    )

    class Meta:
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['priority']),
            models.Index(fields=['target_audience']),
        ]

    def __str__(self):
        return f"{self.title} - {self.created_at}"


# Contact Us Model
class ContactUs(models.Model):
    contact_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, validators=[RegexValidator(r'^[a-zA-Z\s]+$')], verbose_name=_("Name"))
    email = models.EmailField(validators=[EmailValidator()], verbose_name=_("Email"))
    phone_number = PhoneNumberField(blank=True, null=True, verbose_name=_("Phone Number"))
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    message = models.TextField(verbose_name=_("Message"))
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Submitted At"))
    status = models.CharField(
        max_length=20,
        choices=[('new', 'New'), ('in_progress', 'In Progress'), ('resolved', 'Resolved')],
        default='new',
        verbose_name=_("Status")
    )
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='contact_responses',
        verbose_name=_("Responded By")
    )
    response = models.TextField(blank=True, null=True, verbose_name=_("Response"))
    response_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Response At"))
    source = models.CharField(
        max_length=20,
        choices=[('web', 'Website'), ('app', 'App'), ('email', 'Email')],
        default='web',
        verbose_name=_("Source")
    )
    attachments = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Attachments"),
        help_text=_("JSON string: '[{\"url\": \"/media/file.jpg\", \"type\": \"image\"}]'"),
        default=list
    )

    class Meta:
        verbose_name = _("Contact Us Entry")
        verbose_name_plural = _("Contact Us Entries")
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['submitted_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.subject}"


# FAQ Model
class FAQ(models.Model):
    faq_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=255, verbose_name=_("Question"))
    answer = models.TextField(verbose_name=_("Answer"))
    category = models.CharField(
        max_length=50,
        choices=[
            ('account', 'Account'), ('listing', 'Listings'), ('payment', 'Payments'),
            ('advertising', 'Advertising'), ('general', 'General'), ('technical', 'Technical')
        ],
        default='general',
        verbose_name=_("Category")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Views Count"))
    helpful_count = models.PositiveIntegerField(default=0, verbose_name=_("Helpful Count"))
    not_helpful_count = models.PositiveIntegerField(default=0, verbose_name=_("Not Helpful Count"))
    tags = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Tags"),
        help_text=_("JSON string: '[\"ads\", \"billing\", \"support\"]'"),
        default=list
    )

    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.question


# Legal Document Model
class LegalDocument(models.Model):
    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    content = models.TextField(verbose_name=_("Content"))
    document_type = models.CharField(
        max_length=20,
        choices=[
            ('terms', 'Terms of Service'), ('privacy', 'Privacy Policy'),
            ('disclaimer', 'Disclaimer'), ('agreement', 'User Agreement'),
            ('ad_policy', 'Advertising Policy'), ('gdpr', 'GDPR Compliance'),
            ('ccpa', 'CCPA Notice')
        ],
        verbose_name=_("Document Type")
    )
    version = models.CharField(max_length=20, verbose_name=_("Version"), help_text=_("e.g., 'v1.0.0'"))
    effective_date = models.DateTimeField(verbose_name=_("Effective Date"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    audience = models.CharField(
        max_length=20,
        choices=[('all', 'All'), ('users', 'Users'), ('advertisers', 'Advertisers')],
        default='all',
        verbose_name=_("Audience")
    )

    class Meta:
        verbose_name = _("Legal Document")
        verbose_name_plural = _("Legal Documents")
        ordering = ['-effective_date']
        unique_together = ('document_type', 'version')
        indexes = [
            models.Index(fields=['document_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.title} ({self.version})"


# Audit Log Model
class AuditLog(models.Model):
    audit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='audit_entries',
        verbose_name=_("User")
    )
    action_type = models.CharField(
        max_length=20,
        choices=[
            ('create', 'Create'), ('update', 'Update'), ('delete', 'Delete'),
            ('login', 'Login'), ('logout', 'Logout'), ('permission_change', 'Permission Change'),
            ('ad_action', 'Ad Action')
        ],
        verbose_name=_("Action Type")
    )
    model_name = models.CharField(max_length=100, verbose_name=_("Model Name"))
    object_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Object ID"))
    old_value = models.JSONField(blank=True, null=True, verbose_name=_("Old Value"), default=dict)
    new_value = models.JSONField(blank=True, null=True, verbose_name=_("New Value"), default=dict)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP Address"))
    user_agent = models.TextField(blank=True, null=True, verbose_name=_("User Agent"))
    request_method = models.CharField(
        max_length=10,
        blank=True, null=True,
        verbose_name=_("Request Method"),
        help_text=_("e.g., 'GET', 'POST'")
    )

    class Meta:
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action_type']),
            models.Index(fields=['model_name']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.action_type} - {self.model_name} - {self.timestamp}"


# Geofence Alert Model
class GeofenceAlert(models.Model):
    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='geofence_alerts',
        verbose_name=_("User")
    )
    geofence_name = models.CharField(max_length=100, verbose_name=_("Geofence Name"))
    coordinates = models.JSONField(
        verbose_name=_("Coordinates"),
        help_text=_("JSON string: '[{\"lat\": 40.7128, \"lon\": -74.0060}, ...]'"),
        default=list
    )
    radius_km = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0.1)],
        verbose_name=_("Radius (km)")
    )
    trigger_type = models.CharField(
        max_length=20,
        choices=[('enter', 'Enter'), ('exit', 'Exit'), ('both', 'Both')],
        default='enter',
        verbose_name=_("Trigger Type")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    last_triggered = models.DateTimeField(blank=True, null=True, verbose_name=_("Last Triggered"))
    notification_method = models.CharField(
        max_length=20,
        choices=[('email', 'Email'), ('sms', 'SMS'), ('push', 'Push'), ('whatsapp', 'WhatsApp')],
        default='push',
        verbose_name=_("Notification Method")
    )
    alert_message = models.TextField(
        blank=True, null=True,
        verbose_name=_("Alert Message"),
        help_text=_("Custom message sent on trigger")
    )
    trigger_count = models.PositiveIntegerField(default=0, verbose_name=_("Trigger Count"))

    class Meta:
        verbose_name = _("Geofence Alert")
        verbose_name_plural = _("Geofence Alerts")
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['last_triggered']),
        ]

    def __str__(self):
        return f"{self.geofence_name} - {self.user.email}"