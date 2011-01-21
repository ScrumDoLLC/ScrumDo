from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext,TemplateDoesNotExist
from django.template.loader import get_template

from os.path import isfile

def tutorial(request, page=1):
    page = int(page)
    def check_exists(page_num):
        try:
            get_template("tutorial/"+str(page_num)+".html")
        except TemplateDoesNotExist:
            return False
        return True
    if not check_exists(page):
        raise Http404
    
    prev = None
    if check_exists(page-1):
        prev = page-1
    next = None
    if check_exists(page+1):
        next = page+1
    
    return render_to_response("tutorial/"+str(page)+".html", {    
      "prev": prev,
      "next": next,
    }, context_instance=RequestContext(request))
