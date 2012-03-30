from operator import attrgetter
from models import Agenda
from django.core.urlresolvers import reverse

def get_agendas_context_for_model(obj,user=None):
    # do this import here to prevent some kind of circular import
    from knesset.agendas.views import AgendaDetailView
    if user and user.is_authenticated():
        agendas = Agenda.objects.get_selected_for_instance(obj, user=user, top=3, bottom=3)
    else:
        agendas = Agenda.objects.get_selected_for_instance(obj, user=None, top=3, bottom=3)
    agendas = agendas['top'] + agendas['bottom']
    for agenda in agendas:
        agenda.watched=False
    if user and user.is_authenticated():
        watched_agendas = user.get_profile().agendas
        for watched_agenda in watched_agendas:
            if watched_agenda in agendas:
                agendas[agendas.index(watched_agenda)].watched = True
            else:
                if obj.__class__.__name__=='Member':
                    watched_agenda.score = watched_agenda.member_score(obj)
                elif obj.__class__.__name__=='Party':
                    watched_agenda.score = watched_agenda.party_score(obj)
                watched_agenda.watched = True
                agendas.append(watched_agenda)
    agendas.sort(key=attrgetter('score'), reverse=True)
    agendas_objects=agendas
    agendas=[]
    for agenda_obj in agendas_objects:
        agenda=AgendaDetailView.get_li_context(agenda_obj)
        agenda['watched']=agenda_obj.watched
        agenda['score']=getattr(agenda_obj, 'score', 0)
        if obj.__class__.__name__=='Member':
            agenda['mk-agenda-detail-url']=reverse('mk-agenda-detail',args=[agenda['id'],obj.id])
        agendas.append(agenda)
    return agendas

