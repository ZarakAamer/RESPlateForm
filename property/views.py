from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from .models import (
    Property, Address, Listing, Amenity, ListingAmenity, ListingPhoto, PriceHistory,
    MarketTrend, Transit, PropertyTransit, School, PropertySchool, OpenHouse,
    MapCluster, MapOverlay, PropertyValuation, ListingAnalytics
)
from users.models import UserProperty
from .serializers import (
    PropertySerializer, ListingSerializer, AddressSerializer, AmenitySerializer,
    ListingAmenitySerializer, ListingPhotoSerializer, PriceHistorySerializer,
    MarketTrendSerializer, TransitSerializer, PropertyTransitSerializer,
    SchoolSerializer, PropertySchoolSerializer, OpenHouseSerializer,
    MapClusterSerializer, MapOverlaySerializer, PropertyValuationSerializer,
    ListingAnalyticsSerializer
)
from django.db.models import Count, Avg, Q
from functools import reduce
from math import sqrt
import json
import logging

logger = logging.getLogger(__name__)

# --- Pagination Class ---
class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

# --- Helper Functions ---
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate approximate distance in km between two lat/long points."""
    lat_diff = (lat1 - lat2) * 111
    lon_diff = (lon1 - lon2) * 111 * abs(lat1)
    return sqrt(lat_diff**2 + lon_diff**2)

def update_map_clusters():
    """Update MapCluster dynamically."""
    clusters = MapCluster.objects.all()
    for cluster in clusters:
        listings = Listing.objects.within_radius(cluster.center_latitude, cluster.center_longitude, cluster.radius_km)
        cluster.property_count = listings.values('property').distinct().count()
        cluster.listing_count = listings.count()
        cluster.avg_price = listings.aggregate(Avg('price'))['price__avg'] or 0
        cluster.save()
    cache.delete('map_clusters')

def invalidate_cache(key_pattern):
    """Invalidate cache keys matching a pattern (simplified for latest Django)."""
    # Django doesn’t natively support pattern deletion; use cache.clear() for simplicity or a custom backend
    cache.delete(key_pattern)  # Assumes exact key match; adjust if using a custom cache backend

# --- CRUD API Views with DRF Generics ---
class PropertyListCreateView(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

    @method_decorator(cache_page(60 * 15))
    @method_decorator(vary_on_cookie)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = {
            'property_type': self.request.query_params.get('property_type'),
            'status': self.request.query_params.get('status'),
            'min_units': self.request.query_params.get('min_units'),
        }
        for key, value in filters.items():
            if value:
                queryset = queryset.filter(**{key: value})
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        invalidate_cache('property_list')
        invalidate_cache('property_detail')

class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    lookup_field = 'property_id'

    def get(self, request, *args, **kwargs):
        cache_key = f"property_detail_{self.kwargs['property_id']}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 60)
        return response

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache(f"property_detail_{self.kwargs['property_id']}")
        invalidate_cache('property_list')

    def perform_destroy(self, instance):
        instance.delete()
        invalidate_cache(f"property_detail_{self.kwargs['property_id']}")
        invalidate_cache('property_list')

class ListingListCreateView(generics.ListCreateAPIView):
    queryset = Listing.objects.active_listings()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = {
            'min_price': self.request.query_params.get('min_price', type=float),
            'max_price': self.request.query_params.get('max_price', type=float),
            'bedrooms': self.request.query_params.get('bedrooms', type=int),
            'neighborhood': self.request.query_params.get('neighborhood'),
            'latitude': self.request.query_params.get('latitude', type=float),
            'longitude': self.request.query_params.get('longitude', type=float),
            'radius': float(self.request.query_params.get('radius', 5)),
        }
        if filters['min_price']:
            queryset = queryset.filter(price__gte=filters['min_price'])
        if filters['max_price']:
            queryset = queryset.filter(price__lte=filters['max_price'])
        if filters['bedrooms']:
            queryset = queryset.filter(bedrooms=filters['bedrooms'])
        if filters['neighborhood']:
            queryset = queryset.by_neighborhood(filters['neighborhood'])
        if filters['latitude'] and filters['longitude']:
            queryset = queryset.within_radius(filters['latitude'], filters['longitude'], filters['radius'])
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        invalidate_cache('listing_list')
        invalidate_cache('listing_detail')
        update_map_clusters()

class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    lookup_field = 'listing_id'

    def get(self, request, *args, **kwargs):
        cache_key = f"listing_detail_{self.kwargs['listing_id']}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 30)
        return response

    def perform_update(self, serializer):
        serializer.save()
        invalidate_cache(f"listing_detail_{self.kwargs['listing_id']}")
        invalidate_cache('listing_list')
        update_map_clusters()

    def perform_destroy(self, instance):
        instance.delete()
        invalidate_cache(f"listing_detail_{self.kwargs['listing_id']}")
        invalidate_cache('listing_list')
        update_map_clusters()

# --- Map-Specific Views ---
class ListingMapView(generics.GenericAPIView):
    serializer_class = ListingSerializer

    @method_decorator(cache_page(60 * 5))
    def get(self, request, *args, **kwargs):
        lat = float(request.query_params.get('latitude', 40.7128))
        lon = float(request.query_params.get('longitude', -74.0060))
        radius = float(request.query_params.get('radius', 5))
        listings = Listing.objects.within_radius(lat, lon, radius)

        data = {
            'listings': ListingSerializer(listings, many=True).data,
            'center': {'latitude': lat, 'longitude': lon},
            'radius_km': radius,
            'property_count': listings.values('property').distinct().count(),
            'listing_count': listings.count(),
            'avg_price': listings.aggregate(Avg('price'))['price__avg'] or 0,
            'heatmap_data': [
                {'lat': l.property.address.latitude, 'lon': l.property.address.longitude, 'weight': l.heatmap_weight}
                for l in listings
            ],
            'clusters': MapClusterSerializer(MapCluster.objects.all(), many=True).data,
            'overlays': MapOverlaySerializer(MapOverlay.objects.filter(is_active=True), many=True).data
        }
        return Response(data)

class MapClusterListCreateView(generics.ListCreateAPIView):
    queryset = MapCluster.objects.all()
    serializer_class = MapClusterSerializer

    @method_decorator(cache_page(60 * 10))
    def get(self, request, *args, **kwargs):
        update_map_clusters()
        return super().get(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()
        update_map_clusters()
        invalidate_cache('map_clusters')

# --- User Interaction Views ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def favorite_listing(request, listing_id):
    listing = get_object_or_404(Listing, listing_id=listing_id)
    # Assuming UserProperty or similar model for favorites
    UserProperty.objects.get_or_create(user=request.user, property=listing.property, property_type='saved')
    listing.favorites_count += 1
    listing.save(update_fields=['favorites_count'])
    invalidate_cache(f"listing_detail_{listing_id}")
    return Response({'message': 'Listing favorited'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_inquiry(request, listing_id):
    listing = get_object_or_404(Listing, listing_id=listing_id)
    message = request.data.get('message')
    if not message:
        return Response({'error': 'Message required'}, status=status.HTTP_400_BAD_REQUEST)
    # Logic to send inquiry (e.g., email or notification) can be added
    listing.inquiries_count += 1
    listing.save(update_fields=['inquiries_count'])
    invalidate_cache(f"listing_detail_{listing_id}")
    return Response({'message': 'Inquiry sent'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rsvp_open_house(request, open_house_id):
    open_house = get_object_or_404(OpenHouse, open_house_id=open_house_id)
    if open_house.registration_required:
        open_house.attendees_count += 1
        open_house.save(update_fields=['attendees_count'])
        invalidate_cache(f"open_houses_{open_house.listing.listing_id}")
        # Add user to RSVP list (e.g., via a related model)
    return Response({'message': 'RSVP confirmed'}, status=status.HTTP_200_OK)

# --- Bulk Upload View ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_listing_upload(request):
    listings_data = request.data.get('listings', [])
    created_listings = []
    for data in listings_data:
        serializer = ListingSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            created_listings.append(serializer.data)
    if created_listings:
        invalidate_cache('listing_list')
        invalidate_cache('listing_detail')
        update_map_clusters()
        return Response({'created': created_listings}, status=status.HTTP_201_CREATED)
    return Response({'error': 'No valid listings'}, status=status.HTTP_400_BAD_REQUEST)

# --- Analytics Dashboard View ---
class ListingAnalyticsDashboardView(generics.GenericAPIView):
    serializer_class = ListingAnalyticsSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, listing_id):
        cache_key = f"listing_analytics_dashboard_{listing_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        listing = get_object_or_404(Listing, listing_id=listing_id)
        analytics = ListingAnalytics.objects.filter(listing=listing)
        serializer = self.get_serializer(analytics, many=True)
        data = {
            'listing': ListingSerializer(listing).data,
            'analytics': serializer.data,
            'total_views': analytics.aggregate(Avg('views'))['views__avg'] or 0,
            'total_inquiries': analytics.aggregate(Avg('inquiries'))['inquiries__avg'] or 0,
        }
        cache.set(cache_key, data, timeout=60 * 60)
        return Response(data)

# --- Traditional Views with CRUD ---
@method_decorator(login_required, name='dispatch')
@method_decorator(cache_page(60 * 15), name='dispatch')
class PropertyListView(View):
    def get(self, request):
        properties = Property.objects.all()
        context = {'properties': properties}
        return render(request, 'property_app/property_list.html', context)

@method_decorator(login_required, name='dispatch')
class PropertyCreateView(View):
    def get(self, request):
        return render(request, 'property_app/property_create.html')

    def post(self, request):
        data = request.POST
        property = Property.objects.create(
            building_name=data.get('building_name'),
            property_type=data.get('property_type'),
            user=request.user,
            # Add other fields as needed
        )
        invalidate_cache('property_list')
        return JsonResponse({'message': 'Property created', 'property_id': str(property.property_id)})

@method_decorator(login_required, name='dispatch')
class ListingCreateView(View):
    def get(self, request):
        properties = Property.objects.all()
        return render(request, 'property_app/listing_create.html', {'properties': properties})

    def post(self, request):
        data = request.POST
        listing = Listing.objects.create(
            property_id=data.get('property_id'),
            user=request.user,
            listing_type=data.get('listing_type'),
            price=data.get('price'),
            # Add other fields
        )
        invalidate_cache('listing_list')
        update_map_clusters()
        return JsonResponse({'message': 'Listing created', 'listing_id': str(listing.listing_id)})

# --- Additional StreetEasy-Inspired Views ---
@method_decorator(cache_page(60 * 60), name='dispatch')
class NeighborhoodStatsView(View):
    def get(self, request, neighborhood):
        trends = MarketTrend.objects.filter(neighborhood=neighborhood)
        listings = Listing.objects.by_neighborhood(neighborhood)
        context = {
            'neighborhood': neighborhood,
            'trends': trends,
            'listing_count': listings.count(),
            'avg_price': listings.aggregate(Avg('price'))['price__avg'] or 0,
        }
        return render(request, 'property_app/neighborhood_stats.html', context)

@api_view(['GET'])
def price_drop_listings(request):
    listings = Listing.objects.price_drops()
    serializer = ListingSerializer(listings, many=True, context={'request': request})
    return Response(serializer.data)