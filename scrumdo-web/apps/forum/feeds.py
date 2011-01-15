from django.conf import settings
from django.contrib.syndication.feeds import Feed
from django.contrib.syndication.feeds import FeedDoesNotExist
from django.utils.feedgenerator import Atom1Feed
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from forum.models import Forum, Thread, Post

class RssForumFeed(Feed):
    title_template = 'forum/feeds/post_title.html'
    description_template = 'forum/feeds/post_description.html'

    def get_object(self, bits):
        if len(bits) == 0:
            return None
        else:
            slug = "/".join(bits)
            return Forum.objects.get(slug__exact=slug)

    def title(self, obj):
        if not hasattr(self, '_site'):
            self._site = Site.objects.get_current()

        if obj:
            return _("%(title)s's Forum: %(forum)s") % { 
                'title': self._site.name,
                'forum': obj.title }
        else:
            return _("%(title)s's Forum") % {'title': self._site.name}

    def description(self, obj):
        if obj:
            return obj.description
        else:
            return _('Latest forum posts')

    def link(self, obj):
        if obj:
            return obj.get_absolute_url()
        else:
            return reverse('forum_index')

    def get_query_set(self, obj):
        if obj:
            return Post.objects.filter(thread__forum__pk=obj.id).order_by('-time')
        else:
            return Post.objects.order_by('-time')

    def items(self, obj):
        return self.get_query_set(obj)[:15]

    def item_pubdate(self, item):
        return item.time


class AtomForumFeed(RssForumFeed):
    feed_type = Atom1Feed

    def subtitle(self, obj):
        return RssForumFeed.description(self, obj)
