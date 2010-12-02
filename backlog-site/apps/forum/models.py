""" 
A basic forum model with corresponding thread/post models.

Just about all logic required for smooth updates is in the save() 
methods. A little extra logic is in views.py.
"""

from django.db import models
import datetime
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
try:
    from markdown import markdown
except ImportError:
    class MarkdownNotFound(Exception):
        def __str__(self):
            return "Markdown is not installed!"
    raise MarkdownNotFound

from forum.managers import ForumManager

class Forum(models.Model):
    """
    Very basic outline for a Forum, or group of threads. The threads
    and posts fielsd are updated by the save() methods of their
    respective models and are used for display purposes.

    All of the parent/child recursion code here is borrowed directly from
    the Satchmo project: http://www.satchmoproject.com/
    """
    groups = models.ManyToManyField(Group, blank=True)
    title = models.CharField(_("Title"), max_length=100)
    slug = models.SlugField(_("Slug"))
    parent = models.ForeignKey('self', blank=True, null=True, related_name='child')
    description = models.TextField(_("Description"))
    threads = models.IntegerField(_("Threads"), default=0, editable=False)
    posts = models.IntegerField(_("Posts"), default=0, editable=False)
    ordering = models.IntegerField(_("Ordering"), blank=True, null=True)

    objects = ForumManager()

    def _get_forum_latest_post(self):
        """This gets the latest post for the forum"""
        if not hasattr(self, '__forum_latest_post'):
            try:
                self.__forum_latest_post = Post.objects.filter(thread__forum__pk=self.id).latest("time")
            except Post.DoesNotExist:
                self.__forum_latest_post = None

        return self.__forum_latest_post
    forum_latest_post = property(_get_forum_latest_post)

    def _recurse_for_parents_slug(self, forum_obj):
        #This is used for the urls
        p_list = []
        if forum_obj.parent_id:
            p = forum_obj.parent
            p_list.append(p.slug)
            more = self._recurse_for_parents_slug(p)
            p_list.extend(more)
        if forum_obj == self and p_list:
            p_list.reverse()
        return p_list

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        p_list = self._recurse_for_parents_slug(self)
        p_list.append(self.slug)
        return '%s%s/' % (reverse('forum_index'), '/'.join (p_list))

    def _recurse_for_parents_name(self, forum_obj):
        #This is used for the visual display & save validation
        p_list = []
        if forum_obj.parent_id:
            p = forum_obj.parent
            p_list.append(p.title)
            more = self._recurse_for_parents_name(p)
            p_list.extend(more)
        if forum_obj == self and p_list:
            p_list.reverse()
        return p_list

    def get_separator(self):
        return ' &raquo; '

    def _parents_repr(self):
        p_list = self._recurse_for_parents_name(self)
        return self.get_separator().join(p_list)
    _parents_repr.short_description = _("Forum parents")

    def _recurse_for_parents_name_url(self, forum__obj):
        #Get all the absolute urls and names (for use in site navigation)
        p_list = []
        url_list = []
        if forum__obj.parent_id:
            p = forum__obj.parent
            p_list.append(p.title)
            url_list.append(p.get_absolute_url())
            more, url = self._recurse_for_parents_name_url(p)
            p_list.extend(more)
            url_list.extend(url)
        if forum__obj == self and p_list:
            p_list.reverse()
            url_list.reverse()
        return p_list, url_list

    def get_url_name(self):
        #Get a list of the url to display and the actual urls
        p_list, url_list = self._recurse_for_parents_name_url(self)
        p_list.append(self.title)
        url_list.append(self.get_absolute_url())
        return zip(p_list, url_list)

    def __unicode__(self):
        return u'%s' % self.title
    
    class Meta:
        ordering = ['ordering', 'title',]
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')

    def save(self, force_insert=False, force_update=False):
        p_list = self._recurse_for_parents_name(self)
        if (self.title) in p_list:
            raise validators.ValidationError(_("You must not save a forum in itself!"))
        super(Forum, self).save(force_insert, force_update)

    def _flatten(self, L):
        """
        Taken from a python newsgroup post
        """
        if type(L) != type([]): return [L]
        if L == []: return L
        return self._flatten(L[0]) + self._flatten(L[1:])

    def _recurse_for_children(self, node):
        children = []
        children.append(node)
        for child in node.child.all():
            children_list = self._recurse_for_children(child)
            children.append(children_list)
        return children

    def get_all_children(self):
        """
        Gets a list of all of the children forums.
        """
        children_list = self._recurse_for_children(self)
        flat_list = self._flatten(children_list[1:])
        return flat_list

class Thread(models.Model):
    """
    A Thread belongs in a Forum, and is a collection of posts.

    Threads can be closed or stickied which alter their behaviour 
    in the thread listings. Again, the posts & views fields are 
    automatically updated with saving a post or viewing the thread.
    """
    forum = models.ForeignKey(Forum)
    title = models.CharField(_("Title"), max_length=100)
    sticky = models.BooleanField(_("Sticky?"), blank=True, default=False)
    closed = models.BooleanField(_("Closed?"), blank=True, default=False)
    posts = models.IntegerField(_("Posts"), default=0)
    views = models.IntegerField(_("Views"), default=0)
    latest_post_time = models.DateTimeField(_("Latest Post Time"), blank=True, null=True)

    def _get_thread_latest_post(self):
        """This gets the latest post for the thread"""
        if not hasattr(self, '__thread_latest_post'):
            try:
                self.__thread_latest_post = Post.objects.filter(thread__pk=self.id).latest("time")
            except Post.DoesNotExist:
                self.__thread_latest_post = None

        return self.__thread_latest_post
    thread_latest_post = property(_get_thread_latest_post)

    class Meta:
        ordering = ('-sticky', '-latest_post_time')
        verbose_name = _('Thread')
        verbose_name_plural = _('Threads')

    def save(self, force_insert=False, force_update=False):
        f = self.forum
        f.threads = f.thread_set.count()
        f.save()
        if not self.sticky:
            self.sticky = False
        super(Thread, self).save(force_insert, force_update)

    def delete(self):
        super(Thread, self).delete()
        f = self.forum
        f.threads = f.thread_set.count()
        f.posts = Post.objects.filter(thread__forum__pk=f.id).count()
        f.save()
    
    def get_absolute_url(self):
        return ('forum_view_thread', [str(self.id)])
    get_absolute_url = models.permalink(get_absolute_url)
    
    def __unicode__(self):
        return u'%s' % self.title

class Post(models.Model):
    """ 
    A Post is a User's input to a thread. Uber-basic - the save() 
    method also updates models further up the heirarchy (Thread,Forum)
    """
    thread = models.ForeignKey(Thread)
    author = models.ForeignKey(User, related_name='forum_post_set')
    body = models.TextField(_("Body"))
    body_html = models.TextField(editable=False)
    time = models.DateTimeField(_("Time"), blank=True, null=True)

    def save(self, force_insert=False, force_update=False):
        if not self.id:
            self.time = datetime.datetime.now()
        
        self.body_html = markdown(escape(self.body))
        super(Post, self).save(force_insert, force_update)

        t = self.thread
        t.latest_post_time = t.post_set.latest('time').time
        t.posts = t.post_set.count()
        t.save()

        f = self.thread.forum
        f.threads = f.thread_set.count()
        f.posts = Post.objects.filter(thread__forum__pk=f.id).count()
        f.save()

    def delete(self):
        try:
            latest_post = Post.objects.exclude(pk=self.id).latest('time')
            latest_post_time = latest_post.time
        except Post.DoesNotExist:
            latest_post_time = None

        t = self.thread
        t.posts = t.post_set.exclude(pk=self.id).count()
        t.latest_post_time = latest_post_time
        t.save()

        f = self.thread.forum
        f.posts = Post.objects.filter(thread__forum__pk=f.id).exclude(pk=self.id).count()
        f.save()

        super(Post, self).delete()

    class Meta:
        ordering = ('-time',)
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        
    def get_absolute_url(self):
        return '%s?page=last#post%s' % (self.thread.get_absolute_url(), self.id)
    
    def __unicode__(self):
        return u"%s" % self.id

class Subscription(models.Model):
    """
    Allow users to subscribe to threads.
    """
    author = models.ForeignKey(User)
    thread = models.ForeignKey(Thread)

    class Meta:
        unique_together = (("author", "thread"),)
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')

    def __unicode__(self):
        return u"%s to %s" % (self.author, self.thread)
