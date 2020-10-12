# Generated by Django 3.0.6 on 2020-10-02 14:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('modules', '0008_auto_20201002_1601'),
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gameitemlink',
            name='gameItemIDfk',
        ),
        migrations.RemoveField(
            model_name='gameitemlink',
            name='gameItemType',
        ),
        migrations.AddField(
            model_name='gameitemlink',
            name='module',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='modules.AllModuleItems'),
            preserve_default=False,
        ),
    ]
