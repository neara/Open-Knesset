from knesset.links.models import Link
from django.conf import settings

def get_object_links_context(obj):
    l = Link.objects.for_model(obj)
    links=[]
    for link in l:
        linktype={}
        if link.link_type:
            linktype=dict(
                image=unicode(link.link_type.image),
                title=link.link_type.title,
            )
        links.append(dict(
            active=link.active,
            url=link.url,
            link_type=linktype,
            title=link.title,
        ))
    return {'links': links, 'MEDIA_URL': settings.MEDIA_URL}