from django.contrib.contenttypes.generic import GenericTabularInline
from links.models import Link
from events.models import Event
from models import *

from django.contrib import admin

class ComiteAdmin(admin.ModelAdmin):
    ordering = ('name',)

admin.site.register(Comite, ComiteAdmin)

class LinksTable(GenericTabularInline):
    model = Link
    ct_field='content_type'
    ct_fk_field='object_pk'

class EventsTable(GenericTabularInline):
    model = Event
    ct_field='which_type'
    ct_fk_field='which_pk'

class IssueAdmin(admin.ModelAdmin):
    ordering = ('-created',)
    inlines = [
        LinksTable,
        EventsTable,
    ]

admin.site.register(Issue, IssueAdmin)
