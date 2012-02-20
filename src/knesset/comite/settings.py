from django.conf import settings

COMITE_AUTO_PUBLISHING = getattr(settings, 'COMITE_AUTO_PUBLISHING', True)
