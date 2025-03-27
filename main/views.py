# main/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import (
    SystemConfig, AdCampaign, Banner, AdRequest, AdAnalytics, Transaction, Message,
    SupportTicket, Feedback, SystemLog, Announcement, ContactUs, FAQ, LegalDocument,
    AuditLog, GeofenceAlert
)
from .serializers import (
    SystemConfigSerializer, AdCampaignSerializer, BannerSerializer, AdRequestSerializer,
    AdAnalyticsSerializer, TransactionSerializer, MessageSerializer, SupportTicketSerializer,
    FeedbackSerializer, SystemLogSerializer, AnnouncementSerializer, ContactUsSerializer,
    FAQSerializer, LegalDocumentSerializer, AuditLogSerializer, GeofenceAlertSerializer
)
from .forms import (
    SystemConfigForm, AdCampaignForm, BannerForm, AdRequestForm, TransactionForm,
    MessageForm, SupportTicketForm, FeedbackForm, AnnouncementForm, ContactUsForm,
    FAQForm, LegalDocumentForm, GeofenceAlertForm
)

# Mixin for admin-only access
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

# --- SystemConfig Views ---
# API Views
class SystemConfigListCreateAPIView(generics.ListCreateAPIView):
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAdminUser]

class SystemConfigDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'config_id'

class ActiveSystemConfigAPIView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        config = SystemConfig.objects.get_active_config()
        serializer = SystemConfigSerializer(config)
        return Response(serializer.data)

# Template Views
class SystemConfigListView(AdminRequiredMixin, ListView):
    model = SystemConfig
    template_name = 'main/systemconfig_list.html'
    context_object_name = 'configs'

class SystemConfigDetailView(AdminRequiredMixin, DetailView):
    model = SystemConfig
    template_name = 'main/systemconfig_detail.html'
    context_object_name = 'config'

class SystemConfigCreateView(AdminRequiredMixin, CreateView):
    model = SystemConfig
    form_class = SystemConfigForm
    template_name = 'main/systemconfig_form.html'
    success_url = reverse_lazy('systemconfig-list')

class SystemConfigUpdateView(AdminRequiredMixin, UpdateView):
    model = SystemConfig
    form_class = SystemConfigForm
    template_name = 'main/systemconfig_form.html'
    success_url = reverse_lazy('systemconfig-list')

# --- AdCampaign Views ---
# API Views
class AdCampaignListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AdCampaignSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return AdCampaign.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AdCampaignDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdCampaignSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'campaign_id'
    def get_queryset(self):
        return AdCampaign.objects.filter(user=self.request.user)

# Template Views
class AdCampaignListView(LoginRequiredMixin, ListView):
    model = AdCampaign
    template_name = 'main/adcampaign_list.html'
    context_object_name = 'campaigns'
    def get_queryset(self):
        return AdCampaign.objects.filter(user=self.request.user)

class AdCampaignDetailView(LoginRequiredMixin, DetailView):
    model = AdCampaign
    template_name = 'main/adcampaign_detail.html'
    context_object_name = 'campaign'

class AdCampaignCreateView(LoginRequiredMixin, CreateView):
    model = AdCampaign
    form_class = AdCampaignForm
    template_name = 'main/adcampaign_form.html'
    success_url = reverse_lazy('adcampaign-list')
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class AdCampaignUpdateView(LoginRequiredMixin, UpdateView):
    model = AdCampaign
    form_class = AdCampaignForm
    template_name = 'main/adcampaign_form.html'
    success_url = reverse_lazy('adcampaign-list')

# --- Banner Views ---
# API Views
class BannerListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Banner.objects.filter(campaign__user=self.request.user)
    def perform_create(self, serializer):
        campaign = get_object_or_404(AdCampaign, campaign_id=self.request.data.get('campaign'), user=self.request.user)
        serializer.save(campaign=campaign)

class BannerDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'banner_id'
    def get_queryset(self):
        return Banner.objects.filter(campaign__user=self.request.user)

# Template Views
class BannerListView(LoginRequiredMixin, ListView):
    model = Banner
    template_name = 'main/banner_list.html'
    context_object_name = 'banners'
    def get_queryset(self):
        return Banner.objects.filter(campaign__user=self.request.user)

class BannerDetailView(LoginRequiredMixin, DetailView):
    model = Banner
    template_name = 'main/banner_detail.html'
    context_object_name = 'banner'

class BannerCreateView(LoginRequiredMixin, CreateView):
    model = Banner
    form_class = BannerForm
    template_name = 'main/banner_form.html'
    success_url = reverse_lazy('banner-list')

class BannerUpdateView(LoginRequiredMixin, UpdateView):
    model = Banner
    form_class = BannerForm
    template_name = 'main/banner_form.html'
    success_url = reverse_lazy('banner-list')

# --- AdRequest Views ---
# API Views
class AdRequestListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AdRequestSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return AdRequest.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AdRequestDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdRequestSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'request_id'
    def get_queryset(self):
        return AdRequest.objects.filter(user=self.request.user)

# Template Views
class AdRequestListView(LoginRequiredMixin, ListView):
    model = AdRequest
    template_name = 'main/adrequest_list.html'
    context_object_name = 'requests'
    def get_queryset(self):
        return AdRequest.objects.filter(user=self.request.user)

class AdRequestDetailView(LoginRequiredMixin, DetailView):
    model = AdRequest
    template_name = 'main/adrequest_detail.html'
    context_object_name = 'request'

class AdRequestCreateView(LoginRequiredMixin, CreateView):
    model = AdRequest
    form_class = AdRequestForm
    template_name = 'main/adrequest_form.html'
    success_url = reverse_lazy('adrequest-list')
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

# --- AdAnalytics Views ---
# API Views
class AdAnalyticsListAPIView(generics.ListAPIView):
    serializer_class = AdAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return AdAnalytics.objects.filter(banner__campaign__user=self.request.user)

class AdAnalyticsDetailAPIView(generics.RetrieveAPIView):
    serializer_class = AdAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'analytics_id'
    def get_queryset(self):
        return AdAnalytics.objects.filter(banner__campaign__user=self.request.user)

# Template Views
class AdAnalyticsListView(LoginRequiredMixin, ListView):
    model = AdAnalytics
    template_name = 'main/adanalytics_list.html'
    context_object_name = 'analytics'
    def get_queryset(self):
        return AdAnalytics.objects.filter(banner__campaign__user=self.request.user)

class AdAnalyticsDetailView(LoginRequiredMixin, DetailView):
    model = AdAnalytics
    template_name = 'main/adanalytics_detail.html'
    context_object_name = 'analytics'

# --- Transaction Views ---
# API Views
class TransactionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Transaction.objects.filter(buyer=self.request.user) | Transaction.objects.filter(seller=self.request.user)

class TransactionDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'transaction_id'
    def get_queryset(self):
        return Transaction.objects.filter(buyer=self.request.user) | Transaction.objects.filter(seller=self.request.user)

# Template Views
class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'main/transaction_list.html'
    context_object_name = 'transactions'
    def get_queryset(self):
        return Transaction.objects.filter(buyer=self.request.user) | Transaction.objects.filter(seller=self.request.user)

class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'main/transaction_detail.html'
    context_object_name = 'transaction'

# --- Message Views ---
# API Views
class MessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user) | Message.objects.filter(recipient=self.request.user)
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class MessageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'message_id'
    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user) | Message.objects.filter(recipient=self.request.user)

class MarkMessageReadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, message_id):
        message = get_object_or_404(Message, message_id=message_id, recipient=request.user)
        message.mark_as_read()
        return Response({"detail": "Message marked as read"}, status=status.HTTP_200_OK)

# Template Views
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'main/message_list.html'
    context_object_name = 'messages'
    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user) | Message.objects.filter(recipient=self.request.user)

class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'main/message_detail.html'
    context_object_name = 'message'
    def get_object(self):
        obj = super().get_object()
        if obj.recipient == self.request.user and not obj.is_read:
            obj.mark_as_read()
        return obj

class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'main/message_form.html'
    success_url = reverse_lazy('message-list')
    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super().form_valid(form)

# --- SupportTicket Views ---
# API Views
class SupportTicketListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SupportTicketDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'ticket_id'
    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user)

# Template Views
class SupportTicketListView(LoginRequiredMixin, ListView):
    model = SupportTicket
    template_name = 'main/supportticket_list.html'
    context_object_name = 'tickets'
    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user)

class SupportTicketDetailView(LoginRequiredMixin, DetailView):
    model = SupportTicket
    template_name = 'main/supportticket_detail.html'
    context_object_name = 'ticket'

class SupportTicketCreateView(LoginRequiredMixin, CreateView):
    model = SupportTicket
    form_class = SupportTicketForm
    template_name = 'main/supportticket_form.html'
    success_url = reverse_lazy('supportticket-list')
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

# --- Feedback Views ---
# API Views
class FeedbackListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FeedbackDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'feedback_id'
    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user)

# Template Views
class FeedbackListView(LoginRequiredMixin, ListView):
    model = Feedback
    template_name = 'main/feedback_list.html'
    context_object_name = 'feedbacks'
    def get_queryset(self):
        return Feedback.objects.filter(user=self.request.user)

class FeedbackDetailView(LoginRequiredMixin, DetailView):
    model = Feedback
    template_name = 'main/feedback_detail.html'
    context_object_name = 'feedback'

class FeedbackCreateView(LoginRequiredMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'main/feedback_form.html'
    success_url = reverse_lazy('feedback-list')
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

# --- SystemLog Views ---
# API Views
class SystemLogListAPIView(generics.ListAPIView):
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [IsAdminUser]

class SystemLogDetailAPIView(generics.RetrieveAPIView):
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'log_id'

# Template Views
class SystemLogListView(AdminRequiredMixin, ListView):
    model = SystemLog
    template_name = 'main/systemlog_list.html'
    context_object_name = 'logs'

class SystemLogDetailView(AdminRequiredMixin, DetailView):
    model = SystemLog
    template_name = 'main/systemlog_detail.html'
    context_object_name = 'log'

# --- Announcement Views ---
# API Views
class AnnouncementListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAdminUser]
    def get_queryset(self):
        return Announcement.objects.filter(is_active=True)

class AnnouncementDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'announcement_id'

# Template Views
class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'main/announcement_list.html'
    context_object_name = 'announcements'
    def get_queryset(self):
        return Announcement.objects.filter(is_active=True)

class AnnouncementDetailView(DetailView):
    model = Announcement
    template_name = 'main/announcement_detail.html'
    context_object_name = 'announcement'

class AnnouncementCreateView(AdminRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'main/announcement_form.html'
    success_url = reverse_lazy('announcement-list')
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

# --- ContactUs Views ---
# API Views
class ContactUsListCreateAPIView(generics.ListCreateAPIView):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    permission_classes = []

class ContactUsDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'contact_id'

# Template Views
class ContactUsListView(AdminRequiredMixin, ListView):
    model = ContactUs
    template_name = 'main/contactus_list.html'
    context_object_name = 'contacts'

class ContactUsDetailView(AdminRequiredMixin, DetailView):
    model = ContactUs
    template_name = 'main/contactus_detail.html'
    context_object_name = 'contact'

class ContactUsCreateView(CreateView):
    model = ContactUs
    form_class = ContactUsForm
    template_name = 'main/contactus_form.html'
    success_url = reverse_lazy('contactus-thanks')

# --- FAQ Views ---
# API Views
class FAQListCreateAPIView(generics.ListCreateAPIView):
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    permission_classes = []
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return []

class FAQDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'faq_id'

# Template Views
class FAQListView(ListView):
    model = FAQ
    template_name = 'main/faq_list.html'
    context_object_name = 'faqs'
    def get_queryset(self):
        return FAQ.objects.filter(is_active=True)

class FAQDetailView(DetailView):
    model = FAQ
    template_name = 'main/faq_detail.html'
    context_object_name = 'faq'

class FAQCreateView(AdminRequiredMixin, CreateView):
    model = FAQ
    form_class = FAQForm
    template_name = 'main/faq_form.html'
    success_url = reverse_lazy('faq-list')

# --- LegalDocument Views ---
# API Views
class LegalDocumentListCreateAPIView(generics.ListCreateAPIView):
    queryset = LegalDocument.objects.filter(is_active=True)
    serializer_class = LegalDocumentSerializer
    permission_classes = []
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return []

class LegalDocumentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LegalDocument.objects.all()
    serializer_class = LegalDocumentSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'document_id'

# Template Views
class LegalDocumentListView(ListView):
    model = LegalDocument
    template_name = 'main/legaldocument_list.html'
    context_object_name = 'documents'
    def get_queryset(self):
        return LegalDocument.objects.filter(is_active=True)

class LegalDocumentDetailView(DetailView):
    model = LegalDocument
    template_name = 'main/legaldocument_detail.html'
    context_object_name = 'document'

class LegalDocumentCreateView(AdminRequiredMixin, CreateView):
    model = LegalDocument
    form_class = LegalDocumentForm
    template_name = 'main/legaldocument_form.html'
    success_url = reverse_lazy('legaldocument-list')

# --- AuditLog Views ---
# API Views
class AuditLogListAPIView(generics.ListAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]

class AuditLogDetailAPIView(generics.RetrieveAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'audit_id'

# Template Views
class AuditLogListView(AdminRequiredMixin, ListView):
    model = AuditLog
    template_name = 'main/auditlog_list.html'
    context_object_name = 'logs'

class AuditLogDetailView(AdminRequiredMixin, DetailView):
    model = AuditLog
    template_name = 'main/auditlog_detail.html'
    context_object_name = 'log'

# --- GeofenceAlert Views ---
# API Views
class GeofenceAlertListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = GeofenceAlertSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return GeofenceAlert.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GeofenceAlertDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GeofenceAlertSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'alert_id'
    def get_queryset(self):
        return GeofenceAlert.objects.filter(user=self.request.user)

# Template Views
class GeofenceAlertListView(LoginRequiredMixin, ListView):
    model = GeofenceAlert
    template_name = 'main/geofencealert_list.html'
    context_object_name = 'alerts'
    def get_queryset(self):
        return GeofenceAlert.objects.filter(user=self.request.user)

class GeofenceAlertDetailView(LoginRequiredMixin, DetailView):
    model = GeofenceAlert
    template_name = 'main/geofencealert_detail.html'
    context_object_name = 'alert'

class GeofenceAlertCreateView(LoginRequiredMixin, CreateView):
    model = GeofenceAlert
    form_class = GeofenceAlertForm
    template_name = 'main/geofencealert_form.html'
    success_url = reverse_lazy('geofencealert-list')
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)