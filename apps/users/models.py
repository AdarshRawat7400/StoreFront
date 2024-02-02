from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import AbstractBaseModel
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as BuiltInUserManager
from django.contrib.auth.models import PermissionsMixin
from apps.core.custom_model_fields import Base64Field
from django_countries.fields import CountryField


USER_ROLES = [
    ('customer', 'Customer'),
    ('admin', 'Admin'),
    ('superadmin', 'Super Admin'),
]

class UserManager(BuiltInUserManager):
    def create_superuser(self, username, password, **extra_fields):
        return Users.objects.create(
            password=make_password(password),
            username=username,
            role="superadmin",
            is_active=True,
            is_superuser=True,
            is_staff=True,
        )

    def get_queryset(self):
        return super().get_queryset()
    

class Users(AbstractBaseModel,AbstractBaseUser,PermissionsMixin):
    id = models.AutoField(primary_key=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    password = models.CharField(
        _("password"),
        max_length=128,
        blank=True,
        null=True,
        validators=[
            MinLengthValidator(limit_value=5, message="The password must be at least 5 characters.")
        ],
    )
    role = models.CharField(_("user type"), choices=USER_ROLES, max_length=30, default='user')
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Designates whether this user should be treated as active."),
    )
    username = models.CharField(
        _("username"),
        max_length=50,
        unique=True,
        validators=[
            MinLengthValidator(limit_value=4, message="The username must be at least 4 characters.")
        ],
    )
    first_name = models.CharField(_("first name"), max_length=50, blank=True,default='')
    last_name = models.CharField(_("last name"), max_length=50, blank=True,default='')
    balance = models.DecimalField(
        _("balance"), max_digits=15, decimal_places=2, default=0.00
    )

    email = models.EmailField(_("email"), max_length=255, null=True, blank=True)
    dob = models.DateField(_("dob"), null=True, blank=True)
    full_name = models.CharField(_("full name"), max_length=100, null=True, blank=True)
    state = models.CharField(_("state"), max_length=255, null=True, blank=True)
    complete_address = models.CharField(_("complete address"),max_length=500, null=True, blank=True,default='')
    phone_number = models.CharField(_("phone number"), max_length=20, null=True, blank=True)
    system_id = models.CharField(_("system id"), max_length=250, null=True, blank=True, default=None)
    admin = models.ForeignKey(
        "Admin",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="user_customers",
    )
    city = models.CharField(_("city"), max_length=255, null=True, blank=True,default='')
    country = models.CharField(_("country"), max_length=255, null=True, blank=True,default='')
    postal_code = models.CharField(_("postal code"), max_length=255, null=True, blank=True)
    about_me = models.TextField(_("about me"), null=True, blank=True,default='')
    profile_pic = Base64Field(null=True, blank=True)
    wishlist = models.ManyToManyField('store.Product', related_name='wishlist', blank=True)
    country_code = CountryField(blank_label='(select country)', null=True, blank=True)





    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['email']
    
    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.role == "user":
            self.is_admin = False
            self.is_superuser = False

        if not self.system_id and self.role != "superadmin":
            self.system_id = self.set_system_id()

        self.modified = timezone.now()
        return super().save(*args, **kwargs)

    def set_system_id(self):
        if self.role == "admin":
            return "A"
        elif self.role == "user":
            return "C"
        return None





class CustomerManager(models.Manager):
    def get_queryset(self):
        return super(CustomerManager, self).get_queryset().filter(role="customer")


class Customer(Users):
    objects = CustomerManager()

    class Meta:
        proxy = True


class AdminManager(models.Manager):
    def get_queryset(self):
        return super(AdminManager, self).get_queryset().filter(role="admin")


class Admin(Users):
    objects = AdminManager()

    class Meta:
        proxy = True


class SuperAdminManager(models.Manager):
    def get_queryset(self):
        return super(SuperAdminManager, self).get_queryset().filter(role="superadmin")


class SuperAdmin(Users):
    objects = SuperAdminManager()

    class Meta:
        proxy = True



