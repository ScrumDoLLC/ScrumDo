
class Limit(object) :
  
  def addHandler(self, handler ):
    self.handlers.append( handler )
  
  def stats(self, **kwargs ):
    for handler in self.handlers:
      if handler.canHandle( **kwargs ):
        return handler.stats( **kwargs )
    return (0,0,False)
    
  
  def increaseAllowed(self, **kwargs ):
    for handler in self.handlers:
      if handler.canHandle( **kwargs ):
        return handler.increaseAllowed( **kwargs )
    return True
    
  def __init__(self, *args, **kwargs):
    self.providing_args = kwargs.pop("providing_args")
    self.handlers = []
    super(self.__class__, self).__init__(*args, **kwargs)



    
project_limit      = Limit( providing_args=["organization","user"] )
user_limit         = Limit( providing_args=["organization","user"] )
organization_limit = Limit( providing_args=["organization","user"] )    