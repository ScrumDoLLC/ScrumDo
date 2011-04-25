from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import Authorization


class ScrumDoAuthorization(Authorization):
  def __init__(self, read_q, write_q):
    """
    read_q and write_q are functions that return Q queries that check for read and write access 
    respectively for the resource type in question.
    
    each takes the user in question as its only argument.
    """
    self.read_q = read_q
    self.write_q = write_q
    
  def is_authorized(self, request, object=None):
    # this method is NEVER passed an object currently as far as I can tell (somewhat misleadingly), 
    # so it is useless unless you are doing class level authorization.
    return True

  def apply_limits(self, request, object_list):
    if request and hasattr(request, 'user') and self:
      if request.method == 'GET':
        return object_list.filter(self.read_q(request.user)).distinct()
      elif request.method in ['POST','PUT','DELETE']:
        return object_list.filter(self.write_q(request.user)).distinct()
    else: # if there is no user, then this is an internal call, in which case give it all back
      return object_list.all()

class ScrumDoAuthentication(ApiKeyAuthentication):
  """ Overriding to use more sensible param name for username (as username collides with built in django auth) """
  def is_authenticated(self, request, **kwargs):
      """
      Finds the user and checks their API key.
      
      Should return either ``True`` if allowed, ``False`` if not or an
      ``HttpResponse`` if you need something custom.
      """
      from django.contrib.auth.models import User
      
      username = request.GET.get('api_name') or request.POST.get('api_name')
      api_key = request.GET.get('api_key') or request.POST.get('api_key')
      
      if not username or not api_key:
          return self._unauthorized()
      
      try:
          user = User.objects.get(username=username)
      except (User.DoesNotExist, User.MultipleObjectsReturned):
          return self._unauthorized()
  
      request.user = user
  
      return self.get_key(user, api_key)
      
  def get_identifier(self, request):
      """
      Provides a unique string identifier for the requestor.
      
      This implementation returns the user's username.
      """
      return request.REQUEST.get('api_name', 'no_user')
