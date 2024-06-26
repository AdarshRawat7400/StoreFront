# Generated by Django 5.0.1 on 2024-02-16 11:53

import apps.core.custom_model_fields
import apps.users.models
import django.core.validators
import django.db.models.deletion
import django_countries.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('password', models.CharField(blank=True, max_length=128, null=True, validators=[django.core.validators.MinLengthValidator(limit_value=5, message='The password must be at least 5 characters.')], verbose_name='password')),
                ('role', models.CharField(choices=[('customer', 'Customer'), ('admin', 'Admin'), ('superadmin', 'Super Admin')], default='user', max_length=30, verbose_name='user type')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active.', verbose_name='active')),
                ('username', models.CharField(max_length=50, unique=True, validators=[django.core.validators.MinLengthValidator(limit_value=4, message='The username must be at least 4 characters.')], verbose_name='username')),
                ('first_name', models.CharField(blank=True, default='', max_length=50, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, default='', max_length=50, verbose_name='last name')),
                ('balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=15, verbose_name='balance')),
                ('email', models.EmailField(blank=True, max_length=255, null=True, verbose_name='email')),
                ('dob', models.DateField(blank=True, null=True, verbose_name='dob')),
                ('full_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='full name')),
                ('state', models.CharField(blank=True, max_length=255, null=True, verbose_name='state')),
                ('complete_address', models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='complete address')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='phone number')),
                ('system_id', models.CharField(blank=True, default=None, max_length=250, null=True, verbose_name='system id')),
                ('city', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='city')),
                ('country', models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='country')),
                ('postal_code', models.CharField(blank=True, max_length=255, null=True, verbose_name='postal code')),
                ('about_me', models.TextField(blank=True, default='', null=True, verbose_name='about me')),
                ('profile_pic', apps.core.custom_model_fields.Base64Field(blank=True, null=True)),
                ('country_code', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('wishlist', models.ManyToManyField(blank=True, related_name='wishlist', to='store.product')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', apps.users.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('users.users',),
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('users.users',),
        ),
        migrations.CreateModel(
            name='SuperAdmin',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('users.users',),
        ),
        migrations.AddField(
            model_name='users',
            name='admin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_customers', to='users.admin'),
        ),
    ]
