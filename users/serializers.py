from rest_framework import serializers
from typing import Any
from .models import (
    User, UserProperty, UserAddress, SavedMapView, UserActivity,
    UserConnection, SavedSearch, UserNotification, AgentProfile,
    UserReview, UserDocument, UserSubscription, UserReferral,
    UserAuditLog, UserPreference, UserMapInteraction
)

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['user_id', 'email', 'full_name', 'user_role', 'primary_location_latitude', 'primary_location_longitude']
        read_only_fields = ['user_id', 'full_name']

class UserPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProperty
        fields = ['title', 'location_latitude', 'location_longitude', 'price', 'property_type', 'created_at']
        read_only_fields = ['created_at']

class UserAddressSerializer(serializers.ModelSerializer):
    country = serializers.CharField(source='country.code', read_only=True)  # Assuming CountryField usage

    class Meta:
        model = UserAddress
        fields = ['address_type', 'address_line_1', 'city', 'state', 'postal_code', 'country']

class SavedMapViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedMapView
        fields = ['name', 'center_latitude', 'center_longitude', 'zoom_level', 'map_style']
        extra_kwargs = {
            'zoom_level': {'min_value': 1, 'max_value': 20}
        }

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ['action_type', 'action_detail', 'timestamp']
        read_only_fields = ['timestamp']

class UserConnectionSerializer(serializers.ModelSerializer):
    connected_user_email = serializers.EmailField(source='connected_user.email', read_only=True)

    class Meta:
        model = UserConnection
        fields = ['connected_user_email', 'connection_type', 'connected_at']
        read_only_fields = ['connected_user_email', 'connected_at']

class SavedSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        fields = ['name', 'search_query', 'created_at', 'notify_on_match']
        read_only_fields = ['created_at']

class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = ['message', 'notification_type', 'priority', 'created_at', 'is_read']
        read_only_fields = ['created_at']

class AgentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentProfile
        fields = ['license_number', 'agency_name', 'years_experience', 'bio', 'rating']
        extra_kwargs = {
            'rating': {'min_value': 0, 'max_value': 5}
        }

class UserReviewSerializer(serializers.ModelSerializer):
    reviewer_email = serializers.EmailField(source='reviewer.email', read_only=True)
    reviewer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)

    class Meta:
        model = UserReview
        fields = ['reviewer', 'reviewer_email', 'reviewed_user', 'rating', 'comment', 'created_at']
        read_only_fields = ['reviewer_email', 'created_at']
        extra_kwargs = {
            'rating': {'min_value': 1, 'max_value': 5}
        }

class UserDocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)  # Ensure file upload handling

    class Meta:
        model = UserDocument
        fields = ['document_type', 'file', 'uploaded_at', 'verified']
        read_only_fields = ['uploaded_at']

class UserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ['plan_name', 'start_date', 'end_date', 'is_active', 'amount']
        read_only_fields = ['start_date']

class UserReferralSerializer(serializers.ModelSerializer):
    referred_user_email = serializers.EmailField(source='referred_user.email', read_only=True)

    class Meta:
        model = UserReferral
        fields = ['referred_user_email', 'referral_code', 'referred_at', 'reward_earned']
        read_only_fields = ['referred_user_email', 'referral_code', 'referred_at']

class UserAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAuditLog
        fields = ['change_type', 'field_name', 'old_value', 'new_value', 'timestamp']
        read_only_fields = ['timestamp']

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['theme', 'language', 'date_format', 'time_format', 'default_search_radius', 'map_provider', 'currency']
        extra_kwargs = {
            'default_search_radius': {'min_value': 1, 'max_value': 1000}
        }

class UserMapInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMapInteraction
        fields = ['interaction_type', 'location_latitude', 'location_longitude', 'zoom_level', 'timestamp']
        read_only_fields = ['timestamp']
        extra_kwargs = {
            'zoom_level': {'min_value': 1, 'max_value': 20}
        }