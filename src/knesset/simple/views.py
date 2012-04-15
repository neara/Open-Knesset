from django.http import HttpResponse
from django import http
from django.utils import simplejson as json
from django.shortcuts import render_to_response
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from djpjax import PJAXResponseMixin

def hello_world(request):
    return HttpResponse('hello world')

class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)

class DetailView(JSONResponseMixin, PJAXResponseMixin, SingleObjectTemplateResponseMixin, BaseDetailView):
    def render_to_response(self, context):
        # TODO: retunr more than just json
        return JSONResponseMixin.render_to_response(self, context)

class ListView(JSONResponseMixin, PJAXResponseMixin, BaseListView):
    def render_to_response(self, context):
        return JSONResponseMixin.render_to_response(self, context)
