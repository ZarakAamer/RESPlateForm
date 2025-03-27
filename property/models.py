# -------- Property App Models --------- #
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid


# --- Property Model (Buildings/Units) ---
class Property(models.Model):
    property_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building_name = models.CharField(max_length=255, blank=True, verbose_name=_("Building Name"))
    property_type = models.CharField(
        max_length=50,
        choices=[
            ('condo', 'Condo'), ('coop', 'Co-op'), ('townhouse', 'Townhouse'),
            ('single_family', 'Single Family'), ('multi_family', 'Multi-Family'),
            ('rental', 'Rental'), ('commercial', 'Commercial'), ('mixed_use', 'Mixed Use'),
            ('land', 'Land'), ('industrial', 'Industrial'), ('tiny_home', 'Tiny Home'),
            ('modular', 'Modular'), ('prefab', 'Prefabricated')
        ],
        verbose_name=_("Property Type")
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'), ('pending', 'Pending'), ('sold', 'Sold'),
            ('off_market', 'Off Market'), ('under_contract', 'Under Contract'),
            ('expired', 'Expired'), ('withdrawn', 'Withdrawn')
        ],
        default='active',
        verbose_name=_("Status")
    )
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, related_name='properties')
    total_units = models.PositiveIntegerField(default=1, verbose_name=_("Total Units"))
    year_built = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1800), MaxValueValidator(timezone.now().year + 50)],
        verbose_name=_("Year Built")
    )
    year_renovated = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1800), MaxValueValidator(timezone.now().year + 50)],
        verbose_name=_("Year Renovated")
    )
    lot_size_sqft = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Lot Size (sqft)"))
    building_size_sqft = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Building Size (sqft)"))
    floors = models.PositiveIntegerField(default=1, verbose_name=_("Number of Floors"))
    zoning_type = models.CharField(max_length=50, blank=True, verbose_name=_("Zoning Type"))
    construction_status = models.CharField(
        max_length=20,
        choices=[('completed', 'Completed'), ('under_construction', 'Under Construction'), ('planned', 'Planned')],
        default='completed',
        verbose_name=_("Construction Status")
    )
    energy_efficiency_rating = models.CharField(
        max_length=10,
        blank=True,
        choices=[('A+', 'A+'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F')],
        verbose_name=_("Energy Efficiency Rating")
    )
    smart_home_enabled = models.BooleanField(default=False, verbose_name=_("Smart Home Enabled"))
    solar_panels = models.BooleanField(default=False, verbose_name=_("Solar Panels Installed"))
    green_certification = models.CharField(max_length=50, blank=True, verbose_name=_("Green Certification"))
    historical_status = models.BooleanField(default=False, verbose_name=_("Historical Property"))
    virtual_tour_3d_url = models.URLField(blank=True, verbose_name=_("3D Virtual Tour URL"))
    ar_view_enabled = models.BooleanField(default=False, verbose_name=_("Augmented Reality View Enabled"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Views Count"))
    favorites_count = models.PositiveIntegerField(default=0, verbose_name=_("Favorites Count"))

    class Meta:
        verbose_name = _("Property")
        verbose_name_plural = _("Properties")
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['property_type']),
        ]

    def __str__(self):
        return self.building_name or f"Property {self.property_id}"


# --- Address Model (Property-Specific Addresses) ---
class Address(models.Model):
    address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    street_address = models.CharField(max_length=255, verbose_name=_("Street Address"))
    unit_number = models.CharField(max_length=50, blank=True, verbose_name=_("Unit Number"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    state = models.CharField(max_length=100, verbose_name=_("State"))
    postal_code = models.CharField(max_length=20, verbose_name=_("Postal Code"))
    neighborhood = models.CharField(max_length=100, blank=True, verbose_name=_("Neighborhood"))
    borough = models.CharField(max_length=100, blank=True, verbose_name=_("Borough"))
    county = models.CharField(max_length=100, blank=True, verbose_name=_("County"))
    latitude = models.FloatField(verbose_name=_("Latitude"))
    longitude = models.FloatField(verbose_name=_("Longitude"))
    elevation = models.FloatField(null=True, blank=True, verbose_name=_("Elevation (meters)"))
    walk_score = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MaxValueValidator(100)],
        verbose_name=_("Walk Score")
    )
    transit_score = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MaxValueValidator(100)],
        verbose_name=_("Transit Score")
    )
    bike_score = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MaxValueValidator(100)],
        verbose_name=_("Bike Score")
    )
    noise_level = models.CharField(
        max_length=20,
        choices=[('quiet', 'Quiet'), ('moderate', 'Moderate'), ('noisy', 'Noisy')],
        blank=True,
        verbose_name=_("Noise Level")
    )
    crime_rate = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Crime Rate (per 1000)")
    )
    flood_zone = models.BooleanField(default=False, verbose_name=_("In Flood Zone"))

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['neighborhood']),
        ]

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state}"


# --- Listing Model (For Sale/Rent Listings) ---
class Listing(models.Model):
    listing_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='listings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    listing_type = models.CharField(
        max_length=20,
        choices=[('sale', 'For Sale'), ('rent', 'For Rent'), ('auction', 'Auction'), ('lease_to_own', 'Lease to Own')],
        default='sale',
        verbose_name=_("Listing Type")
    )
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("Price"))
    original_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Original Price"))
    bedrooms = models.PositiveIntegerField(default=0, verbose_name=_("Bedrooms"))
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name=_("Bathrooms"))
    square_footage = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Square Footage"))
    floor = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Floor"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    listed_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Listed Date"))
    contract_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Contract Date"))
    closing_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Closing Date"))
    days_on_market = models.PositiveIntegerField(default=0, verbose_name=_("Days on Market"))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Views Count"))
    unique_visitors = models.PositiveIntegerField(default=0, verbose_name=_("Unique Visitors"))
    inquiries_count = models.PositiveIntegerField(default=0, verbose_name=_("Inquiries Count"))
    is_no_fee = models.BooleanField(default=False, verbose_name=_("No Fee"))
    virtual_tour_url = models.URLField(blank=True, verbose_name=_("Virtual Tour URL"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    pet_policy = models.CharField(
        max_length=20,
        choices=[('allowed', 'Allowed'), ('not_allowed', 'Not Allowed'), ('case_by_case', 'Case by Case')],
        blank=True,
        verbose_name=_("Pet Policy")
    )
    maintenance_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Maintenance Fee"))
    hoa_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("HOA Fee"))
    tax_annual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Annual Tax"))
    rent_controlled = models.BooleanField(default=False, verbose_name=_("Rent Controlled"))
    lease_term_months = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Lease Term (Months)"))
    move_in_date = models.DateField(null=True, blank=True, verbose_name=_("Available Move-In Date"))
    furnished = models.BooleanField(default=False, verbose_name=_("Furnished"))
    parking_spaces = models.PositiveIntegerField(default=0, verbose_name=_("Parking Spaces"))
    parking_type = models.CharField(
        max_length=20,
        choices=[('garage', 'Garage'), ('driveway', 'Driveway'), ('street', 'Street'), ('none', 'None')],
        blank=True,
        verbose_name=_("Parking Type")
    )
    ev_charging_available = models.BooleanField(default=False, verbose_name=_("EV Charging Available"))
    virtual_staging_enabled = models.BooleanField(default=False, verbose_name=_("Virtual Staging Enabled"))
    ar_preview_url = models.URLField(blank=True, verbose_name=_("AR Preview URL"))
    ai_valuation = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("AI-Estimated Value"))
    ai_valuation_confidence = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name=_("AI Valuation Confidence")
    )
    heatmap_weight = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Heatmap Weight")
    )

    class Meta:
        verbose_name = _("Listing")
        verbose_name_plural = _("Listings")
        indexes = [
            models.Index(fields=['is_active', 'listing_type']),
            models.Index(fields=['price']),
        ]

    def save(self, *args, **kwargs):
        if self.contract_date and self.listed_date:
            self.days_on_market = (self.contract_date - self.listed_date).days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.property.building_name} - {self.listing_type} - ${self.price}"


# --- Amenity Model ---
class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))
    category = models.CharField(
        max_length=20,
        choices=[('building', 'Building'), ('unit', 'Unit'), ('community', 'Community')],
        default='building',
        verbose_name=_("Category")
    )
    is_premium = models.BooleanField(default=False, verbose_name=_("Premium Amenity"))

    class Meta:
        verbose_name = _("Amenity")
        verbose_name_plural = _("Amenities")

    def __str__(self):
        return self.name


class ListingAmenity(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='amenities')
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)
    details = models.CharField(max_length=255, blank=True, verbose_name=_("Details"))
    verified = models.BooleanField(default=False, verbose_name=_("Verified"))

    class Meta:
        unique_together = ('listing', 'amenity')
        verbose_name = _("Listing Amenity")
        verbose_name_plural = _("Listing Amenities")

    def __str__(self):
        return f"{self.listing.property.building_name} - {self.amenity.name}"


# --- Listing Photo Model ---
class ListingPhoto(models.Model):
    photo_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='listing_photos/%Y/%m/%d/', verbose_name=_("Image"))
    caption = models.CharField(max_length=255, blank=True, verbose_name=_("Caption"))
    is_primary = models.BooleanField(default=False, verbose_name=_("Is Primary"))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded At"))
    resolution = models.CharField(max_length=20, blank=True, verbose_name=_("Resolution"))
    file_size_kb = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("File Size (KB)"))
    is_360_view = models.BooleanField(default=False, verbose_name=_("360° View"))

    class Meta:
        verbose_name = _("Listing Photo")
        verbose_name_plural = _("Listing Photos")
        indexes = [
            models.Index(fields=['listing', 'is_primary']),
        ]

    def __str__(self):
        return f"Photo for {self.listing.property.building_name}"


# --- Price History Model ---
class PriceHistory(models.Model):
    history_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("Old Price"))
    new_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("New Price"))
    change_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Change Date"))
    reason = models.CharField(max_length=100, blank=True, verbose_name=_("Reason"))
    price_change_percentage = models.FloatField(null=True, blank=True, verbose_name=_("Price Change (%)"))

    class Meta:
        verbose_name = _("Price History")
        verbose_name_plural = _("Price Histories")
        indexes = [
            models.Index(fields=['listing', 'change_date']),
        ]

    def save(self, *args, **kwargs):
        if self.old_price and self.new_price:
            self.price_change_percentage = ((self.new_price - self.old_price) / self.old_price) * 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Price change for {self.listing.property.building_name}"


# --- Market Trend Model ---
class MarketTrend(models.Model):
    trend_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    neighborhood = models.CharField(max_length=100, verbose_name=_("Neighborhood"))
    borough = models.CharField(max_length=100, blank=True, verbose_name=_("Borough"))
    period = models.DateField(verbose_name=_("Period"))
    median_sale_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, verbose_name=_("Median Sale Price"))
    median_rent_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, verbose_name=_("Median Rent Price"))
    inventory_count = models.PositiveIntegerField(default=0, verbose_name=_("Inventory Count"))
    days_on_market_avg = models.PositiveIntegerField(default=0, verbose_name=_("Avg Days on Market"))
    sales_volume = models.DecimalField(max_digits=15, decimal_places=2, default=0.0, verbose_name=_("Sales Volume"))
    price_per_sqft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Price per Sqft"))
    rental_yield = models.FloatField(null=True, blank=True, verbose_name=_("Rental Yield (%)"))
    appreciation_rate = models.FloatField(null=True, blank=True, verbose_name=_("Appreciation Rate (%)"))

    class Meta:
        verbose_name = _("Market Trend")
        verbose_name_plural = _("Market Trends")
        indexes = [
            models.Index(fields=['neighborhood', 'period']),
        ]

    def __str__(self):
        return f"{self.neighborhood} - {self.period}"


# --- Transit Model ---
class Transit(models.Model):
    transit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    transit_type = models.CharField(
        max_length=20,
        choices=[('subway', 'Subway'), ('bus', 'Bus'), ('ferry', 'Ferry'), ('train', 'Train'), ('tram', 'Tram')],
        default='subway',
        verbose_name=_("Transit Type")
    )
    latitude = models.FloatField(verbose_name=_("Latitude"))
    longitude = models.FloatField(verbose_name=_("Longitude"))
    operator = models.CharField(max_length=100, blank=True, verbose_name=_("Operator"))
    schedule_url = models.URLField(blank=True, verbose_name=_("Schedule URL"))

    class Meta:
        verbose_name = _("Transit")
        verbose_name_plural = _("Transits")
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return self.name


class PropertyTransit(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='transit_options')
    transit = models.ForeignKey(Transit, on_delete=models.CASCADE)
    distance_meters = models.FloatField(verbose_name=_("Distance (meters)"))
    walking_time_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Walking Time (minutes)"))

    class Meta:
        unique_together = ('property', 'transit')
        verbose_name = _("Property Transit")
        verbose_name_plural = _("Property Transits")

    def __str__(self):
        return f"{self.property.building_name} - {self.transit.name}"


# --- School Model ---
class School(models.Model):
    school_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    school_type = models.CharField(
        max_length=20,
        choices=[('elementary', 'Elementary'), ('middle', 'Middle'), ('high', 'High'), ('charter', 'Charter'), ('private', 'Private')],
        default='elementary',
        verbose_name=_("School Type")
    )
    latitude = models.FloatField(verbose_name=_("Latitude"))
    longitude = models.FloatField(verbose_name=_("Longitude"))
    rating = models.PositiveIntegerField(
        null=True, blank=True,
        choices=[(i, i) for i in range(1, 11)],
        verbose_name=_("Rating")
    )
    student_count = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Student Count"))
    teacher_student_ratio = models.CharField(max_length=10, blank=True, verbose_name=_("Teacher:Student Ratio"))
    website = models.URLField(blank=True, verbose_name=_("Website"))

    class Meta:
        verbose_name = _("School")
        verbose_name_plural = _("Schools")
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return self.name


class PropertySchool(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='schools')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    distance_meters = models.FloatField(verbose_name=_("Distance (meters)"))
    walking_time_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Walking Time (minutes)"))

    class Meta:
        unique_together = ('property', 'school')
        verbose_name = _("Property School")
        verbose_name_plural = _("Property Schools")

    def __str__(self):
        return f"{self.property.building_name} - {self.school.name}"


# --- Open House Model ---
class OpenHouse(models.Model):
    open_house_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='open_houses')
    start_time = models.DateTimeField(verbose_name=_("Start Time"))
    end_time = models.DateTimeField(verbose_name=_("End Time"))
    registration_required = models.BooleanField(default=False, verbose_name=_("Registration Required"))
    virtual_link = models.URLField(blank=True, verbose_name=_("Virtual Link"))
    attendees_count = models.PositiveIntegerField(default=0, verbose_name=_("Attendees Count"))
    rsvp_deadline = models.DateTimeField(null=True, blank=True, verbose_name=_("RSVP Deadline"))

    class Meta:
        verbose_name = _("Open House")
        verbose_name_plural = _("Open Houses")
        indexes = [
            models.Index(fields=['listing', 'start_time']),
        ]

    def __str__(self):
        return f"Open House for {self.listing.property.building_name}"


# --- Map Cluster Model (For Map Circles with Property Counts) ---
class MapCluster(models.Model):
    cluster_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    center_latitude = models.FloatField(verbose_name=_("Center Latitude"))
    center_longitude = models.FloatField(verbose_name=_("Center Longitude"))
    radius_km = models.FloatField(default=5.0, verbose_name=_("Radius (km)"))
    property_count = models.PositiveIntegerField(default=0, verbose_name=_("Property Count"))
    listing_count = models.PositiveIntegerField(default=0, verbose_name=_("Listing Count"))
    avg_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Average Price"))
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))

    class Meta:
        verbose_name = _("Map Cluster")
        verbose_name_plural = _("Map Clusters")
        indexes = [
            models.Index(fields=['center_latitude', 'center_longitude']),
        ]

    def __str__(self):
        return f"Cluster at ({self.center_latitude}, {self.center_longitude}) - {self.property_count} properties"


# --- Map Overlay Model (Custom Map Features) ---
class MapOverlay(models.Model):
    overlay_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name=_("Overlay Name"))
    overlay_type = models.CharField(
        max_length=20,
        choices=[
            ('traffic', 'Traffic'), ('transit', 'Transit'), ('bike', 'Bike Paths'),
            ('crime', 'Crime Heatmap'), ('schools', 'Schools'), ('amenities', 'Amenities'),
            ('flood', 'Flood Zones'), ('zoning', 'Zoning')
        ],
        verbose_name=_("Overlay Type")
    )
    data_source = models.CharField(max_length=100, blank=True, verbose_name=_("Data Source"))
    overlay_data = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Overlay Data"),
        help_text=_("JSON with coordinates and values")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        verbose_name = _("Map Overlay")
        verbose_name_plural = _("Map Overlays")
        indexes = [
            models.Index(fields=['overlay_type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.overlay_type}"


# --- Property Valuation Model ---
class PropertyValuation(models.Model):
    valuation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='valuations')
    estimated_value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("Estimated Value"))
    valuation_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Valuation Date"))
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name=_("Confidence Score")
    )
    valuation_method = models.CharField(
        max_length=50,
        choices=[('ai', 'AI Model'), ('manual', 'Manual'), ('market', 'Market Comparison')],
        default='ai',
        verbose_name=_("Valuation Method")
    )
    comparable_properties = models.JSONField(
        blank=True, null=True,
        verbose_name=_("Comparable Properties"),
        help_text=_("JSON list of comparable property IDs")
    )

    class Meta:
        verbose_name = _("Property Valuation")
        verbose_name_plural = _("Property Valuations")
        indexes = [
            models.Index(fields=['property', 'valuation_date']),
        ]

    def __str__(self):
        return f"Valuation for {self.property.building_name} - ${self.estimated_value}"


# --- Listing Analytics Model ---
class ListingAnalytics(models.Model):
    analytics_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField(verbose_name=_("Date"))
    views = models.PositiveIntegerField(default=0, verbose_name=_("Views"))
    unique_visitors = models.PositiveIntegerField(default=0, verbose_name=_("Unique Visitors"))
    inquiries = models.PositiveIntegerField(default=0, verbose_name=_("Inquiries"))
    favorites = models.PositiveIntegerField(default=0, verbose_name=_("Favorites"))
    bounce_rate = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Bounce Rate (%)")
    )
    avg_time_spent_seconds = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Avg Time Spent (seconds)"))

    class Meta:
        verbose_name = _("Listing Analytics")
        verbose_name_plural = _("Listing Analytics")
        indexes = [
            models.Index(fields=['listing', 'date']),
        ]

    def __str__(self):
        return f"Analytics for {self.listing.property.building_name} - {self.date}"


# --- Custom Manager for Listings ---
class ListingManager(models.Manager):
    def active_listings(self):
        return self.filter(is_active=True)

    def by_neighborhood(self, neighborhood):
        return self.filter(property__address__neighborhood=neighborhood, is_active=True)

    def price_drops(self):
        return self.filter(price_history__isnull=False, is_active=True).distinct()

    def within_radius(self, latitude, longitude, radius_km=5):
        # Simple distance filter using Haversine approximation
        return self.filter(
            property__address__latitude__gte=latitude - radius_km / 111,
            property__address__latitude__lte=latitude + radius_km / 111,
            property__address__longitude__gte=longitude - radius_km / 111,
            property__address__longitude__lte=longitude + radius_km / 111,
            is_active=True
        )


# Assign Manager to Listing
Listing.objects = ListingManager()