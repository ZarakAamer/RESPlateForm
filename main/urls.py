# main/urls.py
from django.urls import path
from . import views
from django.shortcuts import render
urlpatterns = [
    # API Routes
    path('api/system-config/', views.SystemConfigListCreateAPIView.as_view(), name='api-systemconfig-list'),
    path('api/system-config/<uuid:config_id>/', views.SystemConfigDetailAPIView.as_view(), name='api-systemconfig-detail'),
    path('api/system-config/active/', views.ActiveSystemConfigAPIView.as_view(), name='api-active-systemconfig'),
    path('api/ad-campaigns/', views.AdCampaignListCreateAPIView.as_view(), name='api-adcampaign-list'),
    path('api/ad-campaigns/<uuid:campaign_id>/', views.AdCampaignDetailAPIView.as_view(), name='api-adcampaign-detail'),
    path('api/banners/', views.BannerListCreateAPIView.as_view(), name='api-banner-list'),
    path('api/banners/<uuid:banner_id>/', views.BannerDetailAPIView.as_view(), name='api-banner-detail'),
    path('api/ad-requests/', views.AdRequestListCreateAPIView.as_view(), name='api-adrequest-list'),
    path('api/ad-requests/<uuid:request_id>/', views.AdRequestDetailAPIView.as_view(), name='api-adrequest-detail'),
    path('api/ad-analytics/', views.AdAnalyticsListAPIView.as_view(), name='api-adanalytics-list'),
    path('api/ad-analytics/<uuid:analytics_id>/', views.AdAnalyticsDetailAPIView.as_view(), name='api-adanalytics-detail'),
    path('api/transactions/', views.TransactionListCreateAPIView.as_view(), name='api-transaction-list'),
    path('api/transactions/<uuid:transaction_id>/', views.TransactionDetailAPIView.as_view(), name='api-transaction-detail'),
    path('api/messages/', views.MessageListCreateAPIView.as_view(), name='api-message-list'),
    path('api/messages/<uuid:message_id>/', views.MessageDetailAPIView.as_view(), name='api-message-detail'),
    path('api/messages/<uuid:message_id>/mark-read/', views.MarkMessageReadAPIView.as_view(), name='api-mark-message-read'),
    path('api/support-tickets/', views.SupportTicketListCreateAPIView.as_view(), name='api-supportticket-list'),
    path('api/support-tickets/<uuid:ticket_id>/', views.SupportTicketDetailAPIView.as_view(), name='api-supportticket-detail'),
    path('api/feedback/', views.FeedbackListCreateAPIView.as_view(), name='api-feedback-list'),
    path('api/feedback/<uuid:feedback_id>/', views.FeedbackDetailAPIView.as_view(), name='api-feedback-detail'),
    path('api/system-logs/', views.SystemLogListAPIView.as_view(), name='api-systemlog-list'),
    path('api/system-logs/<uuid:log_id>/', views.SystemLogDetailAPIView.as_view(), name='api-systemlog-detail'),
    path('api/announcements/', views.AnnouncementListCreateAPIView.as_view(), name='api-announcement-list'),
    path('api/announcements/<uuid:announcement_id>/', views.AnnouncementDetailAPIView.as_view(), name='api-announcement-detail'),
    path('api/contact-us/', views.ContactUsListCreateAPIView.as_view(), name='api-contactus-list'),
    path('api/contact-us/<uuid:contact_id>/', views.ContactUsDetailAPIView.as_view(), name='api-contactus-detail'),
    path('api/faqs/', views.FAQListCreateAPIView.as_view(), name='api-faq-list'),
    path('api/faqs/<uuid:faq_id>/', views.FAQDetailAPIView.as_view(), name='api-faq-detail'),
    path('api/legal-documents/', views.LegalDocumentListCreateAPIView.as_view(), name='api-legaldocument-list'),
    path('api/legal-documents/<uuid:document_id>/', views.LegalDocumentDetailAPIView.as_view(), name='api-legaldocument-detail'),
    path('api/audit-logs/', views.AuditLogListAPIView.as_view(), name='api-auditlog-list'),
    path('api/audit-logs/<uuid:audit_id>/', views.AuditLogDetailAPIView.as_view(), name='api-auditlog-detail'),
    path('api/geofence-alerts/', views.GeofenceAlertListCreateAPIView.as_view(), name='api-geofencealert-list'),
    path('api/geofence-alerts/<uuid:alert_id>/', views.GeofenceAlertDetailAPIView.as_view(), name='api-geofencealert-detail'),

    # Template Routes
    path('system-config/', views.SystemConfigListView.as_view(), name='systemconfig-list'),
    path('system-config/<uuid:pk>/', views.SystemConfigDetailView.as_view(), name='systemconfig-detail'),
    path('system-config/create/', views.SystemConfigCreateView.as_view(), name='systemconfig-create'),
    path('system-config/<uuid:pk>/update/', views.SystemConfigUpdateView.as_view(), name='systemconfig-update'),
    path('ad-campaigns/', views.AdCampaignListView.as_view(), name='adcampaign-list'),
    path('ad-campaigns/<uuid:pk>/', views.AdCampaignDetailView.as_view(), name='adcampaign-detail'),
    path('ad-campaigns/create/', views.AdCampaignCreateView.as_view(), name='adcampaign-create'),
    path('ad-campaigns/<uuid:pk>/update/', views.AdCampaignUpdateView.as_view(), name='adcampaign-update'),
    path('banners/', views.BannerListView.as_view(), name='banner-list'),
    path('banners/<uuid:pk>/', views.BannerDetailView.as_view(), name='banner-detail'),
    path('banners/create/', views.BannerCreateView.as_view(), name='banner-create'),
    path('banners/<uuid:pk>/update/', views.BannerUpdateView.as_view(), name='banner-update'),
    path('ad-requests/', views.AdRequestListView.as_view(), name='adrequest-list'),
    path('ad-requests/<uuid:pk>/', views.AdRequestDetailView.as_view(), name='adrequest-detail'),
    path('ad-requests/create/', views.AdRequestCreateView.as_view(), name='adrequest-create'),
    path('ad-analytics/', views.AdAnalyticsListView.as_view(), name='adanalytics-list'),
    path('ad-analytics/<uuid:pk>/', views.AdAnalyticsDetailView.as_view(), name='adanalytics-detail'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('messages/', views.MessageListView.as_view(), name='message-list'),
    path('messages/<uuid:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
    path('messages/create/', views.MessageCreateView.as_view(), name='message-create'),
    path('support-tickets/', views.SupportTicketListView.as_view(), name='supportticket-list'),
    path('support-tickets/<uuid:pk>/', views.SupportTicketDetailView.as_view(), name='supportticket-detail'),
    path('support-tickets/create/', views.SupportTicketCreateView.as_view(), name='supportticket-create'),
    path('feedback/', views.FeedbackListView.as_view(), name='feedback-list'),
    path('feedback/<uuid:pk>/', views.FeedbackDetailView.as_view(), name='feedback-detail'),
    path('feedback/create/', views.FeedbackCreateView.as_view(), name='feedback-create'),
    path('system-logs/', views.SystemLogListView.as_view(), name='systemlog-list'),
    path('system-logs/<uuid:pk>/', views.SystemLogDetailView.as_view(), name='systemlog-detail'),
    path('announcements/', views.AnnouncementListView.as_view(), name='announcement-list'),
    path('announcements/<uuid:pk>/', views.AnnouncementDetailView.as_view(), name='announcement-detail'),
    path('announcements/create/', views.AnnouncementCreateView.as_view(), name='announcement-create'),
    path('contact-us/', views.ContactUsListView.as_view(), name='contactus-list'),
    path('contact-us/<uuid:pk>/', views.ContactUsDetailView.as_view(), name='contactus-detail'),
    path('contact-us/create/', views.ContactUsCreateView.as_view(), name='contactus-create'),
    path('contact-us/thanks/', lambda request: render(request, 'main/contactus_thanks.html'), name='contactus-thanks'),
    path('faqs/', views.FAQListView.as_view(), name='faq-list'),
    path('faqs/<uuid:pk>/', views.FAQDetailView.as_view(), name='faq-detail'),
    path('faqs/create/', views.FAQCreateView.as_view(), name='faq-create'),
    path('legal-documents/', views.LegalDocumentListView.as_view(), name='legaldocument-list'),
    path('legal-documents/<uuid:pk>/', views.LegalDocumentDetailView.as_view(), name='legaldocument-detail'),
    path('legal-documents/create/', views.LegalDocumentCreateView.as_view(), name='legaldocument-create'),
    path('audit-logs/', views.AuditLogListView.as_view(), name='auditlog-list'),
    path('audit-logs/<uuid:pk>/', views.AuditLogDetailView.as_view(), name='auditlog-detail'),
    path('geofence-alerts/', views.GeofenceAlertListView.as_view(), name='geofencealert-list'),
    path('geofence-alerts/<uuid:pk>/', views.GeofenceAlertDetailView.as_view(), name='geofencealert-detail'),
    path('geofence-alerts/create/', views.GeofenceAlertCreateView.as_view(), name='geofencealert-create'),
]