from extras.interfaces import ScrumdoProjectExtra
from django.conf import settings

class ExampleExtra( ScrumdoProjectExtra ):
  def getName(self):
    return "Example Extra"
    
  # Returns a version of the name consisting of only letters, numbers, or dashes
  def getSlug(self):
    return "example"

  def getLogo(self):
    return settings.STATIC_URL + "extras/example-logo.png"      
    
  # Returns a user-friendly description of this extra.  This text will be passed through a Markdown filter when displayed to the user.
  def getDescription(self):
    return "This Extra demonstrates the bare minimal required to get a ScrumDo Project based extra working."
    
  # Should return a django style response that handles any configuration that this extra may need.
  def doProjectConfigration( self, request, project ):
    return 
    
  