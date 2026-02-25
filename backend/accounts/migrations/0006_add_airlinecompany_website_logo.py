from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_remove_customer_address_remove_customer_phone_no"),
    ]

    operations = [
        migrations.AddField(
            model_name="airlinecompany",
            name="website",
            field=models.URLField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="airlinecompany",
            name="logo",
            field=models.ImageField(blank=True, null=True, upload_to="airlines/"),
        ),
    ]

