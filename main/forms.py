# main/forms.py
from django import forms
from .models import (
    SystemConfig, AdCampaign, Banner, AdRequest, Transaction, Message, SupportTicket,
    Feedback, Announcement, ContactUs, FAQ, LegalDocument, GeofenceAlert
)

class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = '__all__'

class AdCampaignForm(forms.ModelForm):
    class Meta:
        model = AdCampaign
        exclude = ['user', 'total_spent', 'remaining_budget']

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = '__all__'

class AdRequestForm(forms.ModelForm):
    class Meta:
        model = AdRequest
        exclude = ['user', 'reviewed_by', 'review_date']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ['buyer', 'seller', 'transaction_date', 'completed_date']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body', 'message_type', 'attachment']

class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        exclude = ['user', 'resolved_at', 'assigned_to']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = ['user', 'submitted_at']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        exclude = ['created_by', 'views_count']

class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['name', 'email', 'phone_number', 'subject', 'message', 'attachments']

class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = '__all__'

class LegalDocumentForm(forms.ModelForm):
    class Meta:
        model = LegalDocument
        fields = '__all__'

class GeofenceAlertForm(forms.ModelForm):
    class Meta:
        model = GeofenceAlert
        exclude = ['user', 'last_triggered', 'trigger_count']