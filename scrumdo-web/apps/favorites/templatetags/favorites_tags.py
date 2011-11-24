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


from django import template
from datetime import date
from favorites.models import Favorite
from django.template.defaultfilters import stringfilter
from django.conf import settings
import re
import logging

register = template.Library()
logger = logging.getLogger(__name__)




@register.inclusion_tag("favorites/favorite_snippet.html", takes_context=True)
def favorite(context, target):
    fav_type = Favorite.getTargetType(target)
    fav = Favorite.getFavorite( context['request'].user, target )    
    return {'fav_type':fav_type, 'favorite':fav, 'target':target, 'STATIC_URL':settings.SSL_STATIC_URL}
