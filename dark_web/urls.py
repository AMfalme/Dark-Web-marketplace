from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf.urls import url
from django.views.generic import RedirectView
from accounts import views as account_views
from vendor import views as vendor_views
from main import views as product_views

urlpatterns = [
    path('alibaba/', admin.site.urls),
    path('support/', include('support.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^signup/$', account_views.signup, name='signup'),
    url(r'^signin/$', account_views.LoginView.as_view(), name='signin'),
    url(r'^signin/gpg_auth/$', account_views.gpg_auth, name='gpg_auth'),
    url(r'^signin/gpg_verify/$', account_views.gpg_verify, name='gpg_verify'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^accounts/login/$', RedirectView.as_view(url='/signin')),
    url(r'^profile/update_tfalogin', account_views.update_tfalogin, name='update_tfalogin'),
    # Vendor Urls
    url(r'^vendor/add_product', vendor_views.add_product, name='user_vendor_add_product'),
    url(r'^vendor/save_product', vendor_views.save_product, name='user_vendor_save_product'),
    url(r'^vendor/delete_product/(?P<product_id>\d+)/$', vendor_views.delete_product, name='user_vendor_delete_product'),
    url(r'^vendor/edit_product/(?P<product_id>\d+)/$', vendor_views.edit_product, name='user_vendor_edit_product'),
    url(r'^vendor/shipping_options/$', vendor_views.shipping_options, name='shipping_options'),
    url(r'^vendor/update_product/$', vendor_views.update_product, name='user_vendor_updateProduct'),
    url(r'^vendor/list_products', vendor_views.list_products, name='user_vendor_listProducts'),
    url(r'^vendor_profile/(?P<id>\d+)/', account_views.vendor_profile, name='vendor_profile'),
    url(r'^vendor_public_profile/(?P<id>\d+)/', account_views.vendor_public_profile, name='vendor_public_profile'),
    url(r'^vendor/newOrders/$', vendor_views.VendorNewOrderListView.as_view(), name='vendor_list_new_order'),
    url(r'^vendor/newOrders/(?P<order_id>\d+)/$', vendor_views.VendorNewOrderDetailView.as_view(), name='vendor_detail_new_order'),
    url(r'^vendor/shipOrders/$', vendor_views.VendorShippedOrderListView.as_view(), name='vendor_list_ship_order'),
    url(r'^vendor/shipOrders/(?P<order_id>\d+)/$', vendor_views.VendorShippedOrderDetailView.as_view(), name='vendor_detail_ship_order'),
    url(r'^vendor/completeOrders/$', vendor_views.VendorCompleteOrderListView.as_view(), name='vendor_list_complete_order'),
    url(r'^vendor/completeOrders/(?P<order_id>\d+)/$', vendor_views.VendorCompleteOrderDetailView.as_view(), name='vendor_detail_complete_order'),
    url(r'^vendor/cancelOrders/$', vendor_views.VendorCancelOrderListView.as_view(), name='vendor_list_cancel_order'),
    url(r'^vendor/cancelOrders/(?P<order_id>\d+)/$', vendor_views.VendorCancelOrderDetailView.as_view(), name='vendor_detail_cancel_order'),
    url(r'^vendor/disputeOrders/$', vendor_views.VendorDisputeOrderListView.as_view(), name='vendor_list_dispute_order'),
    url(r'^vendor/disputeOrders/(?P<order_id>\d+)/$', vendor_views.VendorDisputeOrderDetailView.as_view(), name='vendor_detail_dispute_order'),
    url(r'^vendor/acceptOrder/(?P<order_id>\d+)/$', vendor_views.accept_order, name='vendor_accept_order'),
    url(r'^vendor/rejectOrder/(?P<order_id>\d+)/$', vendor_views.reject_order, name='vendor_reject_order'),

    # Search url
    url(r'^search/$', product_views.search, name='search'),
    # path('accounts/', include('django.contrib.auth.urls')),

    url(r'^messages/$', product_views.UserMessageListView.as_view(), name='message_list'),

    # Inbox url
    url(r'^inbox/$', product_views.UserInboxListView.as_view(), name='inbox_list'),
    url(r'^inbox/(?P<message_id>\d+)/delete/$', product_views.delete_message, name='inbox_delete_message'),
    url(r'^inbox/send/$', product_views.inbox_send, name='inbox_send'),
    url(r'^inbox/send/(?P<receiver_id>\d+)/$', product_views.inbox_send, name='inbox_send'),

    path('account/', include('accounts.urls')),
    url(r'^accounts/$', RedirectView.as_view(url='/account')),  # Redirects url "/accounts" to "/account"

    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('background/', include('background.urls')),
    path('', include('main.urls')),
    # Star Rating Url
    url(r'^ratings/', include('star_ratings.urls', namespace='ratings')),

    # Avatar
    url(r'^avatar/', include('avatar.urls')),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),

                      # For django versions before 2.0:
                      # url(r'^__debug__/', include(debug_toolbar.urls)),

                  ] + urlpatterns
