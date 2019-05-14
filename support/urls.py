from django.conf.urls import url, include
from . import views

app_name = 'support'

urlpatterns =[

    url(r'^$', views.support_list, name='support_list'),
    url(r'^customer_chat/$', views.customer_chat, name='customer_chat'),
    url(r'^customer_ticket_list/$', views.customer_ticket_list, name='customer_ticket_list'),
    url(r'^customer_ticket/(?P<c_id>\d+)', views.customer_ticket, name='customer_ticket'),
    url(r'^create_ticket/$', views.create_ticket, name='create_ticket'),
    url(r'^chat_post_message/$', views.chat_post_message, name='chat_post_message'),
    url(r'^customer_post_ticket/$', views.customer_post_ticket, name='customer_post_ticket'),
    url(r'^customer_ticket_reply/$', views.customer_ticket_reply, name='customer_ticket_reply'),
    url(r'^ticket_state_change/(?P<state>\d+)/(?P<ticket_id>\d+)/(?P<is_admin>\d+)', views.ticket_state_change, name='ticket_state_change'),

    url(r'^admin_chat/$', views.admin_chat, name='admin_chat'),
    url(r'^admin_chat/(?P<c_id>\d+)', views.admin_chat, name='admin_chat'),
    url(r'^admin_ticket_list/$', views.admin_ticket_list, name='admin_ticket_list'),
    url(r'^admin_ticket/(?P<c_id>\d+)', views.admin_ticket, name='admin_ticket'),
    url(r'^admin_ticket_reply/$', views.admin_ticket_reply, name='admin_ticket_reply'),
]
