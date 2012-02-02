from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from models import Comite

class ComiteDetailView(DetailView):
    model = Comite
    context_object_name = 'comite'

class ComiteListView(ListView):
    model = Comite
    context_object_name = 'comites'

