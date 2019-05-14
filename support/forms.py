from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Chat, ChatMessage, Ticket, TicketReply

class ChatMessageForm(forms.ModelForm):
	message = forms.CharField()
	chat_id = forms.IntegerField()
	class Meta:
		model = ChatMessage
		fields = ('message',)

class TicketForm(forms.ModelForm):
	sub_title = forms.CharField()
	sub_description = forms.CharField(widget=forms.Textarea)
	class Meta:
		model = Ticket
		fields = ('sub_title', 'sub_description',)

class TicketReplayForm(forms.ModelForm):
	ticket_id = forms.IntegerField()
	sub_description = forms.CharField(widget=forms.Textarea)
	class Meta:
		model = TicketReply
		fields = ('sub_description','ticket',)
