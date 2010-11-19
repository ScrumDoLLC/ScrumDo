from django.core.management import color
from django.db.backends.util import truncate_name

from common import BaseEvolutionOperations


class EvolutionOperations(BaseEvolutionOperations):
    def rename_column(self, opts, old_field, new_field):
        if old_field.column == new_field.column:
            # No Operation
            return []

        style = color.no_style()
        qn = self.connection.ops.quote_name
        max_name_length = self.connection.ops.max_name_length()
        creation = self.connection.creation
        sql = []
        refs = {}
        models = []

        if old_field.primary_key:
            for field in opts.local_many_to_many:
                if field.rel and field.rel.through:
                    through = field.rel.through

                    for m2m_f in through._meta.local_fields:
                        if (m2m_f.rel and
                            m2m_f.rel.to._meta.db_table == opts.db_table and
                            m2m_f.rel.field_name == old_field.column):

                            models.append(m2m_f.rel.to)
                            refs.setdefault(m2m_f.rel.to, []).append(
                                (through, m2m_f))

            remove_refs = refs.copy()

            for relto in models:
                sql.extend(creation.sql_remove_table_constraints(
                    relto, remove_refs, style))

        params = (qn(opts.db_table),
                  truncate_name(qn(old_field.column), max_name_length),
                  truncate_name(qn(new_field.column), max_name_length))
        sql.append('ALTER TABLE %s RENAME COLUMN %s TO %s;' % params)

        if old_field.primary_key:
            for relto in models:
                for rel_class, f in refs[relto]:
                    f.rel.field_name = new_field.column

                del relto._meta._fields[old_field.name]
                relto._meta._fields[new_field.name] = new_field

                sql.extend(creation.sql_for_pending_references(
                    relto, style, refs))

        return sql

    def get_index_name(self, model, f):
        # By default, Django 1.2 will use a digest hash for the column name.
        # The PostgreSQL support, however, uses the column name itself.
        return '%s_%s' % (model._meta.db_table, f.column)
