from attachments.forms import AttachmentForm
from attachments.views import add_url_for_obj
from django.core.urlresolvers import reverse
from django import template

register = template.Library()

@register.inclusion_tag('attachments/delete_link.html', takes_context=True)
def story_attachment_delete_link(context, story, attachment):
    """ 
    modelled after built in version, but with working redirection.
    """
    if context['user'].has_perm('delete_foreign_attachments') \
       or (context['user'] == attachment.creator and \
           context['user'].has_perm('attachments.delete_attachment')):
        return {
            'next':  reverse("iteration", args=[story.iteration.project.slug, story.iteration.id]) + "#story_" + str(story.id),
            'delete_url': reverse('delete_attachment', kwargs={'attachment_pk': attachment.pk})
        }
    return {'delete_url': None,}



@register.inclusion_tag('attachments/add_form.html', takes_context=True)
def story_attachment_form(context, story):
    """
    modelled after built in version, but with working redirection.
    """
    if context['user'].has_perm('attachments.add_attachment'):
        return {
            'form': AttachmentForm(),
            'form_url': add_url_for_obj(story),
            'next': reverse("iteration", args=[story.iteration.project.slug, story.iteration.id]) + "#story_" + str(story.id),
        }
    else:
        return {
            'form': None,
        }
