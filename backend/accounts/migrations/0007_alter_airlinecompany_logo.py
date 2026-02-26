from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_add_airlinecompany_website_logo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="airlinecompany",
            name="logo",
            field=models.TextField(blank=True, null=True),
        ),
    ]
