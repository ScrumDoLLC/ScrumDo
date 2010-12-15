from django.conf import settings





class ExtrasManager:
  """
    Small class to manage our list of extras.
  """
  
  def getProjectConfig( self , project):
    pass
  
  def getExtras(self):
    return self.extras.values()
    
  def getExtra( self, slug ):
    return self.extras[ slug ]

  def __init__(self, extras_settings):
    manager = self
    self.extras = {}
    for extra in extras_settings:      
      extra_class = get_class( extra )
      extra = extra_class()
      self.extras[ extra.getSlug() ] = extra
      
def get_class( kls ):
  parts = kls.split('.')
  module = ".".join(parts[:-1])
  m = __import__( module )
  for comp in parts[1:]:
      m = getattr(m, comp)            
  return m
    
    
manager = ExtrasManager( settings.SCRUMDO_EXTRAS )  