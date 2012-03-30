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
from knesset.laws.templatetags.laws_extra import recent_votes_count, recent_discipline, recent_coalition_discipline
from knesset.links.views import get_object_links_context

from knesset.video.utils import get_videos_queryset
from datetime import date, timedelta

import logging


logger = logging.getLogger("open-knesset.mks")

class MemberListView(ListView):

    model = Member

    def get_template_names(self):
        info = self.request.GET.get('info','bills_pre')
        if info=='abc':
            return ['mks/member_list.html']
        elif info=='graph':
            return ['mks/member_graph.html']
        else:
            return ['mks/member_list_with_bars.html']

    def get_context_data(self, **kwargs):
        info = self.request.GET.get('info','bills_pre')
        if info not in ['abc','bills_proposed','bills_pre',
                        'bills_first','bills_approved','votes',
                        'presence','committees','graph']:
            raise Http404()
        original_context = super(MemberListView, self).get_context_data(**kwargs)
        qs = original_context['object_list'].filter(is_current=True)

        context = cache.get('object_list_by_%s' % info) or {}
        if context:
            original_context.update(context)
            return original_context
        context['past_mks'] = Member.objects.filter(is_current=False)

        context['friend_pages'] = [['.?info=abc',_('By ABC'), False],
                              ['.?info=bills_proposed',_('By number of bills proposed'), False],
                              ['.?info=bills_pre',_('By number of bills pre-approved'), False],
                              ['.?info=bills_first',_('By number of bills first-approved'), False],
                              ['.?info=bills_approved',_('By number of bills approved'), False],
                              ['.?info=votes', _('By number of votes per month'), False],
                              ['.?info=presence', _('By average weekly hours of presence'), False],
                              ['.?info=committees', _('By average monthly committee meetings'), False],
                              ['.?info=graph', _('Graphical view'), False]]
        if info=='abc':
            context['friend_pages'][0][2] = True
            context['title'] = _('Members')
        elif info=='bills_proposed':
            qs = list(qs)
            for x in qs:
                x.extra = x.bills.count()
                x.bill_stage = 'proposed'
            qs.sort(key=lambda x:x.extra, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.bills.count()
                x.bill_stage = 'proposed'
            context['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            context['friend_pages'][1][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0
            context['title'] = "%s %s" % (_('Members'), _('By number of bills proposed'))
        elif info=='bills_pre':
            qs = list(qs)
            for x in qs:
                x.extra = x.bills.filter(Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
                x.bill_stage = 'pre'
            qs.sort(key=lambda x:x.extra, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.bills.filter(Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
                x.bill_stage = 'pre'
            context['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            context['friend_pages'][2][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0
            context['title'] = "%s %s" % (_('Members'), _('By number of bills pre-approved'))
        elif info=='bills_first':
            qs = list(qs)
            for x in qs:
                x.extra = x.bills.filter(Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
                x.bill_stage = 'first'
            qs.sort(key=lambda x:x.extra, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.bills.filter(Q(stage='4')|Q(stage='5')|Q(stage='6')).count()
                x.bill_stage = 'first'
            context['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            context['friend_pages'][3][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0
            context['title'] = "%s %s" % (_('Members'), _('By number of bills first-approved'))
        elif info=='bills_approved':
            qs = list(qs)
            for x in qs:
                x.extra = x.bills.filter(stage='6').count()
                x.bill_stage = 'approved'
            qs.sort(key=lambda x:x.extra, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.bills.filter(stage='6').count()
                x.bill_stage = 'approved'
            context['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            context['friend_pages'][4][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0
            context['title'] = "%s %s" % (_('Members'), _('By number of bills approved'))
        elif info=='votes':
            qs = list(qs)
            vs = list(MemberVotingStatistics.objects.all())
            vs = dict(zip([x.member_id for x in vs],vs))
            for x in qs:
                x.extra = vs[x.id].average_votes_per_month()
            qs.sort(key=lambda x:x.extra, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.voting_statistics.average_votes_per_month()
            context['past_mks'].sort(key=lambda x:x.extra, reverse=True)
            context['friend_pages'][5][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0
            context['title'] = "%s %s" % (_('Members'), _('By number of votes per month'))
        elif info=='presence':
            qs = list(qs)
            for x in qs:
                x.extra = x.average_weekly_presence()
            qs.sort(key=lambda x:x.extra or 0, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.average_weekly_presence()
            context['past_mks'].sort(key=lambda x:x.extra or 0, reverse=True)
            context['friend_pages'][6][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0
            context['title'] = "%s %s" % (_('Members'), _('By average weekly hours of presence'))
        elif info=='committees':
            qs = list(qs)
            for x in qs:
                x.extra = x.committee_meetings_per_month()
            qs.sort(key=lambda x:x.extra or 0, reverse=True)
            context['past_mks'] = list(context['past_mks'])
            for x in context['past_mks']:
                x.extra = x.committee_meetings_per_month()
            context['past_mks'].sort(key=lambda x:x.extra or 0, reverse=True)
            context['friend_pages'][7][2] = True
            context['norm_factor'] = float(qs[0].extra)/50.0
            context['title'] = "%s %s" % (_('Members'), _('By average monthly committee meetings'))
        elif info=='graph':
            context['friend_pages'][8][2] = True
            context['title'] = "%s %s" % (_('Members'), _('Graphical view'))
        context['object_list']=qs
        cache.set('object_list_by_%s' % info, context, 900)
        original_context.update(context)
        return original_context

class MemberDetailView(FutureDetailView):

    model = Member

    # this classmethod is called from AgendaDetailView
    get_li_context = classmethod(lambda cls, mk: dict(id = mk.id,
        name        = mk.name,
        url         = mk.get_absolute_url(),
        party_id    = mk.current_party.id,
        party_name  = mk.current_party.name,
        ))

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
        
    def get_agendas_context(self,member,is_cached):
        if not is_cached and self.request.user.is_authenticated():
            agendas = Agenda.objects.get_selected_for_instance(member, user=self.request.user, top=3, bottom=3)
        else:
            agendas = Agenda.objects.get_selected_for_instance(member, user=None, top=3, bottom=3)
        agendas = agendas['top'] + agendas['bottom']
        for agenda in agendas:
            agenda.watched=False
        if not is_cached and self.request.user.is_authenticated():
            watched_agendas = self.request.user.get_profile().agendas
            for watched_agenda in watched_agendas:
                if watched_agenda in agendas:
                    agendas[agendas.index(watched_agenda)].watched = True
                else:
                    watched_agenda.score = watched_agenda.member_score(member)
                    watched_agenda.watched = True
                    agendas.append(watched_agenda)
        agendas.sort(key=attrgetter('score'), reverse=True)
        agendas_objects=agendas
        agendas=[]
        for agenda in agendas_objects:
            agendas.append({
                'id':agenda.id,
                'watched':agenda.watched,
                'agenda-detail-url':reverse('agenda-detail',args=[agenda.id]),
                'name':agenda.name,
                'public_owner_name':agenda.public_owner_name,
                'score':agenda.score,
                'mk-agenda-detail-url':reverse('mk-agenda-detail',args=[agenda.id,member.id]),
            })
        return agendas

    def get_context_data (self, object):
        member=object
        cache_key = 'member_detail_%s' % member.id
        context = cache.get(cache_key)
        if not context:
            context = dict(
                name=member.name,
                backlinks_enabled=member.backlinks_enabled,
                pingback_url=reverse('pingback-server'),
                member_trackback=reverse('member-trackback',args=[member.id]),
                absolute_url=member.get_absolute_url(),
                title=member.title(),
                img_url=member.img_url,
                current_party=dict(
                    id=member.current_party.id,
                    party_detail_url=reverse('party-detail',args=[object.current_party.id]),
                    name=member.current_party.name,
                    is_coalition=member.current_party.is_coalition,
                ),
                role=member.get_role,
                date_of_death=unicode(member.date_of_death),
                date_of_birth=unicode(member.date_of_birth),
                year_of_aliyah=unicode(member.year_of_aliyah),
                family_status=member.family_status,
                place_of_birth=member.place_of_birth,
                place_of_residence=member.place_of_residence,
                residence_centrality=member.residence_centrality,
                residence_economy=member.residence_economy,
                is_current=member.is_current,
                phone=member.phone,
                fax=member.fax,
                email=member.email,
                voting_statistics=dict(
                    votes_count=member.voting_statistics.votes_count(),
                    discipline=member.voting_statistics.discipline(),
                    coalition_discipline=member.voting_statistics.coalition_discipline(),
                ),
                recent_votes_count=recent_votes_count(member),
                is_female=member.is_female(),
                recent_discipline=unicode(recent_discipline(member)),
                recent_coalition_discipline=unicode(recent_coalition_discipline(member)),
                committee_meetings_per_month=member.committee_meetings_per_month(),
                links=get_object_links_context(member),
                member_trackback_url=reverse('member-trackback',args=[member.id]),
            )
            
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
            bills_tags=[]
            for bills_tag_object in bills_tags_objects:
                bills_tags.append({
                    'url':reverse('bill-tag',args=[bills_tag_object.id]),
                    'title':unicode(bills_tag_object),
                    'font_size':bills_tag_object.font_size,
                })
                
            agendas=self.get_agendas_context(member,is_cached=True)
                
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
                    'bills_tags':bills_tags,
                    'agendas':agendas,
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
        
        # add non-cached attributes
        
        if self.request.user.is_authenticated():
            p = self.request.user.get_profile()
            watched = member in p.members
        else:
            watched = False
        context.update({'watched_member': watched})   
        
        if self.request.user.is_authenticated():
            context.update({'agendas':self.get_agendas_context(member,is_cached=False)})

        return context

class PartyListView(ListView):

    model = Party

    def get_context_data(self, **kwargs):
        context = super(PartyListView, self).get_context_data(**kwargs)
        qs = context['object_list']
        info = self.request.GET.get('info','seats')
        context['coalition'] = qs.filter(is_coalition=True)
        context['opposition'] = qs.filter(is_coalition=False)
        context['friend_pages'] = [['.',_('By Number of seats'), False],
                              ['.?info=votes-per-seat', _('By votes per seat'), False],
                              ['.?info=discipline', _('By factional discipline'), False],
                              ['.?info=coalition-discipline', _('By coalition/opposition discipline'), False],
                              ['.?info=residence-centrality', _('By residence centrality'), False],
                              ['.?info=residence-economy', _('By residence economy'), False],
                              ['.?info=bills-proposed', _('By bills proposed'), False],
                              ['.?info=bills-pre', _('By bills passed pre vote'), False],
                              ['.?info=bills-first', _('By bills passed first vote'), False],
                              ['.?info=bills-approved', _('By bills approved'), False],
                              ['.?info=presence', _('By average weekly hours of presence'), False],
                              ['.?info=committees', _('By average monthly committee meetings'), False],
                              ]

        if info:
            if info=='seats':
                context['coalition']  =  context['coalition'].annotate(extra=Sum('number_of_seats')).order_by('-extra')
                context['opposition'] = context['opposition'].annotate(extra=Sum('number_of_seats')).order_by('-extra')
                context['friend_pages'][0][2] = True
                context['norm_factor'] = 1
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties'))
            if info=='votes-per-seat':
                m = 0
                for p in context['coalition']:
                    p.extra = p.voting_statistics.votes_per_seat()
                    if p.extra > m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = p.voting_statistics.votes_per_seat()
                    if p.extra > m:
                        m = p.extra
                context['friend_pages'][1][2] = True
                context['norm_factor'] = m/20
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties'))

            if info=='discipline':
                m = 100
                for p in context['coalition']:
                    p.extra = p.voting_statistics.discipline()
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = p.voting_statistics.discipline()
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][2][2] = True
                context['norm_factor'] = (100.0-m)/15
                context['baseline'] = m - 2
                context['title'] = "%s" % (_('Parties'))

            if info=='coalition-discipline':
                m = 100
                for p in context['coalition']:
                    p.extra = p.voting_statistics.coalition_discipline()
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = p.voting_statistics.coalition_discipline()
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][3][2] = True
                context['norm_factor'] = (100.0-m)/15
                context['baseline'] = m - 2
                context['title'] = "%s" % (_('Parties'))

            if info=='residence-centrality':
                m = 10
                for p in context['coalition']:
                    rc = [member.residence_centrality for member in p.members.all() if member.residence_centrality]
                    p.extra = round(float(sum(rc))/len(rc),1)
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    rc = [member.residence_centrality for member in p.members.all() if member.residence_centrality]
                    p.extra = round(float(sum(rc))/len(rc),1)
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][4][2] = True
                context['norm_factor'] = (10.0-m)/15
                context['baseline'] = m-1
                context['title'] = "%s" % (_('Parties by residence centrality'))

            if info=='residence-economy':
                m = 10
                for p in context['coalition']:
                    rc = [member.residence_economy for member in p.members.all() if member.residence_economy]
                    p.extra = round(float(sum(rc))/len(rc),1)
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    rc = [member.residence_economy for member in p.members.all() if member.residence_economy]
                    p.extra = round(float(sum(rc))/len(rc),1)
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][5][2] = True
                context['norm_factor'] = (10.0-m)/15
                context['baseline'] = m-1
                context['title'] = "%s" % (_('Parties by residence economy'))

            if info=='bills-proposed':
                m = 9999
                for p in context['coalition']:
                    p.extra = len(set(Bill.objects.filter(proposers__current_party=p).values_list('id',flat=True)))/p.number_of_seats
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = len(set(Bill.objects.filter(proposers__current_party=p).values_list('id',flat=True)))/p.number_of_seats
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][6][2] = True
                context['norm_factor'] = m/2
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties by number of bills proposed per seat'))

            if info=='bills-pre':
                m = 9999
                for p in context['coalition']:
                    p.extra = round(float(len(set(Bill.objects.filter(Q(proposers__current_party=p),Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).values_list('id',flat=True))))/p.number_of_seats,1)
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = round(float(len(set(Bill.objects.filter(Q(proposers__current_party=p),Q(stage='2')|Q(stage='3')|Q(stage='4')|Q(stage='5')|Q(stage='6')).values_list('id',flat=True))))/p.number_of_seats,1)
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][7][2] = True
                context['norm_factor'] = m/2
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties by number of bills passed pre vote per seat'))

            if info=='bills-first':
                m = 9999
                for p in context['coalition']:
                    p.extra = round(float(len(set(Bill.objects.filter(Q(proposers__current_party=p),Q(stage='4')|Q(stage='5')|Q(stage='6')).values_list('id',flat=True))))/p.number_of_seats,1)
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = round(float(len(set(Bill.objects.filter(Q(proposers__current_party=p),Q(stage='4')|Q(stage='5')|Q(stage='6')).values_list('id',flat=True))))/p.number_of_seats,1)
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][8][2] = True
                context['norm_factor'] = m/2
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties by number of bills passed first vote per seat'))

            if info=='bills-approved':
                m = 9999
                for p in context['coalition']:
                    p.extra = round(float(len(set(Bill.objects.filter(proposers__current_party=p,stage='6').values_list('id',flat=True))))/p.number_of_seats,1)
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    p.extra = round(float(len(set(Bill.objects.filter(proposers__current_party=p,stage='6').values_list('id',flat=True))))/p.number_of_seats,1)
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][9][2] = True
                context['norm_factor'] = m/2
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties by number of bills passed approved per seat'))

            if info=='presence':
                m = 9999
                for p in context['coalition']:
                    awp = [member.average_weekly_presence() for member in p.members.all() if member.average_weekly_presence()]
                    if awp:
                        p.extra = round(float(sum(awp))/len(awp),1)
                    else:
                        p.extra = 0
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    awp = [member.average_weekly_presence() for member in p.members.all() if member.average_weekly_presence()]
                    if awp:
                        p.extra = round(float(sum(awp))/len(awp),1)
                    else:
                        p.extra = 0
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][10][2] = True
                context['norm_factor'] = m/2
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties by average weekly hours of presence'))

            if info=='committees':
                m = 9999
                for p in context['coalition']:
                    cmpm = [member.committee_meetings_per_month() for member in p.members.all() if member.committee_meetings_per_month()]
                    if cmpm:
                        p.extra = round(float(sum(cmpm))/len(cmpm),1)
                    else:
                        p.extra = 0
                    if p.extra < m:
                        m = p.extra
                for p in context['opposition']:
                    cmpm = [member.committee_meetings_per_month() for member in p.members.all() if member.committee_meetings_per_month()]
                    if cmpm:
                        p.extra = round(float(sum(cmpm))/len(cmpm),1)
                    else:
                        p.extra = 0
                    if p.extra < m:
                        m = p.extra
                context['friend_pages'][11][2] = True
                context['norm_factor'] = m/2
                context['baseline'] = 0
                context['title'] = "%s" % (_('Parties by monthly committee meetings'))

        return context

class PartyDetailView(FutureDetailView):
    model = Party

    get_li_context = classmethod(lambda cls, party: dict(id = party.id,
        name        = party.name,
        url         = party.get_absolute_url(),
        ))

    def get_context_data (self, object):
        party=object
        cache_key = 'party_detail_%s' % party.id
        context = cache.get(cache_key)
        if not context:
            context = {}
            party = context['object']
            context['maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
    
            if self.request.user.is_authenticated():
                agendas = Agenda.objects.get_selected_for_instance(party, user=self.request.user, top=3, bottom=3)
            else:
                agendas = Agenda.objects.get_selected_for_instance(party, user=None, top=3, bottom=3)
            agendas = agendas['top'] + agendas['bottom']
            for agenda in agendas:
                agenda.watched=False
            if self.request.user.is_authenticated():
                watched_agendas = self.request.user.get_profile().agendas
                for watched_agenda in watched_agendas:
                    if watched_agenda in agendas:
                        agendas[agendas.index(watched_agenda)].watched = True
                    else:
                        watched_agenda.score = watched_agenda.party_score(party)
                        watched_agenda.watched = True
                        agendas.append(watched_agenda)
            agendas.sort(key=attrgetter('score'), reverse=True)
    
            context.update({'agendas':agendas})
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
