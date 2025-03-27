from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.mixins import (
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, CreateModelMixin
)
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import (
    User, UserProperty, UserAddress, SavedMapView, UserActivity,
    UserConnection, SavedSearch, UserNotification, AgentProfile,
    UserReview, UserDocument, UserSubscription, UserReferral,
    UserAuditLog, UserPreference, UserMapInteraction
)
from .serializers import (
    UserSerializer, UserPropertySerializer, UserAddressSerializer,
    SavedMapViewSerializer, UserActivitySerializer, UserConnectionSerializer,
    SavedSearchSerializer, UserNotificationSerializer, AgentProfileSerializer,
    UserReviewSerializer, UserDocumentSerializer, UserSubscriptionSerializer,
    UserReferralSerializer, UserAuditLogSerializer, UserPreferenceSerializer,
    UserMapInteractionSerializer
)
import json

# --- Helper Functions ---

def invalidate_user_cache(user_id):
    """Invalidate all caches related to a user."""
    prefixes = [
        f"user_{user_id}", f"user_properties_{user_id}", f"user_addresses_{user_id}",
        f"nearby_users_{user_id}", f"saved_map_views_{user_id}", f"user_activity_{user_id}",
        f"user_connections_{user_id}", f"saved_searches_{user_id}", f"user_notifications_{user_id}",
        f"agent_profile_{user_id}", f"user_reviews_{user_id}", f"user_documents_{user_id}",
        f"user_subscriptions_{user_id}", f"user_referrals_{user_id}", f"user_audit_logs_{user_id}",
        f"user_preferences_{user_id}", f"user_map_interactions_{user_id}"
    ]
    for prefix in prefixes:
        # Use cache.delete() for each key pattern manually since delete_pattern isn’t standard
        cache.delete(prefix)

# --- API ViewSets (Full CRUD for All Models) ---

# 1. User
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    lookup_field = 'user_id'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(user_id=user.user_id)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        if user.privacy_level == 'private' and request.user != user and not request.user.is_staff:
            return Response({"error": "Private profile"}, status=status.HTTP_403_FORBIDDEN)
        cache_key = f"user_{user.user_id}_{request.user.is_authenticated}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        serializer = self.get_serializer(user)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 15)
        return Response(data)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        response = super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            invalidate_user_cache(user.user_id)
        return response

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        user.account_status = 'deleted'
        user.is_active = False
        user.save()
        invalidate_user_cache(user.user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

# 2. UserProperty
class UserPropertyViewSet(viewsets.ModelViewSet):
    serializer_class = UserPropertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            return UserProperty.objects.none()
        filter_type = self.request.query_params.get('filter', 'all')
        if filter_type == 'owned':
            return user.properties.filter(property_type='owned', is_active=True)
        elif filter_type == 'saved':
            return user.properties.filter(property_type='saved', is_active=True)
        return user.properties.filter(is_active=True)

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"user_properties_{user_id}_{request.query_params.get('filter', 'all')}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 10)
        return Response(data)

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Unauthorized")
        serializer.save(user=user)
        invalidate_user_cache(user_id)

    def perform_update(self, serializer):
        user_id = self.kwargs['user_id']
        serializer.save()
        invalidate_user_cache(user_id)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        invalidate_user_cache(self.kwargs['user_id'])

# 3. UserAddress
class UserAddressViewSet(viewsets.ModelViewSet):
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            return UserAddress.objects.none()
        return user.addresses.all()

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"user_addresses_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 10)
        return Response(data)

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Unauthorized")
        serializer.save(user=user)
        invalidate_user_cache(user_id)

    def perform_update(self, serializer):
        user_id = self.kwargs['user_id']
        serializer.save()
        invalidate_user_cache(user_id)

    def perform_destroy(self, instance):
        invalidate_user_cache(self.kwargs['user_id'])
        instance.delete()

# 4. SavedMapView
class SavedMapViewViewSet(viewsets.ModelViewSet):
    serializer_class = SavedMapViewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            return SavedMapView.objects.none()
        return SavedMapView.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"saved_map_views_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 10)
        return Response(data)

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        serializer.save(user=user)
        invalidate_user_cache(user_id)

    def perform_update(self, serializer):
        user_id = self.kwargs['user_id']
        serializer.save()
        invalidate_user_cache(user_id)

    def perform_destroy(self, instance):
        invalidate_user_cache(self.kwargs['user_id'])
        instance.delete()

# 5. UserActivity
class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            return UserActivity.objects.none()
        return UserActivity.objects.filter(user=user)[:50]

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"user_activity_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 5)
        return Response(data)

# 6. UserConnection
class UserConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = UserConnectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user.privacy_level == 'private' and user != self.request.user and not self.request.user.is_staff:
            return UserConnection.objects.none()
        return UserConnection.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"user_connections_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 10)
        return Response(data)

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Unauthorized")
        serializer.save(user=user)
        invalidate_user_cache(user_id)

    def perform_destroy(self, instance):
        invalidate_user_cache(self.kwargs['user_id'])
        instance.delete()

# 7. SavedSearch
class SavedSearchViewSet(viewsets.ModelViewSet):
    serializer_class = SavedSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            return SavedSearch.objects.none()
        return SavedSearch.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"saved_searches_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 10)
        return Response(data)

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        serializer.save(user=user)
        invalidate_user_cache(user_id)

    def perform_update(self, serializer):
        user_id = self.kwargs['user_id']
        serializer.save()
        invalidate_user_cache(user_id)

    def perform_destroy(self, instance):
        invalidate_user_cache(self.kwargs['user_id'])
        instance.delete()

# 8. UserNotification
class UserNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = UserNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            return UserNotification.objects.none()
        return UserNotification.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"user_notifications_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 5)
        return Response(data)

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        serializer.save(user=user)
        invalidate_user_cache(user_id)

    def perform_update(self, serializer):
        user_id = self.kwargs['user_id']
        serializer.save()
        invalidate_user_cache(user_id)

    def perform_destroy(self, instance):
        invalidate_user_cache(self.kwargs['user_id'])
        instance.delete()

# 9. AgentProfile
class AgentProfileViewSet(viewsets.ModelViewSet):
    serializer_class = AgentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        return AgentProfile.objects.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"agent_profile_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 15)
        return Response(data)

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Unauthorized")
        if hasattr(user, 'agent_profile'):
            raise ValidationError({"error": "Agent profile already exists"})
        serializer.save(user=user)
        invalidate_user_cache(user_id)

    def perform_update(self, serializer):
        user_id = self.kwargs['user_id']
        serializer.save()
        invalidate_user_cache(user_id)

# 10. UserReview
class UserReviewViewSet(viewsets.ModelViewSet):
    serializer_class = UserReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        return UserReview.objects.filter(reviewed_user=user)

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"user_reviews_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 10)
        return Response(data)

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        serializer.save(reviewer=self.request.user, reviewed_user=user)
        invalidate_user_cache(user_id)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.reviewer != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Unauthorized")
        serializer.save()
        invalidate_user_cache(self.kwargs['user_id'])

    def perform_destroy(self, instance):
        if instance.reviewer != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Unauthorized")
        invalidate_user_cache(self.kwargs['user_id'])
        instance.delete()

# 11. UserDocument
class UserDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = UserDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            return UserDocument.objects.none()
        return UserDocument.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"user_documents_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 10)
        return Response(data)

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        serializer.save(user=user)
        invalidate_user_cache(user_id)

    def perform_update(self, serializer):
        user_id = self.kwargs['user_id']
        serializer.save()
        invalidate_user_cache(user_id)

    def perform_destroy(self, instance):
        invalidate_user_cache(self.kwargs['user_id'])
        instance.delete()

# 12. UserSubscription
class UserSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            return UserSubscription.objects.none()
        return UserSubscription.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"user_subscriptions_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 10)
        return Response(data)

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        serializer.save(user=user)
        invalidate_user_cache(user_id)

    def perform_update(self, serializer):
        user_id = self.kwargs['user_id']
        serializer.save()
        invalidate_user_cache(user_id)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.cancellation_date = timezone.now()
        instance.save()
        invalidate_user_cache(self.kwargs['user_id'])

# 13. UserReferral
class UserReferralViewSet(viewsets.ModelViewSet):
    serializer_class = UserReferralSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            return UserReferral.objects.none()
        return UserReferral.objects.filter(referrer=user)

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"user_referrals_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 10)
        return Response(data)

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        serializer.save(referrer=user)
        invalidate_user_cache(user_id)

    def perform_update(self, serializer):
        user_id = self.kwargs['user_id']
        serializer.save()
        invalidate_user_cache(user_id)

# 14. UserAuditLog
class UserAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserAuditLogSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        return UserAuditLog.objects.filter(user=user)[:50]

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"user_audit_logs_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 5)
        return Response(data)

# 15. UserPreference
class UserPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            return UserPreference.objects.none()
        return UserPreference.objects.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        preference, created = UserPreference.objects.get_or_create(user=user)
        cache_key = f"user_preferences_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        serializer = self.get_serializer(preference)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 15)
        return Response(data)

    def perform_update(self, serializer):
        user_id = self.kwargs['user_id']
        serializer.save()
        invalidate_user_cache(user_id)

# 16. UserMapInteraction
class UserMapInteractionViewSet(viewsets.ModelViewSet):
    serializer_class = UserMapInteractionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        if user != self.request.user and not self.request.user.is_staff:
            return UserMapInteraction.objects.none()
        return UserMapInteraction.objects.filter(user=user)[:50]

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        cache_key = f"user_map_interactions_{user_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 5)
        return Response(data)

    def perform_create(self, serializer):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        serializer.save(user=user)
        invalidate_user_cache(user_id)

# --- Additional Utility Views ---

class NearbyUsersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latitude = float(request.query_params.get('lat', 0))
        longitude = float(request.query_params.get('lon', 0))
        distance_km = float(request.query_params.get('distance', 10))
        cache_key = f"nearby_users_{latitude}_{longitude}_{distance_km}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(json.loads(cached_data))
        users = User.objects.nearby_users(latitude, longitude, distance_km)
        serializer = UserSerializer(users, many=True)
        data = serializer.data
        cache.set(cache_key, json.dumps(data), 60 * 5)
        return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_users_api(request):
    cache_key = "active_users"
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(json.loads(cached_data))
    users = User.objects.active_users()
    serializer = UserSerializer(users, many=True)
    data = serializer.data
    cache.set(cache_key, json.dumps(data), 60 * 5)
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_by_role_api(request, role):
    cache_key = f"users_by_role_{role}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(json.loads(cached_data))
    users = User.objects.by_role(role)
    serializer = UserSerializer(users, many=True)
    data = serializer.data
    cache.set(cache_key, json.dumps(data), 60 * 10)
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_search_preferences_api(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    if user != request.user and not request.user.is_staff:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    cache_key = f"user_search_preferences_{user_id}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(json.loads(cached_data))
    data = {
        'min_price': user.min_price,
        'max_price': user.max_price,
        'min_bedrooms': user.min_bedrooms,
        'max_bedrooms': user.max_bedrooms,
        'property_types': json.loads(user.property_types) if user.property_types else [],
        'preferred_locations': json.loads(user.preferred_locations) if user.preferred_locations else [],
    }
    cache.set(cache_key, json.dumps(data), 60 * 10)
    return Response(data)