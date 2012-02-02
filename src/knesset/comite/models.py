from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from links.models import Link
from events.models import Event

class EventsField(models.ManyToManyField):
    ''' use me to add a links field to your model '''
    def __init__(self, *args,**kwargs):
        return super(models.ManyToManyField, self).__init__(Event, *args, **kwargs)

class Comite(models.Model):
    ''' Comite - a simpler committee
    '''
    name = models.CharField(max_length=256)
    description = models.TextField(null=True,blank=True, verbose_name=_('Description'))

    # topics = models.ManyToManyField('Topic', related_name='comites', verbose_name=_('Topics'))
    links = models.ManyToManyField(Link);
    events = generic.GenericRelation(Event, content_type_field="which_type",
       object_id_field="which_pk")

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
        return "%s" % self.title
