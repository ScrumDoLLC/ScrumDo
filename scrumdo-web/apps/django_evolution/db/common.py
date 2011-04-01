import django
from django.core.management import color
from django.db import connection as default_connection
from django.db.backends.util import truncate_name
import copy


class BaseEvolutionOperations(object):
    connection = None

    def __init__(self, connection = default_connection):
        self.connection = connection

    def quote_sql_param(self, param):
        "Add protective quoting around an SQL string parameter"
        if isinstance(param, basestring):
            return u"'%s'" % unicode(param).replace(u"'",ur"\'")
        else:
            return param

    def rename_table(self, model, old_db_tablename, db_tablename):
        if old_db_tablename == db_tablename:
            # No Operation
            return []

        style = color.no_style()
        qn = self.connection.ops.quote_name
        max_name_length = self.connection.ops.max_name_length()
        creation = self.connection.creation

        sql = []
        refs = {}
        models = []

        for field in model._meta.local_many_to_many:
            if (field.rel and
                field.rel.through and
                field.rel.through._meta.db_table == old_db_tablename):

                through = field.rel.through

                for m2m_field in through._meta.local_fields:
                    if m2m_field.rel and m2m_field.rel.to == model:
                        models.append(m2m_field.rel.to)
                        refs.setdefault(m2m_field.rel.to, []).append(
                            (through, m2m_field))

        remove_refs = refs.copy()

        for relto in models:
            sql.extend(creation.sql_remove_table_constraints(relto, remove_refs,
                                                             style))
        params = (qn(old_db_tablename), qn(db_tablename))
        sql.append('ALTER TABLE %s RENAME TO %s;' % params)

        for relto in models:
            for rel_class, f in refs[relto]:
                if rel_class._meta.db_table == old_db_tablename:
                    rel_class._meta.db_table = db_tablename

                rel_class._meta.db_table = \
                    truncate_name(rel_class._meta.db_table, max_name_length)

            sql.extend(creation.sql_for_pending_references(relto, style, refs))

        return sql

    def delete_column(self, model, f):
        qn = self.connection.ops.quote_name
        params = (qn(model._meta.db_table), qn(f.column))

        return ['ALTER TABLE %s DROP COLUMN %s CASCADE;' % params]

    def delete_table(self, table_name):
        qn = self.connection.ops.quote_name
        return ['DROP TABLE %s;' % qn(table_name)]

    def add_m2m_table(self, model, f):
        style = color.no_style()
        creation = self.connection.creation

        if f.rel.through:
            references = {}
            pending_references = {}

            sql, references = creation.sql_create_model(f.rel.through, style)

            for refto, refs in references.items():
                pending_references.setdefault(refto, []).extend(refs)
                sql.extend(creation.sql_for_pending_references(
                    refto, style, pending_references))

            sql.extend(creation.sql_for_pending_references(
                f.rel.through, style, pending_references))
        else:
            sql = creation.sql_for_many_to_many_field(model, f, style)

        return sql

    def add_column(self, model, f, initial):
        qn = self.connection.ops.quote_name

        if f.rel:
            # it is a foreign key field
            # NOT NULL REFERENCES "django_evolution_addbasemodel" ("id") DEFERRABLE INITIALLY DEFERRED
            # ALTER TABLE <tablename> ADD COLUMN <column name> NULL REFERENCES <tablename1> ("<colname>") DEFERRABLE INITIALLY DEFERRED
            related_model = f.rel.to
            related_table = related_model._meta.db_table
            related_pk_col = related_model._meta.pk.name
            constraints = ['%sNULL' % (not f.null and 'NOT ' or '')]
            if f.unique or f.primary_key:
                constraints.append('UNIQUE')
            params = (qn(model._meta.db_table), qn(f.column), f.db_type(), ' '.join(constraints),
                qn(related_table), qn(related_pk_col), self.connection.ops.deferrable_sql())
            output = ['ALTER TABLE %s ADD COLUMN %s %s %s REFERENCES %s (%s) %s;' % params]
        else:
            null_constraints = '%sNULL' % (not f.null and 'NOT ' or '')
            if f.unique or f.primary_key:
                unique_constraints = 'UNIQUE'
            else:
                unique_constraints = ''

            # At this point, initial can only be None if null=True, otherwise it is
            # a user callable or the default AddFieldInitialCallback which will shortly raise an exception.
            if initial is not None:
                params = (qn(model._meta.db_table), qn(f.column), f.db_type(), unique_constraints)
                output = ['ALTER TABLE %s ADD COLUMN %s %s %s;' % params]

                if callable(initial):
                    params = (qn(model._meta.db_table), qn(f.column), initial(), qn(f.column))
                    output.append('UPDATE %s SET %s = %s WHERE %s IS NULL;' % params)
                else:
                    params = (qn(model._meta.db_table), qn(f.column), qn(f.column))
                    output.append(('UPDATE %s SET %s = %%s WHERE %s IS NULL;' % params, (initial,)))

                if not f.null:
                    # Only put this sql statement if the column cannot be null.
                    output.append(self.set_field_null(model, f, f.null))
            else:
                params = (qn(model._meta.db_table), qn(f.column), f.db_type(),' '.join([null_constraints, unique_constraints]))
                output = ['ALTER TABLE %s ADD COLUMN %s %s %s;' % params]
        return output

    def set_field_null(self, model, f, null):
        qn = self.connection.ops.quote_name
        params = (qn(model._meta.db_table), qn(f.column),)
        if null:
            return 'ALTER TABLE %s ALTER COLUMN %s DROP NOT NULL;' % params
        else:
            return 'ALTER TABLE %s ALTER COLUMN %s SET NOT NULL;' % params

    def create_index(self, model, f):
        "Returns the CREATE INDEX SQL statements."
        style = color.no_style()

        return self.connection.creation.sql_indexes_for_field(model, f, style)

    def drop_index(self, model, f):
        qn = self.connection.ops.quote_name
        index_name = self.get_index_name(model, f)
        max_length = self.connection.ops.max_name_length()

        return ['DROP INDEX %s;' % qn(truncate_name(index_name, max_length))]

    def get_index_name(self, model, f):
        if django.VERSION >= (1, 2):
            colname = self.connection.creation._digest(f.column)
        else:
            colname = f.column

        return '%s_%s' % (model._meta.db_table, colname)

    def change_null(self, model, field_name, new_null_attr, initial=None):
        qn = self.connection.ops.quote_name
        opts = model._meta
        f = opts.get_field(field_name)
        output = []
        if new_null_attr:
            # Setting null to True
            opts = model._meta
            params = (qn(opts.db_table), qn(f.column),)
            output.append(self.set_field_null(model, f, new_null_attr))
        else:
            if initial is not None:
                output = []
                if callable(initial):
                    params = (qn(opts.db_table), qn(f.column), initial(), qn(f.column))
                    output.append('UPDATE %s SET %s = %s WHERE %s IS NULL;' % params)
                else:
                    params = (qn(opts.db_table), qn(f.column), qn(f.column))
                    output.append(('UPDATE %s SET %s = %%s WHERE %s IS NULL;' % params, (initial,)))
            output.append(self.set_field_null(model, f, new_null_attr))

        return output

    def change_max_length(self, model, field_name, new_max_length, initial=None):
        qn = self.connection.ops.quote_name
        opts = model._meta
        f = opts.get_field(field_name)
        f.max_length = new_max_length
        params = (qn(opts.db_table), qn(f.column), f.db_type(), qn(f.column), f.db_type())
        return ['ALTER TABLE %s ALTER COLUMN %s TYPE %s USING CAST(%s as %s);' % params]

    def change_db_column(self, model, field_name, new_db_column, initial=None):
        opts = model._meta
        old_field = opts.get_field(field_name)
        new_field = copy.copy(old_field)
        new_field.column = new_db_column
        return self.rename_column(opts, old_field, new_field)

    def change_db_table(self, model, old_db_tablename, new_db_tablename):
        return self.rename_table(model, old_db_tablename, new_db_tablename)

    def change_db_index(self, model, field_name, new_db_index, initial=None):
        f = model._meta.get_field(field_name)
        f.db_index = new_db_index
        if new_db_index:
            return self.create_index(model, f)
        else:
            return self.drop_index(model, f)

    def change_unique(self, model, field_name, new_unique_value, initial=None):
        qn = self.connection.ops.quote_name
        opts = model._meta
        f = opts.get_field(field_name)
        constraint_name = truncate_name('%s_%s_key' % (opts.db_table, f.column),
                                        self.connection.ops.max_name_length())

        if new_unique_value:
            params = (qn(opts.db_table), constraint_name, qn(f.column),)
            return ['ALTER TABLE %s ADD CONSTRAINT %s UNIQUE(%s);' % params]
        else:
            params = (qn(opts.db_table), constraint_name,)
            return ['ALTER TABLE %s DROP CONSTRAINT %s;' % params]
