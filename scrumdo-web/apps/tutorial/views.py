from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext,TemplateDoesNotExist
from django.template.loader import get_template

from os.path import isfile, join

# syntax is name_of_tutorial: {url_of_page: name_of_page...
# this must match the templates found in tutorial/ . ie tutorial/name_of_tutorial/url_of_page.html
tutorials = { "scrumdo":[("start","What Is ScrumDo?"),
                         ("organizations", "Organizations"),
                         ("projects", "Projects"),
                         ("iterations", "Iteration Planning"),
                         ("basecamp", "Basecamp Integration"),
                         ],


              "scrum":[("start", "Start"),
                       ("roles", "Roles"),
                       ("backlog", "Backlog"),
                       ("planning", "Planning"),
                       ("stories", "Stories"),
                       ("releases", "Releases")],
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


def tutorial(request, name, page="start"):
    def mk_path(page):
        return join("tutorial", name, page+".html")
    if not tutorials.has_key(name) or not list_has_key(tutorials[name], page) :
        raise Http404

    return render_to_response("tutorial/base.html", {
            "page_template": mk_path(page),
            "name": name,
            "this": list_get(tutorials[name], page),
            "pages": tutorials[name],
    }, context_instance=RequestContext(request))

def tutorial_print(request, name):
    if not tutorials.has_key(name):
        raise Http404

    return render_to_response("tutorial/print.html", {
            "page_templates" : map(lambda (x,y): join("tutorial", name, x + ".html"), tutorials[name]),
            "name":name,
            "this": ("print", "Print Version"),
            "pages": tutorials[name],
            },
                              context_instance=RequestContext(request))
