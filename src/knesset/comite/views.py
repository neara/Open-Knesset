from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from models import Comite

class ComiteDetailView(DetailView):
    model = Comite
    context_object_name = 'comite'

    def get_context_data(self, **kwargs):
        context = super(ComiteDetailView, self).get_context_data(**kwargs)
        context['issues'] = context['comite'].issues.public()
        return context

class ComiteListView(ListView):
    model = Comite
    context_object_name = 'comites'

