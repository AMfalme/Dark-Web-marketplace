from django.contrib import admin
from django.db.models import Q
from django.conf import settings

from .models import Chat, ChatMessage, Ticket, TicketReply

admin.site.register(Chat)
admin.site.register(ChatMessage)
admin.site.register(Ticket)
admin.site.register(TicketReply)

