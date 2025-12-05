from django.db import migrations, models


def add_theme_column_if_missing(apps, schema_editor):
    table = 'spots_userprofile'
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        columns = {col.name for col in connection.introspection.get_table_description(cursor, table)}
    if 'theme' not in columns:
        UserProfile = apps.get_model('spots', 'UserProfile')
        field = models.CharField(max_length=10, default='system')
        field.set_attributes_from_name('theme')
        schema_editor.add_field(UserProfile, field)
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE spots_userprofile SET theme = 'system' "
            "WHERE theme IS NULL OR theme = ''"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('spots', '0012_alter_spot_image_url'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_theme_column_if_missing, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='userprofile',
                    name='theme',
                    field=models.CharField(
                        choices=[('system', 'システム設定'), ('light', 'ライト'), ('dark', 'ダーク')],
                        default='system',
                        max_length=10,
                        verbose_name='テーマ',
                    ),
                ),
            ],
        ),
    ]
