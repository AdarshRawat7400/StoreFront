# Generated by Django 5.0.1 on 2024-02-26 16:32

import django.contrib.postgres.fields
import django_resized.forms
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_productimage_product_images'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='images',
        ),
        migrations.DeleteModel(
            name='ProductImage',
        ),
        migrations.AddField(
            model_name='product',
            name='images',
            field=django.contrib.postgres.fields.ArrayField(base_field=django_resized.forms.ResizedImageField(blank=True, crop=None, force_format='WEBP', keep_meta=True, null=True, quality=75, scale=None, size=[1920, 570], upload_to='bucket/products'), blank=True, null=True, size=3),
        ),
    ]
