from HTMLParser import HTMLParser
import urllib2
from django.core.urlresolvers import resolve
from django.http import Http404

class MyHTMLParser(HTMLParser):
    def __init__(self, fp):
        """
        fp is an input stream returned by open() or urllib2.urlopen()
        """
        HTMLParser.__init__(self)
        self.seen = {}
        self.is_good = True
        self.feed(fp.read())


    def handle_starttag(self, tag, attrs):
        """
        Looking for href attributes and validating them
        """
        for k, v in attrs:
            if k == 'href' and v not in self.seen:
                self.seen[v] = True
                try:
                    match = resolve(v)
                except Http404:
                    self.is_good = self._check_abs_url(v)
            if not self.is_good:
                return

    def status(self):
        """
        Indicator if all links in current html are working
        """
        return self.is_good

    def _check_abs_url(self, url):
        """
        Checks if a given url can be opened
        """
        try:
            f = urllib2.urlopen(url)
            return True
        except urllib2.URLError:
            return False