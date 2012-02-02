#encoding: UTF-8
from django.conf.urls.defaults import *
# TODO: use this:
from djangoratings.views import AddRatingFromModel

from models import *
from views import *

urlpatterns = patterns ('',
    url(r'^$', ComiteListView.as_view(), name='comite-list'),
    url(r'^(?P<pk>\d+)/$', ComiteDetailView.as_view(), name='comite-detail'),
    url(r'^(?P<slug>\d+)/$', ComiteDetailView.as_view(), name='comite-detail'),
)

