# -------- Users App Models --------- #
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone
from django.core.validators import (
    MinLengthValidator, RegexValidator, MinValueValidator, MaxValueValidator,
    EmailValidator, URLValidator
)
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
import uuid
from django.utils.translation import gettext_lazy as _

# Custom User Manager
class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('date_joined', timezone.now())
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        UserActivity.objects.create(
            user=user,
            action_type='account_creation',
            action_detail=f"User {email} created account"
        )
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('user_role', 'admin')
        return self.create_user(email, password, **extra_fields)

    def nearby_users(self, latitude, longitude, distance_km=10):
        # Simplified: Filter based on latitude/longitude (approximation, no GIS)
        return self.filter(
            primary_location_latitude__gte=latitude - distance_km / 111,
            primary_location_latitude__lte=latitude + distance_km / 111,
            primary_location_longitude__gte=longitude - distance_km / 111,
            primary_location_longitude__lte=longitude + distance_km / 111
        )

    def active_users(self):
        return self.filter(is_active=True, account_status='active')

    def by_role(self, role):
        return self.filter(user_role=role)

# Main User Model
class User(AbstractUser):
    # Authentication & Core Identifiers
    username = None
    email = models.EmailField(
        unique=True,
        max_length=255,
        validators=[MinLengthValidator(5), EmailValidator()],
        verbose_name=_("Primary Email"),
        help_text=_("Primary email for login, notifications, and recovery")
    )
    secondary_email = models.EmailField(
        blank=True, null=True,
        max_length=255,
        unique=True,
        validators=[EmailValidator()],
        verbose_name=_("Secondary Email"),
        help_text=_("Backup email for recovery or alternate contact")
    )
    user_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text=_("Unique UUID for internal tracking")
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Personal Information
    title = models.CharField(
        max_length=20,
        choices=[('mr', 'Mr.'), ('mrs', 'Mrs.'), ('ms', 'Ms.'), ('dr', 'Dr.'), ('prof', 'Prof.')],
        blank=True, null=True,
        verbose_name=_("Title"),
        help_text=_("Honorific title")
    )
    first_name = models.CharField(
        max_length=50,
        blank=True,
        validators=[MinLengthValidator(2), RegexValidator(r'^[a-zA-Z\- ]+$')],
        verbose_name=_("First Name")
    )
    last_name = models.CharField(
        max_length=50,
        blank=True,
        validators=[MinLengthValidator(2), RegexValidator(r'^[a-zA-Z\- ]+$')],
        verbose_name=_("Last Name")
    )
    middle_name = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Middle Name"))
    maiden_name = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=_("Maiden Name"),
        help_text=_("For historical or legal reference")
    )
    suffix = models.CharField(
        max_length=10,
        blank=True, null=True,
        choices=[('jr', 'Jr'), ('sr', 'Sr'), ('ii', 'II'), ('iii', 'III'), ('iv', 'IV')],
        verbose_name=_("Suffix")
    )
    preferred_name = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=_("Preferred Name"),
        help_text=_("Nickname or preferred display name")
    )
    date_of_birth = models.DateField(
        blank=True, null=True,
        validators=[MaxValueValidator(timezone.now().date())],
        verbose_name=_("Date of Birth")
    )
    gender = models.CharField(
        max_length=20,
        choices=[
            ('male', 'Male'), ('female', 'Female'), ('nonbinary', 'Non-binary'),
            ('other', 'Other'), ('prefer_not_to_say', 'Prefer not to say')
        ],
        blank=True, null=True,
        verbose_name=_("Gender")
    )
    gender_custom = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=_("Custom Gender"),
        help_text=_("If 'Other' selected, user can specify")
    )
    pronouns = models.CharField(
        max_length=20,
        blank=True, null=True,
        verbose_name=_("Pronouns"),
        help_text=_("e.g., 'they/them', 'he/him', 'she/her'")
    )
    marital_status = models.CharField(
        max_length=20,
        choices=[
            ('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced'),
            ('widowed', 'Widowed'), ('partnered', 'Partnered'), ('separated', 'Separated')
        ],
        blank=True, null=True,
        verbose_name=_("Marital Status")
    )
    nationality = CountryField(blank=True, null=True, verbose_name=_("Nationality"))
    languages_spoken = models.JSONField(  # Updated to JSONField
        blank=True, null=True,
        verbose_name=_("Languages Spoken"),
        help_text=_("e.g., ['English', 'Spanish', 'Mandarin']")
    )

    # Contact Information
    phone_number = PhoneNumberField(
        blank=True, null=True,
        verbose_name=_("Primary Phone"),
        help_text=_("e.g., +12025550123")
    )
    secondary_phone_number = PhoneNumberField(blank=True, null=True, verbose_name=_("Secondary Phone"))
    fax_number = PhoneNumberField(blank=True, null=True, verbose_name=_("Fax Number"))
    whatsapp_number = PhoneNumberField(
        blank=True, null=True,
        verbose_name=_("WhatsApp Number"),
        help_text=_("For messaging integration")
    )
    skype_id = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("Skype ID"),
        help_text=_("For video calls or messaging")
    )
    profile_picture = models.ImageField(
        upload_to='users/profile_pics/%Y/%m/%d/',
        blank=True, null=True,
        verbose_name=_("Profile Picture")
    )
    cover_photo = models.ImageField(
        upload_to='users/cover_photos/%Y/%m/%d/',
        blank=True, null=True,
        verbose_name=_("Cover Photo")
    )
    video_intro = models.FileField(
        upload_to='users/video_intros/%Y/%m/%d/',
        blank=True, null=True,
        verbose_name=_("Video Introduction"),
        help_text=_("Short intro video for profile")
    )

    # Account Metadata
    is_verified = models.BooleanField(default=False, verbose_name=_("Fully Verified"))
    email_verified = models.BooleanField(default=False, verbose_name=_("Email Verified"))
    phone_verified = models.BooleanField(default=False, verbose_name=_("Phone Verified"))
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    verification_token_expiry = models.DateTimeField(blank=True, null=True, help_text=_("Expiration for verification token"))
    date_joined = models.DateTimeField(default=timezone.now, verbose_name=_("Date Joined"))
    last_login = models.DateTimeField(blank=True, null=True, verbose_name=_("Last Login"))
    last_active = models.DateTimeField(blank=True, null=True, verbose_name=_("Last Activity"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    is_staff = models.BooleanField(default=False, verbose_name=_("Staff"))
    is_superuser = models.BooleanField(default=False, verbose_name=_("Superuser"))
    account_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'), ('suspended', 'Suspended'), ('banned', 'Banned'),
            ('pending', 'Pending'), ('under_review', 'Under Review'), ('deleted', 'Soft Deleted')
        ],
        default='pending',
        verbose_name=_("Account Status")
    )
    status_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_("Status Reason"),
        help_text=_("e.g., 'Suspended for policy violation'")
    )
    deactivation_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Deactivation Date"))
    reactivation_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Reactivation Date"))
    deactivation_reason = models.TextField(blank=True, null=True, verbose_name=_("Deactivation Reason"))

    # User Roles & Permissions
    USER_ROLES = (
        ('buyer', 'Buyer'), ('seller', 'Seller'), ('agent', 'Real Estate Agent'),
        ('landlord', 'Landlord'), ('tenant', 'Tenant'), ('developer', 'Developer'),
        ('broker', 'Broker'), ('inspector', 'Inspector'), ('appraiser', 'Appraiser'),
        ('admin', 'Administrator'), ('moderator', 'Moderator'), ('guest', 'Guest'),
        ('partner', 'Business Partner')
    )
    user_role = models.CharField(
        max_length=20,
        choices=USER_ROLES,
        default='buyer',
        verbose_name=_("User Role")
    )
    custom_permissions = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Custom Permissions"),
        help_text=_("e.g., {'can_view_reports': True}")
    )

    # Enhanced Geospatial Fields (Future-Proofed)
    primary_location_latitude = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Primary Location Latitude"),
        help_text=_("Latitude of user's primary location")
    )
    primary_location_longitude = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Primary Location Longitude"),
        help_text=_("Longitude of user's primary location")
    )
    preferred_search_area = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Preferred Search Area"),
        help_text=_("e.g., [{'lat': 40.7128, 'lon': -74.0060}, ...]")
    )
    search_radius = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0.1), MaxValueValidator(1000)],
        verbose_name=_("Search Radius (km)"),
        help_text=_("Default radius for map-based searches")
    )
    last_map_view_center_latitude = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Last Map View Center Latitude")
    )
    last_map_view_center_longitude = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Last Map View Center Longitude")
    )
    last_map_zoom_level = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name=_("Last Map Zoom Level"),
        help_text=_("Zoom level from 1 (world) to 20 (street)")
    )
    map_provider_preference = models.CharField(
        max_length=20,
        choices=[('google', 'Google Maps'), ('openstreet', 'OpenStreetMap'), ('mapbox', 'Mapbox'), ('bing', 'Bing Maps')],
        default='google',
        verbose_name=_("Map Provider Preference")
    )
    map_style = models.CharField(
        max_length=20,
        choices=[('roadmap', 'Roadmap'), ('satellite', 'Satellite'), ('hybrid', 'Hybrid'), ('terrain', 'Terrain'), ('custom', 'Custom')],
        default='roadmap',
        verbose_name=_("Map Style")
    )
    custom_map_style = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Custom Map Style"),
        help_text=_("e.g., {'elementType': 'geometry', 'stylers': [{'color': '#f5f5f5'}]}")
    )
    geofence_alerts = models.BooleanField(
        default=False,
        verbose_name=_("Geofence Alerts"),
        help_text=_("Notify user when entering/leaving preferred areas")
    )
    heatmap_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Heatmap Enabled"),
        help_text=_("Enable heatmap visualization for property density")
    )
    heatmap_intensity = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0.1), MaxValueValidator(10)],
        verbose_name=_("Heatmap Intensity"),
        help_text=_("Intensity factor for heatmap rendering")
    )
    clustering_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Marker Clustering Enabled"),
        help_text=_("Cluster map markers for better visibility")
    )
    directions_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Directions Enabled"),
        help_text=_("Allow direction calculations to/from this location")
    )
    default_map_overlays = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Default Map Overlays"),
        help_text=_("e.g., {'overlays': ['traffic', 'transit', 'bike']}")
    )
    map_interaction_history_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Map Interaction History Enabled"),
        help_text=_("Track user map interactions for analytics")
    )

    # Real Estate Preferences
    preferred_locations = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Preferred Locations"),
        help_text=_("e.g., {'cities': ['NYC'], 'coordinates': [{'lat': 40.7128, 'lon': -74.0060}]}")
    )
    min_price = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Minimum Price")
    )
    max_price = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Maximum Price")
    )
    min_bedrooms = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Min Bedrooms"))
    max_bedrooms = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Max Bedrooms"))
    min_bathrooms = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Min Bathrooms"))
    max_bathrooms = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Max Bathrooms"))
    min_square_feet = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Min Square Feet"))
    max_square_feet = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Max Square Feet"))
    min_lot_size = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True,
        verbose_name=_("Min Lot Size (acres)")
    )
    max_lot_size = models.DecimalField(
        max_digits=15, decimal_places=2, blank=True, null=True,
        verbose_name=_("Max Lot Size (acres)")
    )
    property_types = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Property Types"),
        help_text=_("e.g., {'types': ['apartment', 'house', 'condo', 'townhouse']}")
    )
    preferred_amenities = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Preferred Amenities"),
        help_text=_("e.g., {'amenities': ['pool', 'gym', 'doorman', 'parking']}")
    )
    building_styles = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Building Styles"),
        help_text=_("e.g., {'styles': ['modern', 'victorian', 'colonial']}")
    )
    min_year_built = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1800), MaxValueValidator(timezone.now().year)],
        verbose_name=_("Min Year Built")
    )
    max_year_built = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1800), MaxValueValidator(timezone.now().year)],
        verbose_name=_("Max Year Built")
    )
    move_in_date_min = models.DateField(blank=True, null=True, verbose_name=_("Earliest Move-In Date"))
    move_in_date_max = models.DateField(blank=True, null=True, verbose_name=_("Latest Move-In Date"))
    lease_term = models.CharField(
        max_length=20,
        choices=[
            ('short', 'Short-term (<6 months)'), ('long', 'Long-term (1+ year)'),
            ('month', 'Month-to-month'), ('flexible', 'Flexible')
        ],
        blank=True, null=True,
        verbose_name=_("Lease Term")
    )
    pet_policy = models.CharField(
        max_length=20,
        choices=[('yes', 'Pets Allowed'), ('no', 'No Pets'), ('negotiable', 'Negotiable')],
        blank=True, null=True,
        verbose_name=_("Pet Policy Preference")
    )
    accessibility_needs = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Accessibility Needs"),
        help_text=_("e.g., {'needs': ['wheelchair_access', 'elevator']}")
    )
    proximity_to = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Proximity Points"),
        help_text=_("e.g., [{'lat': 40.7128, 'lon': -74.0060}, ...]")
    )
    max_distance_to_proximity = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0.1)],
        verbose_name=_("Max Distance to Proximity (km)"),
        help_text=_("Max distance from proximity points")
    )

    # Financial & Verification Data (No Encryption)
    annual_income = models.DecimalField(
        max_digits=15, decimal_places=2,
        blank=True, null=True,
        verbose_name=_("Annual Income")
    )
    monthly_income = models.DecimalField(
        max_digits=15, decimal_places=2,
        blank=True, null=True,
        verbose_name=_("Monthly Income")
    )
    credit_score = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(300), MaxValueValidator(850)],
        verbose_name=_("Credit Score")
    )
    credit_score_source = models.CharField(
        max_length=50,
        blank=True, null=True,
        choices=[('experian', 'Experian'), ('equifax', 'Equifax'), ('transunion', 'TransUnion'), ('self', 'Self-Reported')],
        verbose_name=_("Credit Score Source")
    )
    budget_range = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Budget Range"),
        help_text=_("e.g., {'monthly_min': 1000, 'monthly_max': 5000}")
    )
    employment_status = models.CharField(
        max_length=20,
        choices=[
            ('employed', 'Employed'), ('self_employed', 'Self-Employed'), ('unemployed', 'Unemployed'),
            ('retired', 'Retired'), ('student', 'Student')
        ],
        blank=True, null=True,
        verbose_name=_("Employment Status")
    )
    employer_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Employer Name"))
    job_title = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Job Title"))
    years_employed = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MaxValueValidator(100)],
        verbose_name=_("Years Employed")
    )

    # Notification Preferences
    email_notifications = models.BooleanField(default=True, verbose_name=_("Email Notifications"))
    sms_notifications = models.BooleanField(default=False, verbose_name=_("SMS Notifications"))
    push_notifications = models.BooleanField(default=True, verbose_name=_("Push Notifications"))
    whatsapp_notifications = models.BooleanField(default=False, verbose_name=_("WhatsApp Notifications"))
    notification_frequency = models.CharField(
        max_length=20,
        choices=[('immediate', 'Immediate'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        default='immediate',
        verbose_name=_("Notification Frequency")
    )
    muted_notification_types = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Muted Notification Types"),
        help_text=_("e.g., {'listing_updates': True, 'system_alerts': False}")
    )
    notification_sound = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=_("Notification Sound"),
        help_text=_("Custom sound ID for app notifications")
    )

    # Security & Access Control
    two_factor_enabled = models.BooleanField(default=False, verbose_name=_("Two-Factor Authentication"))
    two_factor_method = models.CharField(
        max_length=20,
        choices=[('sms', 'SMS'), ('app', 'Authenticator App'), ('email', 'Email'), ('phone_call', 'Phone Call')],
        blank=True, null=True,
        verbose_name=_("2FA Method")
    )
    two_factor_backup_codes = models.JSONField(
        blank=True, null=True,
        verbose_name=_("2FA Backup Codes"),
        help_text=_("e.g., {'codes': ['abc123', 'xyz789']}")
    )
    last_password_change = models.DateTimeField(blank=True, null=True, verbose_name=_("Last Password Change"))
    password_expiry_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_("Password Expiry Date"),
        help_text=_("Force password change after this date")
    )
    failed_login_attempts = models.PositiveIntegerField(default=0, verbose_name=_("Failed Login Attempts"))
    account_locked_until = models.DateTimeField(blank=True, null=True, verbose_name=_("Account Locked Until"))
    trusted_devices = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Trusted Devices"),
        help_text=_("e.g., {'devices': [{'id': 'device1', 'last_used': '2025-03-24'}]}")
    )
    privacy_level = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'), ('friends', 'Friends Only'), ('agents', 'Agents Only'),
            ('private', 'Private'), ('custom', 'Custom')
        ],
        default='private',
        verbose_name=_("Privacy Level")
    )
    custom_privacy_settings = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Custom Privacy Settings"),
        help_text=_("e.g., {'profile_visible_to': ['friends', 'agents']}")
    )

    # Social Media & External Integrations
    facebook_id = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name=_("Facebook ID"))
    google_id = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name=_("Google ID"))
    linkedin_id = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name=_("LinkedIn ID"))
    twitter_handle = models.CharField(
        max_length=15,
        blank=True, null=True,
        validators=[RegexValidator(r'^@?(\w){1,15}$')],
        verbose_name=_("Twitter Handle")
    )
    instagram_handle = models.CharField(
        max_length=30,
        blank=True, null=True,
        validators=[RegexValidator(r'^@?(\w){1,30}$')],
        verbose_name=_("Instagram Handle")
    )
    social_connections = models.ManyToManyField(
        'self',
        symmetrical=True,
        blank=True,
        through='UserConnection',
        verbose_name=_("Social Connections")
    )
    external_api_keys = models.JSONField(
        blank=True, null=True,
        verbose_name=_("External API Keys"),
        help_text=_("e.g., {'google_maps': 'xyz123'}")
    )

    # Legal & Compliance
    terms_accepted = models.BooleanField(default=False, verbose_name=_("Terms Accepted"))
    terms_version = models.CharField(
        max_length=20,
        blank=True, null=True,
        verbose_name=_("Terms Version"),
        help_text=_("e.g., 'v1.2.3'")
    )
    terms_accepted_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Terms Accepted Date"))
    gdpr_consent = models.BooleanField(default=False, verbose_name=_("GDPR Consent"))
    gdpr_consent_date = models.DateTimeField(blank=True, null=True, verbose_name=_("GDPR Consent Date"))
    ccpa_opt_out = models.BooleanField(
        default=False,
        verbose_name=_("CCPA Opt-Out"),
        help_text=_("Opt-out of data selling (California)")
    )
    data_sharing_opt_in = models.BooleanField(default=False, verbose_name=_("Data Sharing Opt-In"))
    marketing_consent = models.BooleanField(default=False, verbose_name=_("Marketing Consent"))
    consent_history = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Consent History"),
        help_text=_("e.g., {'gdpr': {'date': '2025-03-24', 'version': '1.0'}}")
    )

    # Analytics & Engagement
    profile_views = models.PositiveIntegerField(default=0, verbose_name=_("Profile Views"))
    last_profile_update = models.DateTimeField(blank=True, null=True, verbose_name=_("Last Profile Update"))
    engagement_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Engagement Score"),
        help_text=_("Calculated based on activity")
    )
    referral_code = models.CharField(
        max_length=20,
        unique=True,
        default=lambda: uuid.uuid4().hex[:10],  # Lambda for callable default
        verbose_name=_("Referral Code")
    )
    referred_by = models.ForeignKey(
        'self',
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='referrals',
        verbose_name=_("Referred By")
    )

    # Custom Manager
    objects = CustomUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_role']),
            models.Index(fields=['is_active', 'account_status']),
            models.Index(fields=['last_login']),
            models.Index(fields=['primary_location_latitude', 'primary_location_longitude']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(min_price__lte=models.F('max_price')),
                name='min_price_lte_max_price'
            )
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        parts = [self.title, self.first_name, self.middle_name, self.last_name, self.suffix]
        return " ".join(filter(None, parts)).strip() or self.email

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = uuid.uuid4()
        if self.is_verified:
            self.email_verified = True
            self.phone_verified = True if self.phone_number else False
        super().save(*args, **kwargs)

    def properties_nearby(self, distance_km=5):
        if self.primary_location_latitude and self.primary_location_longitude:
            return UserProperty.objects.filter(
                location_latitude__gte=self.primary_location_latitude - distance_km / 111,
                location_latitude__lte=self.primary_location_latitude + distance_km / 111,
                location_longitude__gte=self.primary_location_longitude - distance_km / 111,
                location_longitude__lte=self.primary_location_longitude + distance_km / 111
            )
        return UserProperty.objects.none()

# User Connection
class UserConnection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connection_from')
    connected_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connection_to')
    connection_type = models.CharField(
        max_length=20,
        choices=[('friend', 'Friend'), ('colleague', 'Colleague'), ('family', 'Family'), ('business', 'Business')],
        default='friend',
        verbose_name=_("Connection Type")
    )
    connected_at = models.DateTimeField(default=timezone.now, verbose_name=_("Connected At"))
    is_mutual = models.BooleanField(default=True, verbose_name=_("Mutual Connection"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'connected_user'], name='unique_user_connection')
        ]
        verbose_name = _("User Connection")
        verbose_name_plural = _("User Connections")

    def __str__(self):
        return f"{self.user.email} -> {self.connected_user.email} ({self.connection_type})"

# User Address
class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(
        max_length=20,
        choices=[
            ('home', 'Home'), ('billing', 'Billing'), ('shipping', 'Shipping'),
            ('work', 'Work'), ('vacation', 'Vacation'), ('temporary', 'Temporary')
        ],
        default='home',
        verbose_name=_("Address Type")
    )
    address_line_1 = models.CharField(max_length=255, verbose_name=_("Address Line 1"))
    address_line_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Address Line 2"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    state = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("State/Province"))
    postal_code = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^[A-Za-z0-9\s\-]+$')],
        verbose_name=_("Postal Code")
    )
    country = CountryField(default='US', verbose_name=_("Country"))
    is_primary = models.BooleanField(default=False, verbose_name=_("Primary Address"))
    latitude = models.FloatField(blank=True, null=True, verbose_name=_("Latitude"))
    longitude = models.FloatField(blank=True, null=True, verbose_name=_("Longitude"))
    elevation = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Elevation (meters)"),
        help_text=_("Height above sea level")
    )
    timezone = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=_("Timezone"),
        help_text=_("e.g., 'America/New_York'")
    )
    delivery_instructions = models.TextField(
        blank=True, null=True,
        verbose_name=_("Delivery Instructions"),
        help_text=_("e.g., 'Leave at front desk'")
    )
    address_verified = models.BooleanField(default=False, verbose_name=_("Address Verified"))
    verification_method = models.CharField(
        max_length=50,
        blank=True, null=True,
        choices=[('manual', 'Manual'), ('api', 'API'), ('user', 'User-Confirmed')],
        verbose_name=_("Verification Method")
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'address_type', 'is_primary'], name='unique_user_address_type_primary')
        ]
        verbose_name = _("User Address")
        verbose_name_plural = _("User Addresses")
        indexes = [
            models.Index(fields=['user', 'is_primary']),
            models.Index(fields=['country', 'postal_code']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return f"{self.address_line_1}, {self.city}, {self.postal_code} ({self.user.email})"

# Saved Search
class SavedSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100, verbose_name=_("Search Name"))
    search_query = models.JSONField(
        verbose_name=_("Search Query"),
        help_text=_("e.g., {'location': 'NYC', 'min_price': 2000, 'bedrooms': 2, 'amenities': ['pool']}")
    )
    search_area = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Search Area"),
        help_text=_("e.g., [{'lat': 40.7128, 'lon': -74.0060}, ...]")
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    notify_on_match = models.BooleanField(default=True, verbose_name=_("Notify on Match"))
    notification_frequency = models.CharField(
        max_length=20,
        choices=[('instant', 'Instant'), ('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        default='instant',
        verbose_name=_("Notification Frequency")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    priority = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_("Priority"),
        help_text=_("Higher priority searches processed first")
    )
    last_run = models.DateTimeField(blank=True, null=True, verbose_name=_("Last Run"))
    match_count = models.PositiveIntegerField(default=0, verbose_name=_("Match Count"))
    tags = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Tags"),
        help_text=_("e.g., ['urgent', 'nyc', 'rental']")
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Saved Search")
        verbose_name_plural = _("Saved Searches")
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} - {self.user.email}"

# User Activity
class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action_type = models.CharField(
        max_length=50,
        choices=[
            ('login', 'Login'), ('logout', 'Logout'), ('view_listing', 'View Listing'),
            ('save_search', 'Save Search'), ('profile_update', 'Profile Update'),
            ('password_change', 'Password Change'), ('message_sent', 'Message Sent'),
            ('listing_favorited', 'Listing Favorited'), ('review_posted', 'Review Posted'),
            ('map_interaction', 'Map Interaction')
        ],
        verbose_name=_("Action Type")
    )
    action_detail = models.TextField(verbose_name=_("Action Detail"), help_text=_("e.g., 'Viewed listing #123'"))
    timestamp = models.DateTimeField(default=timezone.now, verbose_name=_("Timestamp"))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP Address"))
    device_info = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name=_("Device Info"),
        help_text=_("e.g., 'Chrome 120.0 on Windows 11'")
    )
    session_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Session ID"))
    user_agent = models.TextField(blank=True, null=True, verbose_name=_("User Agent"))
    referrer_url = models.URLField(blank=True, null=True, verbose_name=_("Referrer URL"))
    duration = models.DurationField(
        blank=True, null=True,
        verbose_name=_("Duration"),
        help_text=_("Time spent on action, if applicable")
    )
    location_latitude = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Action Location Latitude")
    )
    location_longitude = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Action Location Longitude")
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("User Activity")
        verbose_name_plural = _("User Activities")
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type']),
            models.Index(fields=['location_latitude', 'location_longitude']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.action_type} - {self.timestamp}"

# User Notification
class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField(verbose_name=_("Message"))
    notification_type = models.CharField(
        max_length=50,
        choices=[
            ('listing', 'New Listing'), ('update', 'Account Update'), ('system', 'System Alert'),
            ('message', 'Message'), ('offer', 'Offer Received'), ('payment', 'Payment Confirmation'),
            ('review', 'New Review'), ('connection', 'New Connection'), ('geofence', 'Geofence Alert')
        ],
        default='listing',
        verbose_name=_("Notification Type")
    )
    priority = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],
        default='medium',
        verbose_name=_("Priority")
    )
    is_read = models.BooleanField(default=False, verbose_name=_("Read"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Expires At"))
    link = models.URLField(
        blank=True, null=True,
        validators=[URLValidator()],
        verbose_name=_("Link")
    )
    sent_via = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Sent Via"),
        help_text=_("e.g., {'email': True, 'sms': False, 'push': True}")
    )
    delivery_status = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Delivery Status"),
        help_text=_("e.g., {'email': 'delivered', 'sms': 'failed'}")
    )
    read_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Read At"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("User Notification")
        verbose_name_plural = _("User Notifications")
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.notification_type} - {self.message[:50]}"

# Agent Profile
class AgentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    license_number = models.CharField(max_length=50, unique=True, verbose_name=_("License Number"))
    license_state = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("License State"))
    license_issue_date = models.DateField(blank=True, null=True, verbose_name=_("License Issue Date"))
    license_expiry_date = models.DateField(blank=True, null=True, verbose_name=_("License Expiry Date"))
    agency_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Agency Name"))
    agency_address = models.ForeignKey(
        'UserAddress',
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='agent_agencies',
        verbose_name=_("Agency Address")
    )
    agency_website = models.URLField(blank=True, null=True, verbose_name=_("Agency Website"))
    years_experience = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name=_("Years of Experience")
    )
    bio = models.TextField(blank=True, null=True, verbose_name=_("Biography"))
    specialties = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Specialties"),
        help_text=_("e.g., {'specialties': ['luxury homes', 'commercial', 'rentals']}")
    )
    languages_spoken = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Languages Spoken"),
        help_text=_("e.g., ['English', 'Spanish', 'French']")
    )
    certifications = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Certifications"),
        help_text=_("e.g., {'certs': ['CRS', 'ABR']}")
    )
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name=_("Rating")
    )
    review_count = models.PositiveIntegerField(default=0, verbose_name=_("Review Count"))
    verified_agent = models.BooleanField(default=False, verbose_name=_("Verified Agent"))
    profile_views = models.PositiveIntegerField(default=0, verbose_name=_("Profile Views"))
    listings_managed = models.PositiveIntegerField(default=0, verbose_name=_("Listings Managed"))
    successful_transactions = models.PositiveIntegerField(default=0, verbose_name=_("Successful Transactions"))
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True, null=True,
        verbose_name=_("Commission Rate (%)")
    )
    availability_schedule = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Availability Schedule"),
        help_text=_("e.g., {'monday': '9am-5pm'}")
    )
    service_area = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Service Area"),
        help_text=_("e.g., [{'lat': 40.7128, 'lon': -74.0060}, ...]")
    )
    service_area_center_latitude = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Service Area Center Latitude")
    )
    service_area_center_longitude = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Service Area Center Longitude")
    )
    service_area_radius = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0.1)],
        verbose_name=_("Service Area Radius (km)"),
        help_text=_("Optional radius if area is circular")
    )

    class Meta:
        verbose_name = _("Agent Profile")
        verbose_name_plural = _("Agent Profiles")
        indexes = [
            models.Index(fields=['service_area_center_latitude', 'service_area_center_longitude']),
        ]

    def __str__(self):
        return f"Agent: {self.user.email}"

# User Property
class UserProperty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    property_type = models.CharField(
        max_length=20,
        choices=[('owned', 'Owned'), ('saved', 'Saved'), ('managed', 'Managed by Agent')],
        default='saved',
        verbose_name=_("Property Type")
    )
    title = models.CharField(max_length=200, verbose_name=_("Property Title"))
    location_latitude = models.FloatField(verbose_name=_("Property Location Latitude"))
    location_longitude = models.FloatField(verbose_name=_("Property Location Longitude"))
    address = models.CharField(max_length=255, verbose_name=_("Address"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    state = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("State"))
    postal_code = models.CharField(max_length=20, verbose_name=_("Postal Code"))
    country = CountryField(default='US', verbose_name=_("Country"))
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("Price"))
    bedrooms = models.PositiveIntegerField(default=1, verbose_name=_("Bedrooms"))
    bathrooms = models.PositiveIntegerField(default=1, verbose_name=_("Bathrooms"))
    square_feet = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Square Feet"))
    lot_size = models.DecimalField(
        max_digits=15, decimal_places=2,
        blank=True, null=True,
        verbose_name=_("Lot Size (acres)")
    )
    year_built = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1800), MaxValueValidator(timezone.now().year)],
        verbose_name=_("Year Built")
    )
    property_category = models.CharField(
        max_length=20,
        choices=[('apartment', 'Apartment'), ('house', 'House'), ('condo', 'Condo'), ('townhouse', 'Townhouse')],
        default='apartment',
        verbose_name=_("Property Category")
    )
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    images = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Images"),
        help_text=_("e.g., {'urls': ['/media/prop1.jpg', '/media/prop2.jpg']}")
    )
    geofence = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Property Geofence"),
        help_text=_("e.g., [{'lat': 40.7128, 'lon': -74.0060}, ...]")
    )
    elevation = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Elevation (meters)"),
        help_text=_("Height above sea level")
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    visibility = models.CharField(
        max_length=20,
        choices=[('public', 'Public'), ('private', 'Private'), ('agents', 'Agents Only')],
        default='public',
        verbose_name=_("Visibility")
    )
    heatmap_weight = models.FloatField(
        blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Heatmap Weight"),
        help_text=_("Weight for heatmap visualization (e.g., based on price or popularity)")
    )
    marker_icon = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("Marker Icon"),
        help_text=_("Custom marker icon URL or ID")
    )

    class Meta:
        verbose_name = _("User Property")
        verbose_name_plural = _("User Properties")
        indexes = [
            models.Index(fields=['user', 'property_type']),
            models.Index(fields=['location_latitude', 'location_longitude']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    def distance_to(self, other_latitude, other_longitude):
        if self.location_latitude and self.location_longitude and other_latitude and other_longitude:
            from math import sqrt
            lat_diff = self.location_latitude - other_latitude
            lon_diff = self.location_longitude - other_longitude
            return sqrt(lat_diff**2 + lon_diff**2) * 111  # Rough km conversion
        return None

# Saved Map View
class SavedMapView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_map_views')
    name = models.CharField(max_length=100, verbose_name=_("Map View Name"))
    center_latitude = models.FloatField(verbose_name=_("Map Center Latitude"))
    center_longitude = models.FloatField(verbose_name=_("Map Center Longitude"))
    zoom_level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        default=12,
        verbose_name=_("Zoom Level")
    )
    boundary = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Map Boundary"),
        help_text=_("e.g., [{'lat': 40.7128, 'lon': -74.0060}, ...]")
    )
    map_style = models.CharField(
        max_length=20,
        choices=[('roadmap', 'Roadmap'), ('satellite', 'Satellite'), ('hybrid', 'Hybrid'), ('terrain', 'Terrain'), ('custom', 'Custom')],
        default='roadmap',
        verbose_name=_("Map Style")
    )
    custom_map_style = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Custom Map Style"),
        help_text=_("e.g., {'elementType': 'geometry', 'stylers': [{'color': '#f5f5f5'}]}")
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))
    last_used = models.DateTimeField(blank=True, null=True, verbose_name=_("Last Used"))
    is_default = models.BooleanField(default=False, verbose_name=_("Default View"))
    overlays = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Overlays"),
        help_text=_("e.g., {'overlays': ['traffic', 'transit', 'bike']}")
    )
    heatmap_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Heatmap Enabled"),
        help_text=_("Show heatmap for this view")
    )
    clustering_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Clustering Enabled"),
        help_text=_("Enable marker clustering")
    )
    directions_to = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Directions Destination"),
        help_text=_("e.g., {'lat': 40.7128, 'lon': -74.0060}")
    )

    class Meta:
        verbose_name = _("Saved Map View")
        verbose_name_plural = _("Saved Map Views")
        indexes = [
            models.Index(fields=['user', 'is_default']),
            models.Index(fields=['center_latitude', 'center_longitude']),
        ]

    def __str__(self):
        return f"{self.name} - {self.user.email}"

# User Map Interaction
class UserMapInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='map_interactions')
    interaction_type = models.CharField(
        max_length=20,
        choices=[
            ('pan', 'Pan'), ('zoom', 'Zoom'), ('click', 'Click'), ('search', 'Search'),
            ('marker_add', 'Add Marker'), ('marker_remove', 'Remove Marker'),
            ('overlay_toggle', 'Toggle Overlay'), ('geofence_trigger', 'Geofence Trigger')
        ],
        verbose_name=_("Interaction Type")
    )
    location_latitude = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Interaction Location Latitude")
    )
    location_longitude = models.FloatField(
        blank=True, null=True,
        verbose_name=_("Interaction Location Longitude")
    )
    zoom_level = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name=_("Zoom Level")
    )
    timestamp = models.DateTimeField(default=timezone.now, verbose_name=_("Timestamp"))
    details = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Details"),
        help_text=_("e.g., {'new_center': {'lat': 40.7128, 'lon': -74.0060}, 'overlay': 'traffic'}")
    )

    class Meta:
        verbose_name = _("User Map Interaction")
        verbose_name_plural = _("User Map Interactions")
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['interaction_type']),
            models.Index(fields=['location_latitude', 'location_longitude']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.interaction_type} - {self.timestamp}"

# User Review
class UserReview(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Rating")
    )
    comment = models.TextField(blank=True, null=True, verbose_name=_("Comment"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    is_anonymous = models.BooleanField(default=False, verbose_name=_("Anonymous"))
    helpful_votes = models.PositiveIntegerField(default=0, verbose_name=_("Helpful Votes"))
    flagged = models.BooleanField(default=False, verbose_name=_("Flagged"))
    flag_reason = models.TextField(blank=True, null=True, verbose_name=_("Flag Reason"))
    response = models.TextField(blank=True, null=True, verbose_name=_("Response from Reviewed User"))
    response_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Response Date"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['reviewer', 'reviewed_user'], name='unique_user_review')
        ]
        ordering = ['-created_at']
        verbose_name = _("User Review")
        verbose_name_plural = _("User Reviews")

    def __str__(self):
        return f"{self.reviewer.email} -> {self.reviewed_user.email}: {self.rating}/5"

# User Document
class UserDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(
        max_length=50,
        choices=[
            ('id', 'Government ID'), ('license', 'Real Estate License'), ('passport', 'Passport'),
            ('proof_of_income', 'Proof of Income'), ('tax_return', 'Tax Return'),
            ('utility_bill', 'Utility Bill'), ('other', 'Other')
        ],
        verbose_name=_("Document Type")
    )
    file = models.FileField(upload_to='users/documents/%Y/%m/%d/', verbose_name=_("File"))
    uploaded_at = models.DateTimeField(default=timezone.now, verbose_name=_("Uploaded At"))
    verified = models.BooleanField(default=False, verbose_name=_("Verified"))
    verification_method = models.CharField(
        max_length=50,
        blank=True, null=True,
        choices=[('manual', 'Manual'), ('api', 'API'), ('third_party', 'Third-Party Service')],
        verbose_name=_("Verification Method")
    )
    verification_notes = models.TextField(blank=True, null=True, verbose_name=_("Verification Notes"))
    expiry_date = models.DateField(blank=True, null=True, verbose_name=_("Expiry Date"))
    document_number = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=_("Document Number"),
        help_text=_("e.g., Passport number")
    )
    issuing_authority = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("Issuing Authority")
    )

    class Meta:
        verbose_name = _("User Document")
        verbose_name_plural = _("User Documents")

    def __str__(self):
        return f"{self.user.email} - {self.document_type}"

# User Subscription
class UserSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan_name = models.CharField(max_length=100, verbose_name=_("Plan Name"))
    plan_description = models.TextField(blank=True, null=True, verbose_name=_("Plan Description"))
    start_date = models.DateTimeField(default=timezone.now, verbose_name=_("Start Date"))
    end_date = models.DateTimeField(blank=True, null=True, verbose_name=_("End Date"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    billing_cycle = models.CharField(
        max_length=20,
        choices=[('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')],
        default='monthly',
        verbose_name=_("Billing Cycle")
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('credit_card', 'Credit Card'), ('paypal', 'PayPal'), ('bank_transfer', 'Bank Transfer'),
            ('crypto', 'Cryptocurrency'), ('invoice', 'Invoice')
        ],
        blank=True, null=True,
        verbose_name=_("Payment Method")
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name=_("Currency"),
        help_text=_("ISO 4217 code, e.g., 'USD', 'EUR'")
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_("Transaction ID")
    )
    auto_renew = models.BooleanField(default=True, verbose_name=_("Auto-Renew"))
    cancellation_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Cancellation Date"))
    cancellation_reason = models.TextField(blank=True, null=True, verbose_name=_("Cancellation Reason"))

    class Meta:
        verbose_name = _("User Subscription")
        verbose_name_plural = _("User Subscriptions")

    def __str__(self):
        return f"{self.user.email} - {self.plan_name} ({self.start_date})"

# User Referral
class UserReferral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_sent')
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_received')
    referral_code = models.CharField(
        max_length=20,
        unique=True,
        default=lambda: uuid.uuid4().hex[:10],
        verbose_name=_("Referral Code")
    )
    referred_at = models.DateTimeField(default=timezone.now, verbose_name=_("Referred At"))
    reward_earned = models.BooleanField(default=False, verbose_name=_("Reward Earned"))
    reward_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=True, null=True,
        verbose_name=_("Reward Amount")
    )
    reward_type = models.CharField(
        max_length=20,
        choices=[('cash', 'Cash'), ('credit', 'Platform Credit'), ('discount', 'Discount')],
        blank=True, null=True,
        verbose_name=_("Reward Type")
    )
    reward_issued_at = models.DateTimeField(blank=True, null=True, verbose_name=_("Reward Issued At"))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['referrer', 'referred_user'], name='unique_user_referral')
        ]
        verbose_name = _("User Referral")
        verbose_name_plural = _("User Referrals")

    def __str__(self):
        return f"{self.referrer.email} referred {self.referred_user.email}"

# User Audit Log
class UserAuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    changed_by = models.ForeignKey(
        User,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='changes_made',
        verbose_name=_("Changed By")
    )
    change_type = models.CharField(
        max_length=20,
        choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete')],
        verbose_name=_("Change Type")
    )
    field_name = models.CharField(max_length=100, verbose_name=_("Field Name"))
    old_value = models.TextField(blank=True, null=True, verbose_name=_("Old Value"))
    new_value = models.TextField(blank=True, null=True, verbose_name=_("New Value"))
    timestamp = models.DateTimeField(default=timezone.now, verbose_name=_("Timestamp"))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("IP Address"))

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _("User Audit Log")
        verbose_name_plural = _("User Audit Logs")

    def __str__(self):
        return f"{self.user.email} - {self.change_type} - {self.field_name} - {self.timestamp}"

# User Preference
class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(
        max_length=20,
        choices=[('light', 'Light'), ('dark', 'Dark'), ('system', 'System Default')],
        default='light',
        verbose_name=_("Theme")
    )
    language = models.CharField(
        max_length=10,
        default='en',
        verbose_name=_("Language"),
        help_text=_("e.g., 'en', 'es', 'fr'")
    )
    date_format = models.CharField(
        max_length=20,
        choices=[('mm/dd/yyyy', 'MM/DD/YYYY'), ('dd/mm/yyyy', 'DD/MM/YYYY'), ('yyyy-mm-dd', 'YYYY-MM-DD')],
        default='mm/dd/yyyy',
        verbose_name=_("Date Format")
    )
    time_format = models.CharField(
        max_length=20,
        choices=[('12h', '12-Hour'), ('24h', '24-Hour')],
        default='12h',
        verbose_name=_("Time Format")
    )
    default_search_radius = models.PositiveIntegerField(
        default=10,
        validators=[MaxValueValidator(1000)],
        verbose_name=_("Default Search Radius (miles)")
    )
    map_provider = models.CharField(
        max_length=20,
        choices=[('google', 'Google Maps'), ('openstreet', 'OpenStreetMap'), ('mapbox', 'Mapbox'), ('bing', 'Bing Maps')],
        default='google',
        verbose_name=_("Map Provider")
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name=_("Preferred Currency")
    )

    class Meta:
        verbose_name = _("User Preference")
        verbose_name_plural = _("User Preferences")

    def __str__(self):
        return f"Preferences for {self.user.email}"