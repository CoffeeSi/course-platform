from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="checkout_url",
            field=models.URLField(
                max_length=2048,
                blank=True,
                verbose_name="Ссылка на оплату",
            ),
        ),
    ]
