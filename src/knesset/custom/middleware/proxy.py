import logging
import urllib2
from django.http import HttpResponse
from django.core.cache import cache
from custom.help import MyHTMLParser


logger = logging.getLogger('knesset.custom.middleware')


class ProxyMiddleware(object):
    """
    Checks if a requested url has new identifier and if true
    redirects the request to dev server. On successful response from
    dev, validates all links and returns HTTPResponse
    """
    
    def process_request(self, request):
        
        """
        Checking for identifier and redirecting to dev server
        """
        
        if request.GET.get('new') == 'true':
            
            url = "http://dev.oknesset.org%s" % request.path
            resp = cache.get(url)
            if resp is not None:
                logger.info('%s found in cache' % url)
                return HttpResponse(resp.read())

            try:
                fp = urllib2.urlopen(url)
                validator = MyHTMLParser(fp) #validating all hrefs
                if validator.status():
                    logger.info('caching %s' % url)
                    cache.set(url, fp)
                    return HttpResponse(fp.read())
            except urllib2.URLError:
                logger.warning('Failed to retrieve: %s!' % url)
