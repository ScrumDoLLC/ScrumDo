from forms import DeveloperApiKeyForm
from api.models import DeveloperApiKey
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
      
         
    