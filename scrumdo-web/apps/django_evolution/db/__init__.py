# Establish the common EvolutionOperations instance, called evolver.

from django.conf import settings
from django.db import connection

class EvolutionOperationsMulti(object):
    def __init__(self, db_name):
        try:
            from django.db import connections, router
            engine = settings.DATABASES[db_name]['ENGINE'].split('.')[-1]
            connection = connections[db_name]
            module_name = ['django_evolution.db', engine]
            module = __import__('.'.join(module_name), {}, {}, [''])
            self.evolver = module.EvolutionOperations(connection)
        except:
            module_name = ['django_evolution.db',settings.DATABASE_ENGINE]
            module = __import__('.'.join(module_name),{},{},[''])
            self.evolver = module.EvolutionOperations()
    def get_evolver(self):
        return self.evolver
