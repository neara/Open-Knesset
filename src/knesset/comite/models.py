from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from djangoratings.fields import RatingField

from links.models import LinksField
from events.models import Event

def EventsField(**kwargs):
    return generic.GenericRelation(Event, content_type_field="which_type",
       object_id_field="which_pk", **kwargs)

class Comite(models.Model):
    ''' Comite - a simpler committee
    '''
    name = models.CharField(max_length=256)
    description = models.TextField(null=True,blank=True, verbose_name=_('Description'))

    concepts = models.ManyToManyField('Concept', related_name='comites', verbose_name=_('Concept'))
    links = LinksField()
    events = EventsField()

    members = models.ManyToManyField(User, related_name='comites', verbose_name=_('Members'))
    chairs = models.ManyToManyField(User, related_name='comites_chairs', verbose_name=_('Chairmans'))

    class Meta:
        verbose_name = _('Committee')
        verbose_name_plural = _('Committees')

    @models.permalink
    def get_absolute_url(self):
        return ('comite-detail', [str(self.id)])

    @models.permalink
    def get_index_url(cls):
        return ('comite-index')

    def __unicode__(self):
        return "%s" % self.name

CONCEPT_PUBLISHED, CONCEPT_FLAGGED, CONCEPT_REJECTED,\
CONCEPT_ACCEPTED, CONCEPT_APPEAL, CONCEPT_DELETED = range(6)
PUBLIC_CONCEPT_STATUS = ( CONCEPT_PUBLISHED, CONCEPT_ACCEPTED)

class Concept(models.Model):
    ''' Concept is used to hold a concept to explore and invistigate '''

    creator = models.ForeignKey(User, related_name='concpets')
    editors = models.ManyToManyField(User, null=True, blank=True, related_name = 'editing_concepts')
    title = models.CharField(max_length=256,
                             verbose_name = _('Title'))
    description = models.TextField(blank=True,
                                   verbose_name = _('Description'))
    status = models.IntegerField(choices = (
        (CONCEPT_PUBLISHED, _('published')),
        (CONCEPT_FLAGGED, _('flagged')),
        (CONCEPT_REJECTED, _('rejected')),
        (CONCEPT_ACCEPTED, _('accepted')),
        (CONCEPT_APPEAL, _('appeal')),
        (CONCEPT_DELETED, _('deleted')),
            ), default=CONCEPT_PUBLISHED)
    rating = RatingField(range=7, can_change_vote=True, allow_delete=True)
    links = LinksField()
    events = EventsField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    log = models.TextField(default="", blank=True)

    class Meta:
        verbose_name = _('Concept')
        verbose_name_plural = _('Concept')

    @models.permalink
    def get_absolute_url(self):
        return ('concept-detail', [str(self.id)])

    def __unicode__(self):
        return "%s" % self.title
