from django.conf.urls import url

from .views import *

urlpatterns = [
    # url(r'^(?P<tid>[0-9a-zA-Z]+)$', fetch_data),
    url(r'^steps', fetch_data),
    url(r'^history/summary', get_history_summary),
    url(r'^history/(?P<tid>[0-9a-zA-Z]+)$', get_history),
]