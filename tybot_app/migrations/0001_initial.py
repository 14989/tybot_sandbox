# Generated by Django 3.0.8 on 2020-07-17 15:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Change',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workflow', models.CharField(max_length=360)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('marketo_id', models.PositiveIntegerField()),
                ('changed_field', models.CharField(max_length=360)),
                ('old_value', models.CharField(blank=True, max_length=360, null=True)),
                ('new_value', models.CharField(blank=True, max_length=360, null=True)),
            ],
        ),
    ]