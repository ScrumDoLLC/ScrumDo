from forms import DeveloperApiKeyForm
from api.models import DeveloperApiKey, UserApiKey
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
  keys = DeveloperApiKey.objects.filter(developer = request.user)
  return render_to_response("developer/index.html", {
    "keys" : keys,
  })

@login_required
def apply(request):
  form = DeveloperApiKeyForm(request.POST or None)

  if request.method == 'POST':
    if form.is_valid(): # All validation rules pass
      dev_key = form.save( commit=False )
      dev_key.developer = request.user
      dev_key.save()
      request.user.message_set.create(message="Created developer key.")
      return HttpResponseRedirect(reverse("developer_home"))
      
  return render_to_response("developer/apply.html", {
             "form": form,
             })
      
         
@login_required
def user_keys(request):
  if request.method == 'POST' and request.POST.get("key_id"):
    k = UserApiKey.objects.get(pk=request.POST.get("key_id"))
    appname = k.developer_key.application_name
    k.delete()
    request.user.message_set.create(message=("Deleted developer key for application %s." % appname))

  keys = UserApiKey.objects.filter(user = request.user)
  return render_to_response("developer/user_keys.html", {
    "keys" : keys,
  })

