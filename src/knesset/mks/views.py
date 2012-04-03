import urllib
from operator import attrgetter

from django.conf import settings
from django.db.models import Sum, Q
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic import ListView
from django.core.cache import cache
from django.utils import simplejson as json
from tagging.models import Tag
from tagging.utils import calculate_cloud
from backlinks.pingback.server import default_server
from actstream import actor_stream
from django.core.urlresolvers import reverse

from knesset.hashnav.detail import DetailView
from knesset.mks.models import Member, Party
from knesset.mks.forms import VerbsForm
from knesset.mks.utils import percentile
from knesset.laws.models import MemberVotingStatistics, Bill, VoteAction
from knesset.agendas.models import Agenda
from simple.views import DetailView as FutureDetailView
from simple.views import ListView as FutureListView
from knesset.links.views import get_object_links_context
from knesset.agendas.utils import get_agenda_ids_for_model

from knesset.video.utils import get_videos_queryset
from datetime import date, timedelta

import logging


logger = logging.getLogger("open-knesset.mks")

class MemberListView(FutureListView):

    model = Member

    @classmethod
    def get_mks_context(cls,mks):
        members=[]
        for mk in mks:
            members.append(MemberDetailView.get_li_context(mk))
        return members

    def get_context_data(self, **kwargs):
        original_context = super(MemberListView, self).get_context_data(**kwargs)
        qs = original_context['object_list']
        return dict(
            members=MemberListView.get_mks_context(qs.all())
        )

class MemberDetailView(FutureDetailView):

    model = Member

    @classmethod
    def get_li_context(cls,member):
        cx=dict(
            id = member.id,
            name = member.name,
            url = member.get_absolute_url(),
            img_url=member.img_url,
            role=member.get_role,
            is_current=member.is_current,
            party=member.current_party.id,
            residence_centrality=member.residence_centrality,
            residence_economy=member.residence_economy,
            average_weekly_presence=member.average_weekly_presence(),
            committee_meetings_per_month=member.committee_meetings_per_month(),
            num_bills=dict(
                proposed=member.bills.count(),
                pre=member.bills.filter(Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).count(),
                first=member.bills.filter(Q(stage='4')|Q(stage='5')|Q(stage='6')).count(),
                approved=member.bills.filter(stage='6').count(),
            ),
            average_votes_per_month=member.voting_statistics.average_votes_per_month(),
        )
        return cx

    def calc_percentile(self,member,outdict,inprop,outvalprop,outpercentileprop):
        all_members = Member.objects.filter(is_current=True)
        member_count = float(all_members.count())

        member_val = getattr(member,inprop) or 0

        get_inprop = lambda x: getattr(x,inprop) or 0
        avg = sum(map(get_inprop, all_members))
        avg = avg / member_count
        var = sum(map(lambda x: (get_inprop(x)-avg)**2, all_members))
        var = var / member_count

        outdict[outvalprop] = member_val
        outdict[outpercentileprop] = percentile(avg,var,member_val) if var != 0 else 0

    def calc_bill_stats(self,member,bills_statistics,stattype):
        self.calc_percentile( member,
                              bills_statistics,
                              'bills_stats_%s' % stattype,
                              stattype,
                              '%s_percentile' % stattype)

    def get_voteaction_context(self,voteaction):
        return {
            'get_type_display':voteaction.get_type_display(),
            'vote_url':voteaction.vote.get_absolute_url(),
            'vote_title':voteaction.vote.title,
        }
        
    def get_context_data (self, object):
        member=object
        cache_key = 'member_detail_%s' % member.id
        context = cache.get(cache_key)
        if not context:
            context=MemberDetailView.get_li_context(member)
            context.update(dict(
                backlinks_enabled=member.backlinks_enabled,
                pingback_url=reverse('pingback-server'),
                member_trackback=reverse('member-trackback',args=[member.id]),
                title=member.title(),
                current_party_id=member.current_party.id,
                date_of_death=unicode(member.date_of_death),
                date_of_birth=unicode(member.date_of_birth),
                year_of_aliyah=unicode(member.year_of_aliyah),
                family_status=member.family_status,
                place_of_birth=member.place_of_birth,
                place_of_residence=member.place_of_residence,
                phone=member.phone,
                fax=member.fax,
                email=member.email,
                recent_votes_count=member.voting_statistics.votes_count(date.today() - timedelta(30)),
                is_female=member.is_female(),
                recent_discipline=member.voting_statistics.discipline(date.today() - timedelta(30)),
                recent_coalition_discipline=member.voting_statistics.coalition_discipline(date.today() - timedelta(30)),
                links=get_object_links_context(member),
                member_trackback_url=reverse('member-trackback',args=[member.id]),
                votes_count=member.voting_statistics.votes_count(),
                discipline=member.voting_statistics.discipline(),
                coalition_discipline=member.voting_statistics.coalition_discipline(),
            ))
            
            # TODO: add backlinks
            # I douldn't find how to do it
            backlinks=[]
                        
            bills_statistics = {}
            self.calc_bill_stats(member,bills_statistics,'proposed')
            self.calc_bill_stats(member,bills_statistics,'pre')
            self.calc_bill_stats(member,bills_statistics,'first')
            self.calc_bill_stats(member,bills_statistics,'approved')
            
            bills_tags_objects = Tag.objects.usage_for_queryset(member.bills.all(),counts=True)
            bills_tags_objects = calculate_cloud(bills_tags_objects)
            bills_tag_ids=[]
            for bills_tag_object in bills_tags_objects:
                bills_tag_ids.append(bills_tag_object.id)
                
            agenda_ids=get_agenda_ids_for_model(member)
                
            presence = {}
            self.calc_percentile(member, presence,
                                 'average_weekly_presence_hours',
                                 'average_weekly_presence_hours',
                                 'average_weekly_presence_hours_percentile' )
            self.calc_percentile(member, presence,
                                 'average_monthly_committee_presence',
                                 'average_monthly_committee_presence',
                                 'average_monthly_committee_presence_percentile' )
            
            factional_discipline=[]
            for voteaction in VoteAction.objects.filter(member = member, against_party=True):
                factional_discipline.append(self.get_voteaction_context(voteaction))
            
            votes_against_own_bills=[]
            for voteaction in VoteAction.objects.filter(member=member, against_own_bill=True):
                votes_against_own_bills.append(self.get_voteaction_context(voteaction))
            
            general_discipline_params = { 'member' : member }
            is_coalition = member.current_party.is_coalition
            if is_coalition:
                general_discipline_params['against_coalition'] = True
            else:
                general_discipline_params['against_opposition'] = True
            general_discipline_objects = VoteAction.objects.filter(**general_discipline_params)
            general_discipline=[]
            for voteaction in general_discipline_objects:
                general_discipline.append(self.get_voteaction_context(voteaction))
            
            about_videos=get_videos_queryset(member,group='about')
            if (about_videos.count()>0):
                about_video=about_videos[0]
                about_video_embed_link=about_video.embed_link
                about_video_image_link=about_video.image_link
            else:
                about_video_embed_link=''
                about_video_image_link=''
            
            related_videos=get_videos_queryset(member,group='related')
            related_videos=related_videos.filter(
                Q(published__gt=date.today()-timedelta(days=30))
                | Q(sticky=True)
            ).order_by('sticky').order_by('-published')[0:5]
            related_videos_objects=related_videos
            related_videos=[]
            for video in related_videos_objects:
                related_videos.append({
                    'embed_link':video.embed_link,
                    'image_link':video.small_image_link,
                    'title':video.title,
                    'description':video.description,
                    'link':video.link,
                    'published':unicode(video.published),
                })
            
            context.update({
                    'activity_feed_rss':reverse('member-activity-feed',args=[member.id]),
                    'bills_statistics':bills_statistics,
                    'bills_tag_ids':bills_tag_ids,
                    'agenda_ids':agenda_ids,
                    'presence':presence,
                    'factional_discipline':factional_discipline,
                    'votes_against_own_bills':votes_against_own_bills,
                    'general_discipline':general_discipline,
                    'about_video_embed_link':about_video_embed_link,
                    'about_video_image_link':about_video_image_link,
                    'related_videos':related_videos,
                    'num_related_videos':related_videos_objects.count(),
                    'backlinks':backlinks,
                   })
            
            cache.set(cache_key, context, settings.LONG_CACHE_TIME)
        
        # add non-cached attributes
        
        if self.request.user.is_authenticated():
            p = self.request.user.get_profile()
            watched = member in p.members
        else:
            watched = False
        context.update({'watched_member': watched})   
        
        if self.request.user.is_authenticated():
            context.update({'watched_agenda_ids':get_agenda_ids_for_model(member,self.request.user)})

        return context

class PartyListView(FutureListView):

    model = Party

    @classmethod
    def get_parties_context(cls,parties):
        ans=[]
        for party in parties:
            ans.append(PartyDetailView.get_li_context(party))
        return ans

    def get_context_data(self, **kwargs):
        context = super(PartyListView, self).get_context_data(**kwargs)
        return dict(
            parties=PartyListView.get_parties_context(context['object_list'])
        )

class PartyDetailView(FutureDetailView):
    model = Party

    @classmethod
    def get_li_context(cls,party,without_members=False):
        cx=dict(
            id = party.id,
            name = party.name,
            url = party.get_absolute_url(),
            is_coalition = party.is_coalition,
            number_of_seats = party.number_of_seats,
            votes_per_seat=party.voting_statistics.votes_per_seat(),
            discipline=party.voting_statistics.discipline(),
            coalition_discipline=party.voting_statistics.coalition_discipline(),
            num_bills=dict(
                proposed=Bill.objects.filter(proposers__current_party=party).count(),
                pre=Bill.objects.filter(Q(proposers__current_party=party),Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).count(),
                first=Bill.objects.filter(Q(proposers__current_party=party),Q(stage='4')|Q(stage='5')|Q(stage='6')).count(),
                approved=Bill.objects.filter(proposers__current_party=party,stage='6').count(),
            ),
            member_ids=PartyDetailView.get_member_ids(party)
        )
        rc = [member.residence_centrality for member in party.members.all() if member.residence_centrality]
        if len(rc)>0:
            cx['average_residence_centrality']=float(sum(rc))/len(rc)
        else:
            cx['average_residence_centrality']=0
        rc = [member.residence_economy for member in party.members.all() if member.residence_economy]
        if len(rc)>0:
            cx['average_residence_economy']=float(sum(rc))/len(rc)
        else:
            cx['average_residence_economy']=0
        awp = [member.average_weekly_presence() for member in party.members.all() if member.average_weekly_presence()]
        if len(awp)>0:
            cx['average_weekly_presence']=float(sum(awp))/len(awp)
        else:
            cx['average_weekly_presence']=0
        cmpm = [member.committee_meetings_per_month() for member in party.members.all() if member.committee_meetings_per_month()]
        if len(cmpm)>0:
            cx['average_committee_meetings_per_month']=float(sum(cmpm))/len(cmpm)
        else:
            cx['average_committee_meetings_per_month']=0
        return cx
    
    @classmethod
    def get_member_ids(self,party):
        member_ids=[]
        for member in party.members.all():
            member_ids.append(member.id)
        return member_ids

    def get_context_data (self, object):
        party=object
        cache_key = 'party_detail_%s' % party.id
        context = cache.get(cache_key)
        if not context:
            context = PartyDetailView.get_li_context(party)
            context.update(dict(
                maps_api_key=settings.GOOGLE_MAPS_API_KEY,
                agendas=get_agenda_ids_for_model(party),
            ))
            context['votes_count']=party.voting_statistics.votes_count()
            cache.set(cache_key, context, settings.LONG_CACHE_TIME)
            
        if self.request.user.is_authenticated():
            context['watched_agendas']=get_agenda_ids_for_model(party,self.request.user)
        
        return context


def member_auto_complete(request):
    if request.method != 'GET':
        raise Http404

    if not 'query' in request.GET:
        raise Http404

    suggestions = map(lambda member: member.name, Member.objects.filter(name__icontains=request.GET['query'])[:30])

    result = { 'query': request.GET['query'], 'suggestions':suggestions }

    return HttpResponse(json.dumps(result), mimetype='application/json')


def object_by_name(request, objects):
    name = urllib.unquote(request.GET.get('q',''))
    results = objects.find(name)
    if results:
        return HttpResponseRedirect(results[0].get_absolute_url())
    raise Http404(_('No %(object_type)s found matching "%(name)s".' % {'object_type':objects.model.__name__,'name':name}))

def party_by_name(request):
    return object_by_name(request, Party.objects)

def member_by_name(request):
    return object_by_name(request, Member.objects)

def get_mk_entry(**kwargs):
    ''' in Django 1.3 the pony decided generic views get `pk` rather then
        an `object_id`, so we must be crafty and support either
    '''
    i = kwargs.get('pk', kwargs.get('object_id', False))
    return Member.objects.get(pk=i) if i else None

def mk_is_backlinkable(url, entry):
    if entry:
        return entry.backlinks_enabled
    return False

mk_detail = default_server.register_view(MemberDetailView.as_view(), get_mk_entry, mk_is_backlinkable)
