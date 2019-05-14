from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from .models import Chat, ChatMessage, Ticket, TicketReply
from .forms import ChatMessageForm, TicketForm, TicketReplayForm


def customer_chat(request):
    if request.user.is_authenticated:
        chat = Chat.objects.filter(name=request.user)

        if not chat:
            chat = Chat.objects.create(name=request.user)
            chat.save()
            return HttpResponseRedirect(reverse('support:customer_chat'))

        else:
            cur_chat = Chat.objects.filter(name=request.user).first()
            messages = ChatMessage.objects.filter(chat=cur_chat)
            message_form = ChatMessageForm(request.POST)

            ChatMessage.objects.filter(chat=cur_chat, read=False, admin=True).update(read=True)

            context = {
                'messages': messages,
                'message_form': message_form,
            }

            return render(request, 'support/customer_chat.html', context)
    else:
        return render(request, 'main/nlogin.html')


def admin_chat(request, c_id=None):
    if request.user.is_authenticated and request.user.is_admin:
        unread = {}

        if not c_id or c_id == 0:
            for chat in Chat.objects.all():
                unread[chat.id] = ChatMessage.objects.filter(chat=chat, read=False, admin=False).count()

            context = {
                'chat': None,
                'chats': Chat.objects.all(),
                'unread': unread
            }

            return render(request, 'support/admin_chat.html', context)
        else:
            cur_chat = Chat.objects.filter(id=c_id).first()
            messages = ChatMessage.objects.filter(chat=cur_chat)
            message_form = ChatMessageForm(request.POST)

            ChatMessage.objects.filter(chat=cur_chat, read=False, admin=False).update(read=True)

            for chat in Chat.objects.all():
                unread[chat.id] = ChatMessage.objects.filter(chat=chat, read=False, admin=False).count()

            context = {
                'chat': cur_chat,
                'chats': Chat.objects.all(),
                'unread': unread,
                'messages': messages,
                'message_form': message_form,
            }

            return render(request, 'support/admin_chat.html', context)
    else:
        return render(request, 'main/nlogin.html')


def chat_post_message(request):
    if request.user.is_authenticated:
        chat = Chat.objects.filter(name=request.user).first()
        message_form = ChatMessageForm(request.POST)
        if message_form.is_valid():
            message = ChatMessage.objects.create(
                    chat=chat,
                    name=request.user,
                    message=message_form['message'].value())
            message.save()
        return HttpResponseRedirect(reverse('support:customer_chat'))
    else:
        return render(request, 'main/nlogin.html')


# conversations between admin and user.
def customer_ticket(request, c_id):
    if request.user.is_authenticated:
        ticket = get_object_or_404(Ticket, id=c_id)
        conversations = TicketReply.objects.filter(ticket_id=c_id)

        ticket_title = ticket.sub_title
        ticket_description = ticket.sub_description
        ticket_state = ticket.state

        context = {
            'ticket_id': c_id,
            'ticket_title': ticket_title,
            'ticket_description': ticket_description,
            'ticket_state': ticket_state,
            'ticket_conversation': conversations,
        }

        return render(request, 'support/customer_ticket.html', context)
    else:
        return render(request, 'main/nlogin.html')


# conversations between admin and user.
def admin_ticket(request, c_id):
    if request.user.is_authenticated:
        ticket = get_object_or_404(Ticket, id=c_id)
        conversations = TicketReply.objects.filter(ticket_id=c_id)

        ticket_title = ticket.sub_title
        ticket_description = ticket.sub_description
        ticket_state = ticket.state

        context = {
            'ticket_id': c_id,
            'ticket_title': ticket_title,
            'ticket_description': ticket_description,
            'ticket_state': ticket_state,
            'ticket_conversation': conversations,
        }

        return render(request, 'support/admin_ticket.html', context)
    else:
        return render(request, 'main/nlogin.html')


def create_ticket(request):
    if request.user.is_authenticated:
        return render(request, 'support/create_ticket.html')
    else:
        return render(request, 'main/nlogin.html')


def customer_ticket_list(request):
    if request.user.is_authenticated:
        tickets = Ticket.objects.filter(name=request.user)

        context = {
            'tickets': tickets,
        }

        return render(request, 'support/customer_ticket_list.html',context,)
    else:
        return render(request, 'main/nlogin.html')


def admin_ticket_list(request):
    if request.user.is_authenticated and request.user.is_admin:
        tickets = Ticket.objects.all()

        context = {
            'tickets': tickets,
        }

        return render(request, 'support/admin_ticket_list.html', context)
    else:
        return render(request, 'main/nlogin.html')


def customer_post_ticket(request):
    if request.user.is_authenticated:
        ticket_form = TicketForm(request.POST)
        if ticket_form.is_valid():
            ticket = Ticket.objects.create(
                    name=request.user,
                    sub_title=ticket_form['sub_title'].value(),
                    sub_description=ticket_form['sub_description'].value())
            ticket.save()
        return HttpResponseRedirect(reverse('support:customer_ticket_list'))
    else:
        return render(request, 'main/nlogin.html')


def support_list(request):
    if request.user.is_authenticated:
        return render(request, 'support/support_list.html')
    else:
        return render(request, 'main/nlogin.html')


def customer_ticket_reply(request):
    if request.user.is_authenticated:
        ticket_form = TicketReplayForm(request.POST)
        ticket = TicketReply.objects.create(
                sub_description=ticket_form['sub_description'].value(),
                ticket_id=ticket_form['ticket_id'].value(),)
        ticket.save()
        return HttpResponseRedirect(reverse('support:customer_ticket', args=(ticket_form['ticket_id'].value(),)))
    else:
        return render(request, 'main/nlogin.html')


def admin_ticket_reply(request):
    if request.user.is_authenticated and request.user.is_admin:
        ticket_form = TicketReplayForm(request.POST)
        ticket = TicketReply.objects.create(
            sub_description=ticket_form['sub_description'].value(),
            ticket_id=ticket_form['ticket_id'].value(),
            admin=1)
        ticket.save()
        return HttpResponseRedirect(reverse('support:admin_ticket', args=(ticket_form['ticket_id'].value(),)))
    else:
        return render(request, 'main/nlogin.html')


def ticket_state_change(request, state, ticket_id, is_admin):
    if request.user.is_authenticated:
        Ticket.objects.filter(id=ticket_id).update(state=state)
        if is_admin:
            return HttpResponseRedirect(reverse('support:admin_ticket_list'))
        else:
            return HttpResponseRedirect(reverse('support:customer_ticket_list'))
    else:
        return render(request, 'main/nlogin.html')







