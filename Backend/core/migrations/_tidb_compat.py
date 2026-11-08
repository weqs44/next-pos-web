"""Operasi migrasi yang aman untuk TiDB dan juga untuk SQLite (dipakai CI/tes).

Nama modul diawali underscore, jadi tidak dianggap sebagai migrasi oleh Django.

Latar belakang: TiDB tidak mengizinkan ADD COLUMN dan ADD FOREIGN KEY dalam satu ALTER, jadi di MySQL/TiDB
kolom dan constraint ditambahkan terpisah dengan SQL mentah. SQL itu (ADD CONSTRAINT ... FOREIGN KEY,
DROP FOREIGN KEY) ditolak SQLite. Operasi ini memakai SQL mentah hanya di MySQL/TiDB dan perilaku standar
Django di database lain. SQL untuk MySQL/TiDB sama persis dengan migrasi sebelumnya, jadi database produksi
yang sudah termigrasi tidak terpengaruh.
"""
from django.db import migrations


class AddNullableForeignKeySplit(migrations.AddField):
    """AddField untuk ForeignKey nullable dengan nama constraint yang ditentukan eksplisit."""

    def __init__(self, model_name, name, field, fk_name):
        self.fk_name = fk_name
        super().__init__(model_name, name, field)

    def deconstruct(self):
        name, args, kwargs = super().deconstruct()
        kwargs['fk_name'] = self.fk_name
        return name, args, kwargs

    def _sql(self, app_label, state):
        model = state.apps.get_model(app_label, self.model_name)
        field = model._meta.get_field(self.name)
        table = model._meta.db_table
        ref_table = field.remote_field.model._meta.db_table
        ref_column = field.remote_field.model._meta.pk.column
        add_column = f'ALTER TABLE `{table}` ADD COLUMN `{field.column}` bigint NULL'
        add_fk = (
            f'ALTER TABLE `{table}` ADD CONSTRAINT `{self.fk_name}` '
            f'FOREIGN KEY (`{field.column}`) REFERENCES `{ref_table}` (`{ref_column}`)'
        )
        drop_fk = f'ALTER TABLE `{table}` DROP FOREIGN KEY `{self.fk_name}`'
        drop_column = f'ALTER TABLE `{table}` DROP COLUMN `{field.column}`'
        return model, add_column, add_fk, drop_fk, drop_column

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        if schema_editor.connection.vendor != 'mysql':
            return super().database_forwards(app_label, schema_editor, from_state, to_state)
        model, add_column, add_fk, _, _ = self._sql(app_label, to_state)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.execute(add_column)
            schema_editor.execute(add_fk)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        if schema_editor.connection.vendor != 'mysql':
            return super().database_backwards(app_label, schema_editor, from_state, to_state)
        model, _, _, drop_fk, drop_column = self._sql(app_label, from_state)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            schema_editor.execute(drop_fk)
            schema_editor.execute(drop_column)
