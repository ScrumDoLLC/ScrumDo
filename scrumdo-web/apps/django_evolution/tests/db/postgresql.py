from django.db.models.options import Options

autocreate_through_tables = hasattr(Options({}), 'auto_created')


add_field = {
    'AddNonNullNonCallableColumnModel':
        '\n'.join([
            'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field" integer ;',
            'UPDATE "tests_testmodel" SET "added_field" = 1 WHERE "added_field" IS NULL;',
            'ALTER TABLE "tests_testmodel" ALTER COLUMN "added_field" SET NOT NULL;',
        ]),
    'AddNonNullCallableColumnModel':
        '\n'.join([
            'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field" integer ;',
            'UPDATE "tests_testmodel" SET "added_field" = "int_field" WHERE "added_field" IS NULL;',
            'ALTER TABLE "tests_testmodel" ALTER COLUMN "added_field" SET NOT NULL;',
        ]),
    'AddNullColumnWithInitialColumnModel':
        '\n'.join([
            'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field" integer ;',
            'UPDATE "tests_testmodel" SET "added_field" = 1 WHERE "added_field" IS NULL;',
        ]),
    'AddStringColumnModel':
        '\n'.join([
            'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field" varchar(10) ;',
            'UPDATE "tests_testmodel" SET "added_field" = \'abc\\\'s xyz\' WHERE "added_field" IS NULL;',
            'ALTER TABLE "tests_testmodel" ALTER COLUMN "added_field" SET NOT NULL;',
        ]),
    'AddDateColumnModel':
        '\n'.join([
            'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field" timestamp with time zone ;',
            'UPDATE "tests_testmodel" SET "added_field" = 2007-12-13 16:42:00 WHERE "added_field" IS NULL;',
            'ALTER TABLE "tests_testmodel" ALTER COLUMN "added_field" SET NOT NULL;',
        ]),
    'AddDefaultColumnModel':
        '\n'.join([
            'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field" integer ;',
            'UPDATE "tests_testmodel" SET "added_field" = 42 WHERE "added_field" IS NULL;',
            'ALTER TABLE "tests_testmodel" ALTER COLUMN "added_field" SET NOT NULL;',
        ]),
    'AddEmptyStringDefaultColumnModel':
        '\n'.join([
            'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field" varchar(20) ;',
            'UPDATE "tests_testmodel" SET "added_field" = \'\' WHERE "added_field" IS NULL;',
            'ALTER TABLE "tests_testmodel" ALTER COLUMN "added_field" SET NOT NULL;',
        ]),
    'AddNullColumnModel':
        'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field" integer NULL ;',
    'NonDefaultColumnModel':
        'ALTER TABLE "tests_testmodel" ADD COLUMN "non-default_column" integer NULL ;',
    'AddColumnCustomTableModel':
        'ALTER TABLE "custom_table_name" ADD COLUMN "added_field" integer NULL ;',
    'AddIndexedColumnModel':
        '\n'.join([
            'ALTER TABLE "tests_testmodel" ADD COLUMN "add_field" integer NULL ;',
            'CREATE INDEX "tests_testmodel_add_field" ON "tests_testmodel" ("add_field");'
        ]),
    'AddUniqueColumnModel':
        'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field" integer NULL UNIQUE;',
    'AddUniqueIndexedModel':
        'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field" integer NULL UNIQUE;',
    'AddForeignKeyModel':
        '\n'.join([
            'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field_id" integer NULL REFERENCES "tests_addanchor1" ("id")  DEFERRABLE INITIALLY DEFERRED;',
            'CREATE INDEX "tests_testmodel_added_field_id" ON "tests_testmodel" ("added_field_id");'
        ]),
}

if autocreate_through_tables:
    add_field.update({
        'AddManyToManyDatabaseTableModel':
            '\n'.join([
                'CREATE TABLE "tests_testmodel_added_field" (',
                '    "id" serial NOT NULL PRIMARY KEY,',
                '    "testmodel_id" integer NOT NULL,',
                '    "addanchor1_id" integer NOT NULL,',
                '    UNIQUE ("testmodel_id", "addanchor1_id")',
                ')',
                ';',
                'ALTER TABLE "tests_testmodel_added_field" ADD CONSTRAINT "testmodel_id_refs_id_ed159e33" FOREIGN KEY ("testmodel_id") REFERENCES "tests_testmodel" ("id") DEFERRABLE INITIALLY DEFERRED;',
                'ALTER TABLE "tests_testmodel_added_field" ADD CONSTRAINT "addanchor1_id_refs_id_7efbb240" FOREIGN KEY ("addanchor1_id") REFERENCES "tests_addanchor1" ("id") DEFERRABLE INITIALLY DEFERRED;',
            ]),
         'AddManyToManyNonDefaultDatabaseTableModel':
            '\n'.join([
                'CREATE TABLE "tests_testmodel_added_field" (',
                '    "id" serial NOT NULL PRIMARY KEY,',
                '    "testmodel_id" integer NOT NULL,',
                '    "addanchor2_id" integer NOT NULL,',
                '    UNIQUE ("testmodel_id", "addanchor2_id")',
                ')',
                ';',
                'ALTER TABLE "tests_testmodel_added_field" ADD CONSTRAINT "testmodel_id_refs_id_ed159e33" FOREIGN KEY ("testmodel_id") REFERENCES "tests_testmodel" ("id") DEFERRABLE INITIALLY DEFERRED;',
                'ALTER TABLE "tests_testmodel_added_field" ADD CONSTRAINT "addanchor2_id_refs_id_ec3e2588" FOREIGN KEY ("addanchor2_id") REFERENCES "custom_add_anchor_table" ("id") DEFERRABLE INITIALLY DEFERRED;',
            ]),
         'AddManyToManySelf':
            '\n'.join([
                'CREATE TABLE "tests_testmodel_added_field" (',
                '    "id" serial NOT NULL PRIMARY KEY,',
                '    "from_testmodel_id" integer NOT NULL,',
                '    "to_testmodel_id" integer NOT NULL,',
                '    UNIQUE ("from_testmodel_id", "to_testmodel_id")',
                ')',
                ';',
                'ALTER TABLE "tests_testmodel_added_field" ADD CONSTRAINT "from_testmodel_id_refs_id_ed159e33" FOREIGN KEY ("from_testmodel_id") REFERENCES "tests_testmodel" ("id") DEFERRABLE INITIALLY DEFERRED;',
                'ALTER TABLE "tests_testmodel_added_field" ADD CONSTRAINT "to_testmodel_id_refs_id_ed159e33" FOREIGN KEY ("to_testmodel_id") REFERENCES "tests_testmodel" ("id") DEFERRABLE INITIALLY DEFERRED;',
            ]),
    })
else:
    add_field.update({
        'AddManyToManyDatabaseTableModel':
            '\n'.join([
                'CREATE TABLE "tests_testmodel_added_field" (',
                '    "id" serial NOT NULL PRIMARY KEY,',
                '    "testmodel_id" integer NOT NULL REFERENCES "tests_testmodel" ("id") DEFERRABLE INITIALLY DEFERRED,',
                '    "addanchor1_id" integer NOT NULL REFERENCES "tests_addanchor1" ("id") DEFERRABLE INITIALLY DEFERRED,',
                '    UNIQUE ("testmodel_id", "addanchor1_id")',
                ')',
                ';'
            ]),
         'AddManyToManyNonDefaultDatabaseTableModel':
            '\n'.join([
                'CREATE TABLE "tests_testmodel_added_field" (',
                '    "id" serial NOT NULL PRIMARY KEY,',
                '    "testmodel_id" integer NOT NULL REFERENCES "tests_testmodel" ("id") DEFERRABLE INITIALLY DEFERRED,',
                '    "addanchor2_id" integer NOT NULL REFERENCES "custom_add_anchor_table" ("id") DEFERRABLE INITIALLY DEFERRED,',
                '    UNIQUE ("testmodel_id", "addanchor2_id")',
                ')',
                ';'
            ]),
         'AddManyToManySelf':
            '\n'.join([
                'CREATE TABLE "tests_testmodel_added_field" (',
                '    "id" serial NOT NULL PRIMARY KEY,',
                '    "from_testmodel_id" integer NOT NULL REFERENCES "tests_testmodel" ("id") DEFERRABLE INITIALLY DEFERRED,',
                '    "to_testmodel_id" integer NOT NULL REFERENCES "tests_testmodel" ("id") DEFERRABLE INITIALLY DEFERRED,',
                '    UNIQUE ("from_testmodel_id", "to_testmodel_id")',
                ')',
                ';'
            ]),
    })

delete_field = {
    'DefaultNamedColumnModel':
        'ALTER TABLE "tests_testmodel" DROP COLUMN "int_field" CASCADE;',
    'NonDefaultNamedColumnModel':
        'ALTER TABLE "tests_testmodel" DROP COLUMN "non-default_db_column" CASCADE;',
    'ConstrainedColumnModel':
        'ALTER TABLE "tests_testmodel" DROP COLUMN "int_field3" CASCADE;',
    'DefaultManyToManyModel':
        'DROP TABLE "tests_testmodel_m2m_field1";',
    'NonDefaultManyToManyModel':
        'DROP TABLE "non-default_m2m_table";',
    'DeleteForeignKeyModel':
        'ALTER TABLE "tests_testmodel" DROP COLUMN "fk_field1_id" CASCADE;',
    'DeleteColumnCustomTableModel':
        'ALTER TABLE "custom_table_name" DROP COLUMN "value" CASCADE;',
}

change_field = {
    "SetNotNullChangeModelWithConstant":
        '\n'.join([
            'UPDATE "tests_testmodel" SET "char_field1" = \'abc\\\'s xyz\' WHERE "char_field1" IS NULL;',
            'ALTER TABLE "tests_testmodel" ALTER COLUMN "char_field1" SET NOT NULL;',
        ]),
    "SetNotNullChangeModelWithCallable":
            '\n'.join([
                'UPDATE "tests_testmodel" SET "char_field1" = "char_field" WHERE "char_field1" IS NULL;',
                'ALTER TABLE "tests_testmodel" ALTER COLUMN "char_field1" SET NOT NULL;',
            ]),
    "SetNullChangeModel": 'ALTER TABLE "tests_testmodel" ALTER COLUMN "char_field2" DROP NOT NULL;',
    "NoOpChangeModel": '',
    "IncreasingMaxLengthChangeModel": 'ALTER TABLE "tests_testmodel" ALTER COLUMN "char_field" TYPE varchar(45) USING CAST("char_field" as varchar(45));',
    "DecreasingMaxLengthChangeModel": 'ALTER TABLE "tests_testmodel" ALTER COLUMN "char_field" TYPE varchar(1) USING CAST("char_field" as varchar(1));',
    "DBColumnChangeModel": 'ALTER TABLE "tests_testmodel" RENAME COLUMN "custom_db_column" TO "customised_db_column";',
    "AddDBIndexChangeModel": 'CREATE INDEX "tests_testmodel_int_field2" ON "tests_testmodel" ("int_field2");',
    "RemoveDBIndexChangeModel": 'DROP INDEX "tests_testmodel_int_field1";',
    "AddUniqueChangeModel": 'ALTER TABLE "tests_testmodel" ADD CONSTRAINT tests_testmodel_int_field4_key UNIQUE("int_field4");',
    "RemoveUniqueChangeModel": 'ALTER TABLE "tests_testmodel" DROP CONSTRAINT tests_testmodel_int_field3_key;',
    "MultiAttrChangeModel":
        '\n'.join([
            'ALTER TABLE "tests_testmodel" ALTER COLUMN "char_field2" DROP NOT NULL;',
            'ALTER TABLE "tests_testmodel" RENAME COLUMN "custom_db_column" TO "custom_db_column2";',
            'ALTER TABLE "tests_testmodel" ALTER COLUMN "char_field" TYPE varchar(35) USING CAST("char_field" as varchar(35));',
        ]),
    "MultiAttrSingleFieldChangeModel":
        '\n'.join([
            'ALTER TABLE "tests_testmodel" ALTER COLUMN "char_field2" TYPE varchar(35) USING CAST("char_field2" as varchar(35));',
            'ALTER TABLE "tests_testmodel" ALTER COLUMN "char_field2" DROP NOT NULL;',
        ]),
    "RedundantAttrsChangeModel":
        '\n'.join([
            'ALTER TABLE "tests_testmodel" ALTER COLUMN "char_field2" DROP NOT NULL;',
            'ALTER TABLE "tests_testmodel" RENAME COLUMN "custom_db_column" TO "custom_db_column3";',
            'ALTER TABLE "tests_testmodel" ALTER COLUMN "char_field" TYPE varchar(35) USING CAST("char_field" as varchar(35));',
        ]),
}

if autocreate_through_tables:
    change_field.update({
        "M2MDBTableChangeModel":
            '\n'.join([
                'ALTER TABLE "change_field_non-default_m2m_table" DROP CONSTRAINT "testmodel_id_refs_my_id_5d3392f8";',
                'ALTER TABLE "change_field_non-default_m2m_table" RENAME TO "custom_m2m_db_table_name";',
                'ALTER TABLE "custom_m2m_db_table_name" ADD CONSTRAINT "testmodel_id_refs_my_id_a31f0c6f" FOREIGN KEY ("testmodel_id") REFERENCES "tests_testmodel" ("my_id") DEFERRABLE INITIALLY DEFERRED;',
            ]),
    })
else:
    change_field.update({
        "M2MDBTableChangeModel": 'ALTER TABLE "change_field_non-default_m2m_table" RENAME TO "custom_m2m_db_table_name";',
    })

delete_model = {
    'BasicModel':
        'DROP TABLE "tests_basicmodel";',
    'BasicWithM2MModel':
        '\n'.join([
            'DROP TABLE "tests_basicwithm2mmodel_m2m";',
            'DROP TABLE "tests_basicwithm2mmodel";'
        ]),
    'CustomTableModel':
        'DROP TABLE "custom_table_name";',
    'CustomTableWithM2MModel':
        '\n'.join([
            'DROP TABLE "another_custom_table_name_m2m";',
            'DROP TABLE "another_custom_table_name";'
        ]),
}

delete_application = {
    'DeleteApplication':
        '\n'.join([
            'DROP TABLE "tests_appdeleteanchor1";',
            'DROP TABLE "app_delete_custom_add_anchor_table";',
            'DROP TABLE "tests_testmodel_anchor_m2m";',
            'DROP TABLE "tests_testmodel";',
            'DROP TABLE "app_delete_custom_table_name";',
        ]),
}

rename_field = {
    'RenameColumnModel':
        'ALTER TABLE "tests_testmodel" RENAME COLUMN "int_field" TO "renamed_field";',
    'RenameColumnWithTableNameModel':
        'ALTER TABLE "tests_testmodel" RENAME COLUMN "int_field" TO "renamed_field";',
    'RenameForeignKeyColumnModel':
        'ALTER TABLE "tests_testmodel" RENAME COLUMN "fk_field_id" TO "renamed_field_id";',
    'RenameNonDefaultColumnNameModel':
        'ALTER TABLE "tests_testmodel" RENAME COLUMN "custom_db_col_name" TO "renamed_field";',
    'RenameNonDefaultColumnNameToNonDefaultNameModel':
        'ALTER TABLE "tests_testmodel" RENAME COLUMN "custom_db_col_name" TO "non-default_column_name";',
    'RenameNonDefaultColumnNameToNonDefaultNameAndTableModel':
        'ALTER TABLE "tests_testmodel" RENAME COLUMN "custom_db_col_name" TO "non-default_column_name2";',
    'RenameColumnCustomTableModel':
        'ALTER TABLE "custom_rename_table_name" RENAME COLUMN "value" TO "renamed_field";',
    'RenameNonDefaultManyToManyTableModel':
        'ALTER TABLE "non-default_db_table" RENAME TO "tests_testmodel_renamed_field";',
}

sql_mutation = {
    'SQLMutationSequence': """[
...    SQLMutation('first-two-fields', [
...        'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field1" integer NULL;',
...        'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field2" integer NULL;'
...    ], update_first_two),
...    SQLMutation('third-field', [
...        'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field3" integer NULL;',
...    ], update_third)]
""",
    'SQLMutationOutput':
        '\n'.join([
            'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field1" integer NULL;',
            'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field2" integer NULL;',
            'ALTER TABLE "tests_testmodel" ADD COLUMN "added_field3" integer NULL;',
        ]),
}

if autocreate_through_tables:
    rename_field.update({
        'RenamePrimaryKeyColumnModel':
            '\n'.join([
                'ALTER TABLE "non-default_db_table" DROP CONSTRAINT "testmodel_id_refs_id_eeae318e";',
                'ALTER TABLE "tests_testmodel_m2m_field" DROP CONSTRAINT "testmodel_id_refs_id_ba77d38d";',
                'ALTER TABLE "tests_testmodel" RENAME COLUMN "id" TO "my_pk_id";',
                'ALTER TABLE "non-default_db_table" ADD CONSTRAINT "testmodel_id_refs_my_pk_id_eeae318e" FOREIGN KEY ("testmodel_id") REFERENCES "tests_testmodel" ("my_pk_id") DEFERRABLE INITIALLY DEFERRED;',
                'ALTER TABLE "tests_testmodel_m2m_field" ADD CONSTRAINT "testmodel_id_refs_my_pk_id_ba77d38d" FOREIGN KEY ("testmodel_id") REFERENCES "tests_testmodel" ("my_pk_id") DEFERRABLE INITIALLY DEFERRED;',
            ]),
        'RenameManyToManyTableModel':
            '\n'.join([
                'ALTER TABLE "tests_testmodel_m2m_field" DROP CONSTRAINT "testmodel_id_refs_id_ba77d38d";',
                'ALTER TABLE "tests_testmodel_m2m_field" RENAME TO "tests_testmodel_renamed_field";',
                'ALTER TABLE "tests_testmodel_renamed_field" ADD CONSTRAINT "testmodel_id_refs_id_f50a5e5d" FOREIGN KEY ("testmodel_id") REFERENCES "tests_testmodel" ("id") DEFERRABLE INITIALLY DEFERRED;',
            ]),
        'RenameManyToManyTableWithColumnNameModel':
            '\n'.join([
                'ALTER TABLE "tests_testmodel_m2m_field" DROP CONSTRAINT "testmodel_id_refs_id_ba77d38d";',
                'ALTER TABLE "tests_testmodel_m2m_field" RENAME TO "tests_testmodel_renamed_field";',
                'ALTER TABLE "tests_testmodel_renamed_field" ADD CONSTRAINT "testmodel_id_refs_id_f50a5e5d" FOREIGN KEY ("testmodel_id") REFERENCES "tests_testmodel" ("id") DEFERRABLE INITIALLY DEFERRED;',
            ]),
    })
else:
    rename_field.update({
        'RenamePrimaryKeyColumnModel':
            'ALTER TABLE "tests_testmodel" RENAME COLUMN "id" TO "my_pk_id";',
        'RenameManyToManyTableModel':
            'ALTER TABLE "tests_testmodel_m2m_field" RENAME TO "tests_testmodel_renamed_field";',
        'RenameManyToManyTableWithColumnNameModel':
            'ALTER TABLE "tests_testmodel_m2m_field" RENAME TO "tests_testmodel_renamed_field";',
    })

generics = {
    'DeleteColumnModel': 'ALTER TABLE "tests_testmodel" DROP COLUMN "char_field" CASCADE;'
}

inheritance = {
    'AddToChildModel':
        '\n'.join([
            'ALTER TABLE "tests_childmodel" ADD COLUMN "added_field" integer ;',
            'UPDATE "tests_childmodel" SET "added_field" = 42 WHERE "added_field" IS NULL;',
            'ALTER TABLE "tests_childmodel" ALTER COLUMN "added_field" SET NOT NULL;',
        ]),
    'DeleteFromChildModel':
        'ALTER TABLE "tests_childmodel" DROP COLUMN "int_field" CASCADE;',
}
