from django.urls import path, include
from django.conf.urls import url

from . import views as account_views
from orders import views as order_views

urlpatterns = [
    path('', include("accounts.passwords.urls")),
    path('accounts/', include('django.contrib.auth.urls')),

    # url(r'^profile/update/pgp-key/$', account_views.UserPgpUpdateView.as_view(), name='user_pgp_update'),

    url(r'^profile/update/change_terms/$', account_views.Changeterms.as_view(), name='change_terms'),
    url(r'^profile/update/pgp-key/$', account_views.UserPgpUpdateView.as_view(), name='user_pgp_update'),
    url(r'^profile/$', account_views.UserProfileView.as_view(), name='user_profile'),
    url(r'^profile/favorite/$', account_views.favorite_detail, name='user_favorites'),
    url(r'^ratings/$', account_views.user_ratings, name='user_ratings'),
    url(r'^profile/vendor_stats/$', account_views.vendor_stats, name='vendor_stats'),


    # User Order(s)
    url(r'^orders/$', account_views.UserOrdersListView.as_view(), name='user_order_list'),
    url(r'^orders/(?P<order_id>\d+)/$', account_views.UserOrderDetailView.as_view(), name='user_order_detail'),
    url(r'^completeOrder/(?P<order_id>\d+)/$', account_views.complete_order, name='user_order_complete'),
    url(r'^disputeOrder/(?P<order_id>\d+)/$', account_views.dispute_order, name='user_order_dispute'),
    url(r'^waiting/(?P<order_id>\d+)/(?P<address>[-\w]+)/(?P<cost>\d+\.\d{8})$', order_views.waiting, name='waiting'),

    # Trust/Untrust
    url(r'^trust/$', account_views.trust_vendor, name='trust_vendor'),
    url(r'^untrust/$', account_views.untrust_vendor, name='untrust_vendor'),

    # Commenting
    url(r'^comment/$', account_views.comment_order_item, name='comment_order_item'),
]
