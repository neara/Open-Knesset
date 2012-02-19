"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import datetime
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from models import *

now = datetime.datetime.now()

class SimpleTest(TestCase):
    fixtures = ['links']
    def setUp (self):
        self.comite = Comite.objects.create(name='comite')
        self.u1 = User.objects.create(username='abe')

    def test_creation(self):
        """
        Tests the creation of all the models
        """
        self.assertTrue(self.comite.issues.create(title='Hello World'))
        self.assertTrue(self.comite.links.create(url='http://example.com'))
        self.assertTrue(self.comite.events.create(when=now, what='sunrise'))

    def test_comite_list_view(self):
        res = self.client.get(reverse('comite-list'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'comite/comite_list.html')

    def test_comite_detail_view(self):
        res = self.client.get(self.comite.get_absolute_url())
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'comite/comite_detail.html')

    def tearDown(self):
        self.comite.delete()
