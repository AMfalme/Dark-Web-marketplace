
from django.conf.urls import url
from . import views

app_name = 'orders'

urlpatterns = [
    url(r'^create/(?P<product_id>\d+)/$', views.order_create, name='order_create'),
    url(r'^(?P<order_id>\d+)/(?P<product_id>\d+)/pay/$', views.pay, name='pay'),
    url(r'^waiting/(?P<order_id>\d+)/(?P<address>[-\w]+)/(?P<cost>\d+\.\d{8})$', views.waiting, name='waiting'),
]
