from django.contrib.contenttypes import generic
from models import Event

def EventsField(**kwargs):
    return generic.GenericRelation(Event, content_type_field="which_type",
       object_id_field="which_pk", **kwargs)

