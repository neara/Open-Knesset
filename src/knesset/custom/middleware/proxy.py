import urllib2
from django.http import HttpResponse
from django.core.urlresolvers import resolve


class ProxyMiddleware(object):
    """
    Checks if a requested url has new identifier and if true
    redirects the request to dev server. On successful response from
    dev, renders the response
    """
    
    def process_request(self, request):
        
        """
        Checking for identifier and redirecting to dev server
        """
        identifier = u'new'
        
        if identifier in request.path:
            
            url = "http://dev.oknesset.org%s" % request.path
            
            try:
                fp = urllib2.urlopen(url)
                #TODO validate all href attr
                
                return HttpResponse(fp.read())
            except urllib2.URLError:
                print 'error'
