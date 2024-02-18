from django.db import models
from django.utils.text import slugify
from apps.core.custom_model_fields import Base64Field
from apps.users.models import Admin, Customer, Users
from apps.core.models import AbstractBaseModel
from django_countries.fields import CountryField
from django_ckeditor_5.fields import CKEditor5Field
from django.urls import reverse,reverse_lazy
from django_resized import ResizedImageField



# Create your models here.
CATEGORY_CHOICES = (
   ('Store', 'Shirts And Blouses'),
    ('TS', 'T-Shirts'),
    ('SK', 'Skirts'),
    ('HS', 'Hoodies&Sweatshirts')
)

# Create your models here.
PAGES_CATEGORY = (
    
     ('consumer policy', 'Consumer Policy'),
    ('help', 'Help'),
    ('about', 'About'),
    ('group companies', 'Group Companies')
)

LABEL_CHOICES = (
    ('S', 'sale'),
    ('N', 'new'),
    ('P', 'promotion')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)


class Category(AbstractBaseModel):
    name = models.CharField(max_length=255)
    description = CKEditor5Field('Text', config_name='extends')
    slug = models.SlugField(unique=True, blank=True)
    image = ResizedImageField(size=[1920, 570],force_format="WEBP", quality=75, upload_to='bucket/categories',null=True,blank=True)


    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Tag(AbstractBaseModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Product(AbstractBaseModel):
    name = models.CharField(max_length=255)
    description_long = CKEditor5Field('Text', config_name='extends')
    description_short = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sku = models.CharField(max_length=50, unique=True)
    # image = ResizedImageField(size=[1920, 570],force_format="WEBP", quality=75, upload_to='bucket/products',null=True,blank=True)
    tags = models.ManyToManyField(Tag)
    brand = models.CharField(max_length=255, null=True, blank=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, blank=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)


    def get_absolute_url(self):
        return reverse("frontend:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("frontend:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("frontend:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = ResizedImageField(size=[1920, 570], force_format="WEBP", quality=75, upload_to='bucket/products/images', null=True, blank=True)


class Review(AbstractBaseModel):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()

    def __str__(self):
        return f"{self.user} - {self.product}"

class BillingAddress(AbstractBaseModel):
    customer = models.ForeignKey(Users, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False,null=True,blank=True)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer} - {self.street_address}, {self.apartment_address}, {self.country}, {self.zip}"


    class Meta:
        verbose_name_plural = 'BillingAddresses'

# class Cart(AbstractBaseModel):
#     customer = models.ForeignKey(Users, on_delete=models.CASCADE)
#     products = models.ManyToManyField(Product, through='CartProduct')
#     quantity = models.IntegerField()

#     def __str__(self):
#         return f"Cart - {self.customer}"

# class CartProduct(AbstractBaseModel):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.IntegerField()    



class Order(AbstractBaseModel):
    customer = models.ForeignKey(Users, on_delete=models.CASCADE,null=True,blank=True)
    ref_code = models.CharField(max_length=20,null=True,blank=True)
    items = models.ManyToManyField('OrderItem',
                                    related_name='order_items',
                                    through='OrderItemQuantity'
                                    )
    start_date = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    ordered_date = models.DateTimeField(default=None)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'BillingAddress', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'BillingAddress', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'payments.Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.pk} - {self.customer}"

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total




class OrderItem(AbstractBaseModel):
    customer = models.ForeignKey(Users, on_delete=models.CASCADE,null=True,blank=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Product, on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discounted_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discounted_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class OrderItemQuantity(AbstractBaseModel):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

class Coupon(AbstractBaseModel):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    expiration_date = models.DateField()

    def __str__(self):
        return self.code
    


class Shipping(AbstractBaseModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=50)
    carrier = models.CharField(max_length=50)

    def __str__(self):
        return f"Shipping - {self.order}"

class Promotion(AbstractBaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name



class Slide(AbstractBaseModel):
    caption1 = models.CharField(max_length=100)
    caption2 = models.CharField(max_length=100)
    link = models.CharField(max_length=100)
    image = ResizedImageField(size=[1920, 570],force_format="WEBP", quality=75, upload_to='bucket/slides',help_text="Size: 1920x570",null=True,blank=True)


    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {}".format(self.caption1, self.caption2)
    

# Create your models here.
# CATEGORY_CHOICES = (
#     ('consumer_policy', 'Consumer Policy'),
#     ('help', 'Help'),
#     ('about', 'About'),
#     ('group_companies', 'Group Companies')
# )

class Pages(AbstractBaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(null=True,blank=True)
    category = models.CharField(max_length=50, choices=PAGES_CATEGORY)
    content = CKEditor5Field('Text', config_name='extends')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Generate slug from the name
        self.slug = slugify(self.name)

        super(Pages, self).save(*args, **kwargs)

    class Meta:
        unique_together = ['slug', 'category']


class Feedback(AbstractBaseModel):
    email = models.EmailField()
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    feedback =  CKEditor5Field('Text', config_name='comment')


    def __str__(self):
        return f"Feedback from {self.email}"
    

class ContactQueries(AbstractBaseModel):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False)
    email = models.EmailField()
    query = CKEditor5Field('Text', config_name='comment')
    answer = CKEditor5Field('Text', config_name='comment')
    query_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"ContactQuery #{self.id} - {self.customer.username}"



class CmsSocials(models.Model):
    admin = models.OneToOneField(Admin, on_delete=models.CASCADE)
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    pinterest_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Social Profiles"