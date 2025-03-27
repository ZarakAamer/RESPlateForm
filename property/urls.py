from django.urls import path
from . import views

urlpatterns = [
    # HTML Views
    path('profile/<uuid:user_id>/', views.user_profile_view, name='user_profile'),
    path('nearby/<float:latitude>/<float:longitude>/', views.nearby_properties_view, name='nearby_properties'),
    path('sitemap/properties/', views.sitemap_properties, name='sitemap_properties'),
    path('activity/<uuid:user_id>/', views.user_activity_view, name='user_activity'),

    # API Views
    path('api/user/<uuid:user_id>/', views.user_detail_api, name='user_detail_api'),
    path('api/user/<uuid:user_id>/properties/', views.UserPropertyListAPI.as_view(), name='user_properties_api'),
    path('api/user/<uuid:user_id>/addresses/', views.user_addresses_api, name='user_addresses_api'),
    path('api/nearby-users/', views.NearbyUsersAPI.as_view(), name='nearby_users_api'),
    path('api/user/<uuid:user_id>/map-views/', views.saved_map_views_api, name='saved_map_views_api'),
    path('api/user/<uuid:user_id>/activity/', views.user_activity_api, name='user_activity_api'),
    path('api/user/<uuid:user_id>/connections/', views.user_connections_api, name='user_connections_api'),
    path('api/user/<uuid:user_id>/searches/', views.saved_searches_api, name='saved_searches_api'),
    path('api/user/<uuid:user_id>/notifications/', views.user_notifications_api, name='user_notifications_api'),
    path('api/user/<uuid:user_id>/agent/', views.agent_profile_api, name='agent_profile_api'),
    path('api/user/<uuid:user_id>/reviews/', views.user_reviews_api, name='user_reviews_api'),
    path('api/user/<uuid:user_id>/documents/', views.user_documents_api, name='user_documents_api'),
    path('api/user/<uuid:user_id>/subscriptions/', views.user_subscriptions_api, name='user_subscriptions_api'),
    path('api/user/<uuid:user_id>/referrals/', views.user_referrals_api, name='user_referrals_api'),
    path('api/user/<uuid:user_id>/audit-logs/', views.user_audit_logs_api, name='user_audit_logs_api'),
    path('api/user/<uuid:user_id>/preferences/', views.user_preferences_api, name='user_preferences_api'),
    path('api/user/<uuid:user_id>/map-interactions/', views.user_map_interactions_api, name='user_map_interactions_api'),
    path('api/user/<uuid:user_id>/search-preferences/', views.user_search_preferences_api, name='user_search_preferences_api'),
    path('api/users/active/', views.active_users_api, name='active_users_api'),
    path('api/users/role/<str:role>/', views.users_by_role_api, name='users_by_role_api'),
]