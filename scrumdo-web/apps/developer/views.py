from forms import DeveloperApiKeyForm
from api.models import DeveloperApiKey, UserApiKey
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.template import RequestContext,TemplateDoesNotExist
from django.template.loader import get_template

from os.path import isfile, join

@login_required
def home(request):
    keys = DeveloperApiKey.objects.filter(developer = request.user)
    return render_to_response("developer/index.html", {
      "keys" : keys,
      "name": "api",
      "pages": docs["api"]
    }, context_instance=RequestContext(request))

@login_required
def apply(request):
    form = DeveloperApiKeyForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid(): # All validation rules pass
            dev_key = form.save( commit=False )
            dev_key.developer = request.user
            dev_key.approved = True
            dev_key.save()
            request.user.message_set.create(message="Created developer key.")
            return HttpResponseRedirect(reverse("developer_home"))

    return render_to_response("developer/apply.html", {
               "form": form,
               "name": "api",
               "pages": docs["api"]
               }, context_instance=RequestContext(request))


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
    }, context_instance=RequestContext(request))

# syntax is name_of_tutorial: {url_of_page: name_of_page...
# this must match the templates found in tutorial/ . ie tutorial/name_of_tutorial/url_of_page.html
docs = { "api":[("start","Getting Started"),
                ("permissions", "Permissions"),
                ("traversing", "Traversing Data"),
                ("updating", "Updating, deleting"),
                ("reference", "API Reference"),
                ],
              }

def list_has_key(lis,key):
    for k,v in lis:
        if k == key:
            return True
    return False

def list_get(lis, key):
    for k,v in lis:
        if k == key:
            return (k,v)
    return None

def docs_page(request, name, page="start"):
    def mk_path(page):
        return join("developer", name, page+".html")
    if not docs.has_key(name) or not list_has_key(docs[name], page) :
        raise Http404

    return render_to_response("developer/base.html", {
            "page_template": mk_path(page),
            "name": name,
            "this": list_get(docs[name], page),
            "pages": docs[name],
    }, context_instance=RequestContext(request))

def docs_print(request, name):
    if not docs.has_key(name):
        raise Http404

    return render_to_response("developer/print.html", {
            "page_templates" : map(lambda (x,y): join("developer", name, x + ".html"), docs[name]),
            "name":name,
            "this": ("print", "Print Version"),
            "pages": docs[name],
            }, context_instance=RequestContext(request))
