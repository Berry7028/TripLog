# Generated migration to remove AI features

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spots', '0008_userrecommendationscore'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RecommendationJobSetting',
        ),
        migrations.DeleteModel(
            name='RecommendationJobLog',
        ),
        migrations.DeleteModel(
            name='UserRecommendationScore',
        ),
        migrations.RemoveField(
            model_name='spot',
            name='is_ai_generated',
        ),
    ]
