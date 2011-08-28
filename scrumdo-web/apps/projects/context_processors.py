# ScrumDo - Agile/Scrum story management web application
# Copyright (C) 2011 ScrumDo LLC
#
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy (See file COPYING) of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


from django.conf import settings # import the settings file

import logging

logger = logging.getLogger(__name__)

def projects_constants(request):

    # AWS Does it this way:
    forwarded_ssl = ('HTTP_X_FORWARDED_SSL' in request.META) 
    
    # Other proxy's do it this way:
    if 'HTTP_X_FORWARDED_PROTO' in request.META:
        forwarded_ssl = (request.META['HTTP_X_FORWARDED_PROTO'] == 'https')
                    
    # is_secure for direct ssl request
    if request.is_secure() or forwarded_ssl:
        static_url = settings.SSL_STATIC_URL
    else:
        static_url = settings.STATIC_URL

    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'GOOGLE_ANALYTICS': settings.GOOGLE_ANALYTICS,
            'GOOGLE_ANALYTICS_ACCOUNT': settings.GOOGLE_ANALYTICS_ACCOUNT ,
            'BASE_URL': settings.BASE_URL,
            'SUPPORT_URL': settings.SUPPORT_URL,
            'STATIC_URL':static_url }
