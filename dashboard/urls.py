from django.conf.urls import url, include
from dynamic_preferences.api.viewsets import GlobalPreferencesViewSet
from rest_framework import routers

from .views import *

router = routers.SimpleRouter()
router.register(r'global', GlobalPreferencesViewSet, base_name='global')

urlpatterns = [
    url(r'^premium$', tube_find),
    url(r'^tube$', tube),
    url(r'^tube/(?P<tube_id>\d+)$', tube),
    url(r'^manage/', include(router.urls, namespace='manage')),
    url(r'^management/exchange/(?P<exchange>[0-9a-zA-Z]+)/walletaddress$', wallet_address_list),
    url(r'^management/exchange/(?P<exchange>[0-9a-zA-Z]+)/walletaddress/(?P<coin_symbol>[0-9a-zA-Z]+)$', wallet_address)
]
