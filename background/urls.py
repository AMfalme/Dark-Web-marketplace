from django.conf.urls import url
from . import views

app_name = 'background'

urlpatterns = [
    url(r'^$', views.pull_crypto_price, name='pull_crypto_price'),
]
