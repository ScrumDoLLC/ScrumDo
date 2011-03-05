
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



# Limits related to a personal account:
personal_project_limit      = Limit( providing_args=["user"] )
personal_user_limit         = Limit( providing_args=["user","userToAdd"] )
personal_storage_limit      = Limit( providing_args=["user"] )    
personal_extra_limit        = Limit( providing_args=["project"] )

# Limits related to an organization:
org_project_limit      = Limit( providing_args=["organization"] )
org_user_limit         = Limit( providing_args=["organization","userToAdd"] )
org_storage_limit      = Limit( providing_args=["organization"] )
org_extra_limit        = Limit( providing_args=["organization"] )

on_demand_velocity     = Limit( providing_args=["project"] )

# Helper methods:
def userIncreasedAlowed( project, user, userToAdd):
    if project.organization:
        return org_user_limit.increaseAllowed(userToAdd=userToAdd, organization=project.organization)
    else:
        return personal_user_limit.increaseAllowed(userToAdd=userToAdd, user=user)

