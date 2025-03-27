from django.urls import path
from . import views

urlpatterns = [
    # User
    path('api/user/<uuid:user_id>/', views.user_detail_api, name='user_detail_api'),
    
    # UserProperty
    path('api/user/<uuid:user_id>/properties/', views.UserPropertyAPI.as_view(), name='user_properties_api'),
    path('api/user/<uuid:user_id>/properties/<int:property_id>/', views.user_property_detail_api, name='user_property_detail_api'),
    
    # UserAddress
    path('api/user/<uuid:user_id>/addresses/', views.user_addresses_api, name='user_addresses_api'),
    path('api/user/<uuid:user_id>/addresses/<int:address_id>/', views.user_address_detail_api, name='user_address_detail_api'),
    
    # SavedMapView
    path('api/user/<uuid:user_id>/map-views/', views.saved_map_views_api, name='saved_map_views_api'),
    path('api/user/<uuid:user_id>/map-views/<int:map_view_id>/', views.saved_map_view_detail_api, name='saved_map_view_detail_api'),
    
    # UserActivity
    path('api/user/<uuid:user_id>/activity/', views.user_activity_api, name='user_activity_api'),
    
    # UserConnection
    path('api/user/<uuid:user_id>/connections/', views.user_connections_api, name='user_connections_api'),
    path('api/user/<uuid:user_id>/connections/<int:connection_id>/', views.user_connection_detail_api, name='user_connection_detail_api'),
    
    # SavedSearch
    path('api/user/<uuid:user_id>/searches/', views.saved_searches_api, name='saved_searches_api'),
    path('api/user/<uuid:user_id>/searches/<int:search_id>/', views.saved_search_detail_api, name='saved_search_detail_api'),
    
    # UserNotification
    path('api/user/<uuid:user_id>/notifications/', views.user_notifications_api, name='user_notifications_api'),
    path('api/user/<uuid:user_id>/notifications/<int:notification_id>/', views.user_notification_detail_api, name='user_notification_detail_api'),
    
    # AgentProfile
    path('api/user/<uuid:user_id>/agent/', views.agent_profile_api, name='agent_profile_api'),
    
    # UserReview
    path('api/user/<uuid:user_id>/reviews/', views.user_reviews_api, name='user_reviews_api'),
    path('api/user/<uuid:user_id>/reviews/<int:review_id>/', views.user_review_detail_api, name='user_review_detail_api'),
    
    # UserDocument
    path('api/user/<uuid:user_id>/documents/', views.user_documents_api, name='user_documents_api'),
    path('api/user/<uuid:user_id>/documents/<int:document_id>/', views.user_document_detail_api, name='user_document_detail_api'),
    
    # UserSubscription
    path('api/user/<uuid:user_id>/subscriptions/', views.user_subscriptions_api, name='user_subscriptions_api'),
    path('api/user/<uuid:user_id>/subscriptions/<int:subscription_id>/', views.user_subscription_detail_api, name='user_subscription_detail_api'),
    
    # UserReferral
    path('api/user/<uuid:user_id>/referrals/', views.user_referrals_api, name='user_referrals_api'),
    path('api/user/<uuid:user_id>/referrals/<int:referral_id>/', views.user_referral_detail_api, name='user_referral_detail_api'),
    
    # UserAuditLog
    path('api/user/<uuid:user_id>/audit-logs/', views.user_audit_logs_api, name='user_audit_logs_api'),
    
    # UserPreference
    path('api/user/<uuid:user_id>/preferences/', views.user_preferences_api, name='user_preferences_api'),
    
    # UserMapInteraction
    path('api/user/<uuid:user_id>/map-interactions/', views.user_map_interactions_api, name='user_map_interactions_api'),
    
    # Utility Views
    path('api/nearby-users/', views.NearbyUsersAPI.as_view(), name='nearby_users_api'),
    path('api/users/active/', views.active_users_api, name='active_users_api'),
    path('api/users/role/<str:role>/', views.users_by_role_api, name='users_by_role_api'),
    path('api/user/<uuid:user_id>/search-preferences/', views.user_search_preferences_api, name='user_search_preferences_api'),
]