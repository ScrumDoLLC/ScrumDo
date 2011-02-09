from django.db.models import fields

# from  http://www.indirecthit.com/2008/04/29/django-difference-between-two-model-instances/
def get_changes_between_models(model1, model2, excludes = []):
    changes = {}
    for field in model1._meta.fields:
        if not (isinstance(field, (fields.AutoField, fields.related.RelatedField)) 
                or field.name in excludes):
            if field.value_from_object(model1) != field.value_from_object(model2):
                changes[field.verbose_name] = (field.value_from_object(model1),
                                               field.value_from_object(model2))
    return changes
