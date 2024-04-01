# Generated by Django 4.1 on 2024-03-02 08:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiences', '0003_alter_experience_category_alter_experience_host_and_more'),
        ('rooms', '0005_alter_room_amenities_alter_room_category_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wishlists', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wishlist',
            name='experiences',
            field=models.ManyToManyField(related_name='wishlists', to='experiences.experience'),
        ),
        migrations.AlterField(
            model_name='wishlist',
            name='rooms',
            field=models.ManyToManyField(related_name='wishlists', to='rooms.room'),
        ),
        migrations.AlterField(
            model_name='wishlist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlists', to=settings.AUTH_USER_MODEL),
        ),
    ]
