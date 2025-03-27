from rest_framework import serializers
from .models import (
    Property, Address, Listing, Amenity, ListingAmenity, ListingPhoto, PriceHistory,
    MarketTrend, Transit, PropertyTransit, School, PropertySchool, OpenHouse,
    MapCluster, MapOverlay, PropertyValuation, ListingAnalytics
)


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for the Address model."""
    class Meta:
        model = Address
        fields = '__all__'


class PropertySerializer(serializers.ModelSerializer):
    """Serializer for the Property model with nested Address."""
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Property
        fields = '__all__'


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for the Listing model with nested Property."""
    property = PropertySerializer(read_only=True)

    class Meta:
        model = Listing
        fields = '__all__'


class AmenitySerializer(serializers.ModelSerializer):
    """Serializer for the Amenity model."""
    class Meta:
        model = Amenity
        fields = '__all__'


class ListingAmenitySerializer(serializers.ModelSerializer):
    """Serializer for the ListingAmenity model with nested Amenity."""
    amenity = AmenitySerializer(read_only=True)

    class Meta:
        model = ListingAmenity
        fields = '__all__'


class ListingPhotoSerializer(serializers.ModelSerializer):
    """Serializer for the ListingPhoto model."""
    # Optional: Add a computed field for image URL if needed
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ListingPhoto
        fields = '__all__'

    def get_image_url(self, obj):
        """Return the full URL of the image if it exists."""
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url') and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class PriceHistorySerializer(serializers.ModelSerializer):
    """Serializer for the PriceHistory model."""
    class Meta:
        model = PriceHistory
        fields = '__all__'


class MarketTrendSerializer(serializers.ModelSerializer):
    """Serializer for the MarketTrend model."""
    class Meta:
        model = MarketTrend
        fields = '__all__'


class TransitSerializer(serializers.ModelSerializer):
    """Serializer for the Transit model."""
    class Meta:
        model = Transit
        fields = '__all__'


class PropertyTransitSerializer(serializers.ModelSerializer):
    """Serializer for the PropertyTransit model with nested Transit."""
    transit = TransitSerializer(read_only=True)

    class Meta:
        model = PropertyTransit
        fields = '__all__'


class SchoolSerializer(serializers.ModelSerializer):
    """Serializer for the School model."""
    class Meta:
        model = School
        fields = '__all__'


class PropertySchoolSerializer(serializers.ModelSerializer):
    """Serializer for the PropertySchool model with nested School."""
    school = SchoolSerializer(read_only=True)

    class Meta:
        model = PropertySchool
        fields = '__all__'


class OpenHouseSerializer(serializers.ModelSerializer):
    """Serializer for the OpenHouse model."""
    class Meta:
        model = OpenHouse
        fields = '__all__'


class MapClusterSerializer(serializers.ModelSerializer):
    """Serializer for the MapCluster model."""
    class Meta:
        model = MapCluster
        fields = '__all__'


class MapOverlaySerializer(serializers.ModelSerializer):
    """Serializer for the MapOverlay model."""
    class Meta:
        model = MapOverlay
        fields = '__all__'


class PropertyValuationSerializer(serializers.ModelSerializer):
    """Serializer for the PropertyValuation model."""
    class Meta:
        model = PropertyValuation
        fields = '__all__'


class ListingAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for the ListingAnalytics model."""
    class Meta:
        model = ListingAnalytics
        fields = '__all__'