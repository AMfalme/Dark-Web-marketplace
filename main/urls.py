from django.urls import path
from django.conf.urls import url
from . import views as views
from main import views as main_views
from . import views

urlpatterns = [
    url(r'^$', views.product_list, name='product_list'),
    url(r'^category/(?P<category_slug>[-\w]+)/$', views.product_list, name='product_list_by_category'),
    url(r'^subcategory/(?P<subcategory_slug>[-\w]+)/$', views.product_list_by_subcategory, name='product_list_by_subcategory'),
    url(r'^(?P<id>\d+)/(?P<slug>[-\w]+)/$', views.product_detail, name='product_detail'),
]
