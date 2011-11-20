from django.conf import settings
from django.core.urlresolvers import reverse

LOGIN_REDIRECT_URLNAME = getattr(settings, "LOGIN_REDIRECT_URLNAME", '')
import logging

logger = logging.getLogger(__name__)
def get_default_redirect(request, redirect_field_name="next",
        login_redirect_urlname=LOGIN_REDIRECT_URLNAME, default_redirect_to=None):
    """
    Returns the URL to be used in login procedures by looking at different
    values in the following order:

    - LOGIN_REDIRECT_URLNAME - the name of a URLconf entry in the settings
    - LOGIN_REDIRECT_URL - the URL in the setting
    - a REQUEST value, GET or POST, named "next" by default.
    """
    if default_redirect_to == None:
        if login_redirect_urlname:
            default_redirect_to = reverse(login_redirect_urlname)
        else:
            default_redirect_to = settings.LOGIN_REDIRECT_URL
    redirect_to = request.GET.get(redirect_field_name)
    if not redirect_to:
        redirect_to = request.POST.get(redirect_field_name)
        
    logger.debug("=> %s, %s, %s" % (default_redirect_to, redirect_to, redirect_field_name))
    
    
    
    # light security check -- make sure redirect_to isn't garabage.
    if (not redirect_to) or ("://" in redirect_to) or (" " in redirect_to):
        redirect_to = default_redirect_to
    return redirect_to
