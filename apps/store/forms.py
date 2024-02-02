# apps/core/forms.py

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from apps.core.custom_model_fields import Base64Field
from apps.core.utils import resize_image
from .models import LABEL_CHOICES, PAGES_CATEGORY, CmsSocials, ContactQueries, Pages, Slide
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Category
from django.utils.text import slugify
from django_ckeditor_5.widgets import CKEditor5Widget
from django_select2.forms import Select2MultipleWidget


from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.utils.text import slugify
from .models import Category
from .models import Product, Category, Tag



class SlideForm(forms.ModelForm):
    class Meta:
        model = Slide
        fields = ['caption1', 'caption2', 'link', 'image']
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*','class':"form-control"})
        }
    

    def __init__(self, *args, **kwargs):
        super(SlideForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_enctype = 'multipart/form-data'  # Add this line for file uploads
        self.helper.add_input(Submit('submit', 'Save', css_class='btn-primary'))

    def clean_link(self):
        link = self.cleaned_data['link']
        # Add your URL validation logic here
        # For example, you can use Django's URLValidator
        from django.core.validators import URLValidator
        from django.core.exceptions import ValidationError as DjangoValidationError

        url_validator = URLValidator()

        try:
            url_validator(link)
        except DjangoValidationError:
            raise ValidationError('Invalid URL')

        return link

    # def clean_image(self):
    #     image = self.cleaned_data['image']

    #     base64_data = Base64Field().to_base64(image)

    #     return base64_data

    def save(self, commit=True):
        
        instance = super(SlideForm, self).save(commit=False)
        slide_id = self.cleaned_data.get('slide_id')

        if self.cleaned_data['image']:
            image = self.cleaned_data['image']
            image = resize_image(image,1920,570)
            # Convert the file to base64 and store it in the Base64Field
            instance.image = image
        
        # If slide_id is provided, set the instance id for updating
        if slide_id:
            self.cleaned_data.pop('slide_id')
            self.cleaned_data['image'] = instance.image
            Slide.objects.filter(pk=slide_id).update(**self.cleaned_data)

        if not slide_id and commit:
            instance.save()


        return instance
    

# class SlideEditForm(forms.ModelForm):
#     class Meta:
#         model = Slide
#         fields = ['caption1', 'caption2', 'link', 'image', 'is_active']

#     def __init__(self, *args, **kwargs):
#         super(SlideEditForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_method = 'post'
#         self.helper.form_class = 'form-horizontal'
#         self.helper.label_class = 'col-lg-2'
#         self.helper.field_class = 'col-lg-8'
#         self.helper.add_input(Submit('submit', 'Update'))





class CategoryCreateForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
        max_length=255,
        help_text="Enter a unique category name."
    )

    image = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control"}),
        required=False,
        help_text="Upload an image for the category."
    )

    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False,
        help_text="Check to make the category active."
    )

    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        # self.helper = FormHelper()
        # self.helper.form_method = 'post'
        # self.helper.add_input(Submit('submit', 'Create', css_class='btn-primary'))

    def clean_name(self):
        name = self.cleaned_data['name']
        # Validate that the name is unique
        if Category.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("Category with this name already exists.")
        return name

    def clean_image(self):
        image = self.cleaned_data['image']
        # Add any additional validation for the image field if needed
        return image

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(self.cleaned_data['name'])
        if self.cleaned_data['image']:
            image = self.cleaned_data['image']
            image = resize_image(image,1920,570)
            # Convert the file to base64 and store it in the Base64Field
            instance.image = image

        if commit:
            instance.save()

        return instance


class CategoryEditForm(forms.ModelForm):

    id = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
        max_length=255,
        help_text="Enter a unique category name."
    )


    image = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control"}),
        required=False,
        help_text="Upload an image for the category."
    )

    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False,
        help_text="Check to make the category active."
    )

    class Meta:
        model = Category
        fields = ['id','name', 'description', 'image', 'is_active']
        # widgets = {
        #       "description": CKEditor5Widget(
        #           attrs={"class": "django_ckeditor_5"}, config_name="description"
               
        #       )
        #   }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False

    def clean_name(self):
        name = self.cleaned_data['name']
        # Validate that the name is unique
        if Category.objects.filter(name__iexact=name).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Category with this name already exists.")
        return name

    def clean_image(self):
        image = self.cleaned_data['image']
        # Add any additional validation for the image field if needed
        return image

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(self.cleaned_data['name'])
        if  self.cleaned_data['image'] and type(self.cleaned_data['image']) not in [str,None]:
            image = self.cleaned_data['image']
            image = resize_image(image,1920,570)
            # Convert the file to base64 and store it in the Base64Field
            instance.image = image
        
        if commit:
            instance.save()

        return instance


class ProductCreateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['slug']

    image = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control"}),
        required=False,
        help_text="Upload an image for the category."
    )
    

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label=None,
        required=True,
        widget=forms.Select(attrs={'class': 'custom-form-control'}),
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-width': '100%'}),
        required=True
    )
    label = forms.ChoiceField(choices=LABEL_CHOICES, widget=forms.Select(attrs={'class': 'custom-form-control'}), required=True)


    def clean_sku(self):
        sku = self.cleaned_data['sku']
        # Check if a product with the same SKU already exists
        if Product.objects.filter(sku=sku).exists():
            raise forms.ValidationError("A product with this SKU already exists.")
        return sku
    
    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

    def clean_discounted_price(self):
        discounted_price = self.cleaned_data['discounted_price']
        price = self.cleaned_data.get('price', 0)
        if discounted_price is not None and discounted_price >= price:
            raise forms.ValidationError("Discounted price must be less than the original price.")
        return discounted_price
    
    def __init__(self, *args, **kwargs):
        super(ProductCreateForm, self).__init__(*args, **kwargs)
        self.fields["description_long"].required = False

        # Set labels to empty string to remove them
        
        for field_name, field in self.fields.items():
            field.label = ''

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(self.cleaned_data['name'])
        if  self.cleaned_data['image'] and type(self.cleaned_data['image']) not in [str,None]:
            image = self.cleaned_data['image']
            image = resize_image(image,1920,570)
            # Convert the file to base64 and store it in the Base64Field
            instance.image = image
        
        if commit:
            instance.save()
            # Set the tags for the created product
            tags = self.cleaned_data.get('tags', [])
            instance.tags.set(tags) 

        return instance

# forms.py
class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        exclude = ['slug']

    id = forms.CharField(
            widget=forms.HiddenInput(),
            required=False,
        )
    image = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control"}),
        required=False,
        help_text="Upload an image for the product."
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label=None,
        required=True,
        widget=forms.Select(attrs={'class': 'custom-form-control'}),
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=Select2MultipleWidget(attrs={'data-width': '100%'}),
        required=True
    )

    label = forms.ChoiceField(choices=LABEL_CHOICES, widget=forms.Select(attrs={'class': 'custom-form-control'}), required=True)

    sku = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
        required=True,
        help_text="Stock Keeping Unit (SKU) is a unique identifier for each product."
    )

    def __init__(self, *args, **kwargs):
        super(ProductUpdateForm, self).__init__(*args, **kwargs)
        self.fields["description_long"].required = False
        self.fields["sku"].disabled = True

        # Set initial value for tags field
        if self.instance.pk:
            self.fields['tags'].initial = self.instance.tags.all()

        # Set labels to empty string to remove them
        for field_name, field in self.fields.items():
            field.label = ''

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(self.cleaned_data['name'])
        if  self.cleaned_data['image'] and type(self.cleaned_data['image']) not in [str,None]:
            image = self.cleaned_data['image']
            image = resize_image(image,1920,570)
            # Convert the file to base64 and store it in the Base64Field
            instance.image = image

        # Set the tags for the created product
        tags = self.cleaned_data.get('tags', [])
        instance.tags.set(tags)
        
        if commit:
            instance.save()

        return instance
    

    
class CreatePagesForm(forms.ModelForm):
    class Meta:
        model = Pages
        fields = ['name', 'category', 'content', 'is_active']

    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False,
        help_text="Check to make the page active."
    )

    category = forms.ChoiceField(choices=PAGES_CATEGORY, widget=forms.Select(attrs={'class': 'custom-form-control'}), required=True)

    def __init__(self, *args, **kwargs):
        super(CreatePagesForm, self).__init__(*args, **kwargs)
        self.fields["content"].required = False
        # Set labels to empty string to remove them
        for field_name, field in self.fields.items():
            field.label = ''

    def clean_name(self):
        name = self.cleaned_data['name']
        
        # Validate that the name contains only letters
        # if not name.isalpha():
        #     raise forms.ValidationError('Name can only contain letters.')

        # Validate uniqueness of the name
        if Pages.objects.filter(name=name).exists():
            raise forms.ValidationError('A page with this name already exists.')

        return name
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(self.cleaned_data['name'])
        
        if commit:
            instance.save()

        return instance
    
class UpdatePagesForm(forms.ModelForm):
    class Meta:
        model = Pages
        fields = ['name', 'category', 'content', 'is_active']

    category = forms.ChoiceField(choices=PAGES_CATEGORY, widget=forms.Select(attrs={'class': 'custom-form-control'}), required=True)

    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        required=False,
        help_text="Check to make the page active."
    )

    def clean_name(self):
        name = self.cleaned_data['name']
        
        # # Validate that the name contains only letters
        # if not name.isalpha():
        #     raise forms.ValidationError('Name can only contain letters.')

        # Check uniqueness of the name for other pages
        existing_pages = Pages.objects.exclude(id=self.instance.id)
        if existing_pages.filter(name=name).exists():
            raise forms.ValidationError('A page with this name already exists.')

        return name
    
    def __init__(self, *args, **kwargs):
        super(UpdatePagesForm, self).__init__(*args, **kwargs)
        self.fields["content"].required = False
        # Set labels to empty string to remove them
        for field_name, field in self.fields.items():
            field.label = ''

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(self.cleaned_data['name'])
        
        if commit:
            instance.save()

        return instance


class AnswerQueryForm(forms.ModelForm):
    class Meta:
        model = ContactQueries
        fields = ['id', 'answer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label = ''

        # Customize the form fields if needed, e.g., set widget attributes
        self.fields['answer'].required = False


class CmsSocialsForm(forms.ModelForm):
    class Meta:
        model = CmsSocials
        fields = ['facebook_url', 'instagram_url', 'twitter_url', 'youtube_url', 'pinterest_url']

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label = ''
            field.requied = False