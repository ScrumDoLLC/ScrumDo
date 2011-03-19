import os

from django_evolution import EvolutionException, is_multi_db
from django_evolution.models import Evolution
from django_evolution.mutations import SQLMutation


def get_evolution_sequence(app):
    "Obtain the full evolution sequence for an application"
    try:
        app_name = '.'.join(app.__name__.split('.')[:-1])
        evolution_module = __import__(app_name + '.evolutions',{},{},[''])
        return evolution_module.SEQUENCE
    except:
        return []


def get_unapplied_evolutions(app, database):
    "Obtain the list of unapplied evolutions for an application"
    sequence = get_evolution_sequence(app)
    app_label = app.__name__.split('.')[-2]

    evolutions = Evolution.objects.filter(app_label=app_label)

    if is_multi_db():
        evolutions = evolutions.using(database)

    applied = [evo.label for evo in evolutions]

    return [seq for seq in sequence if seq not in applied]


def get_mutations(app, evolution_labels, database):
    """
    Obtain the list of mutations described by the named evolutions.
    """
    # For each item in the evolution sequence. Check each item to see if it is
    # a python file or an sql file.
    try:
        app_name = '.'.join(app.__name__.split('.')[:-1])
        evolution_module = __import__(app_name + '.evolutions', {}, {}, [''])
    except ImportError:
        return []

    mutations = []

    for label in evolution_labels:
        directory_name = os.path.dirname(evolution_module.__file__)

        # The first element is used for compatibility purposes.
        filenames = [
            os.path.join(directory_name, label + '.sql'),
            os.path.join(directory_name, "%s_%s.sql" % (database, label)),
        ]

        found = False

        for filename in filenames:
            if os.path.exists(filename):
                sql = []
                sql_file = open(filename)

                for line in sql_file:
                    sql.append(line)

                mutations.append(SQLMutation(label, sql))

                found = True
                break

        if not found:
            try:
                module_name = [evolution_module.__name__, label]
                module = __import__('.'.join(module_name),
                                    {}, {}, [module_name]);
                mutations.extend(module.MUTATIONS)
            except ImportError:
                raise EvolutionException(
                    'Error: Failed to find an SQL or Python evolution named %s'
                    % label)

    return mutations
