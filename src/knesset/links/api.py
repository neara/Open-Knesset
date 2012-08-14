from knesset.api.resources.base import BaseResource
from links.models import Link

class LinkResource(BaseResource):
    ''' Party API
    TBD: create a party app
    '''
    class Meta:
        queryset = Link.objects.all()
        allowed_methods = ['get']
        excludes = ["active", "object_pk", "id"]
        include_resource_uri = False
