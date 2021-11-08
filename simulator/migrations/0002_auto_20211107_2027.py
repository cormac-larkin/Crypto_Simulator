# Generated by Django 3.2.7 on 2021-11-07 20:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('simulator', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='cryptocurrency',
            field=models.CharField(max_length=5),
        ),
        migrations.CreateModel(
            name='ExtendUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash', models.DecimalField(decimal_places=2, default=10000.0, max_digits=20)),
                ('link', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
