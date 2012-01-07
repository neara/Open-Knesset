from django import forms
from django.forms.models import modelformset_factory

from models import Topic
from knesset.links.models import Link
from knesset.events.models import Event

class EditTopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('title', 'description', 'committees')

LinksFormset = modelformset_factory(Link,
                                    can_delete=True,
                                    fields=('url', 'title'),
                                    extra=3)

EventsFormset = modelformset_factory(Event,
                                    can_delete=True,
                                    fields=('when', 'when_over', 'protocol'),
                                    extra=1)

