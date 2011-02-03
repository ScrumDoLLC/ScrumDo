
class Limit(object) :
  
  def addHandler(self, handler ):
    self.handlers.append( handler )
  
  def increaseAllowed(self, **kwargs ):
    for handler in self.handlers:
      if not handler( **kwargs ):
        return False
    return True
    
  def __init__(self, *args, **kwargs):
    self.providing_args = kwargs.pop("providing_args")
    self.handlers = []
    super(self.__class__, self).__init__(*args, **kwargs)



    
project_limit      = Limit( providing_args=["organization","user"] )
user_limit         = Limit( providing_args=["organization","user"] )
organization_limit = Limit( providing_args=["organization","user"] )    