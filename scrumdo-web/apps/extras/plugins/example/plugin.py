from extras.interfaces import ScrumdoProjectExtra
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

import logging

class ExampleExtra( ScrumdoProjectExtra ):
  def getName(self):
    return "Example Extra"
    
  
  def getSlug(self):
    "Returns a version of the name consisting of only letters, numbers, or dashes"
    return "example"

  def getLogo(self):
    return settings.STATIC_URL + "extras/example-logo.png"      
    
  
  def getDescription(self):
    "Returns a user-friendly description of this extra.  This text will be passed through a Markdown filter when displayed to the user."    
    return "This Extra demonstrates the bare minimal required to get a ScrumDo Project based extra working."
    
  
  def doProjectConfiguration( self, request, project ):
    "Should return a django style response that handles any configuration that this extra may need."    
    return render_to_response("extras/example/configure.html", {
        "extra":self,
      }, context_instance=RequestContext(request)) 
    
  
  def getShortStatus(self, project):
    return "Example status!"
  
  def associate( self, project):
    logging.info("Associated example extra with " + project.slug )


  def unassociate( self, project):
    logging.info("Unassociated example extra with " + project.slug )
    
Plugin = ExampleExtra