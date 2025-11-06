# Generated migration to drop estimator tables

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admindashboard', '0007_component'),
    ]

    operations = [
        migrations.RunSQL(
            "DROP TABLE IF EXISTS estimator_estimateitemcomponent;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS estimator_estimateitem;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS estimator_estimate;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
