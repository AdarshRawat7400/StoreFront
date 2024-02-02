from django import forms
from apps.users.forms import FieldValidators
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from allauth.account.forms import LoginForm, SignupForm
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime
from apps.users.models import Users
from phonenumber_field.formfields import PhoneNumberField

from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.users.models import Admin, Customer, Users
import re
import phonenumbers
from django.core.exceptions import ValidationError
from datetime import datetime



PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1234 Main St',
        'class': 'form-control'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or suite',
        'class': 'form-control'
    }))
    # country = CountryField(blank_label='(select country)').formfield(
    #     widget=CountrySelectWidget(attrs={'class': 'custom-select d-block w-100'})
    # )
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class CustomLoginForm(LoginForm):

    def clean(self):
        cleaned_data = super().clean()

        # Access the authenticated user from self.user_cache
        user = self.user
        if user:
            # Assuming the User model has a profile with a role field
            user_role = user.role  # Replace with your actual attribute/method

            # Check if the role is "admin" or "superadmin"
            if user_role in ["admin", "superadmin"]:
                raise forms.ValidationError("You do not have permission to log in (customer login only).")

        return cleaned_data
    



class CustomSignUpForm(SignupForm,UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                # "placeholder": "Username",
                "class": "form-control"
            }
        ),
        validators=[FieldValidators.validate_username]
        )
    
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                # "placeholder": "Email",
                "class": "form-control"
            }
        ),
        validators=[FieldValidators.validate_email],
        required=True
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                # "placeholder": "Phone Number",
                "class": "form-control",
                "placeholder": "1234567890"
            }
        ),
        validators=[FieldValidators.validate_phone_number]
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                # "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                # "placeholder": "Password check",
                "class": "form-control"
            }
        ))
    

    def save(self, request):
        user = super().save(request)
        # Add additional values to the user model
        user.role = 'customer'
        user.save()

        return user


    class Meta:
        model = Users
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')




class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Users
        fields = [ 'username', 'email', 'first_name', 'last_name', 'phone_number', 'complete_address', 'city', 'country', 'postal_code', 'about_me']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['phone_number'].widget.attrs['class'] = 'form-control'
        self.fields['complete_address'].widget.attrs['class'] = 'form-control'
        self.fields['city'].widget.attrs['class'] = 'form-control'
        self.fields['city'].widget.attrs['required'] = False
        self.fields['country'].widget.attrs['class'] = 'form-control'
        self.fields['country'].widget.attrs['required'] = False
        self.fields['postal_code'].widget.attrs['class'] = 'form-control'
        self.fields['postal_code'].widget.attrs['required'] = False
        self.fields['about_me'].widget.attrs['class'] = 'form-control'
        self.fields['about_me'].widget.attrs['required'] = False
        self.fields['about_me'].widget.attrs['rows'] = 3


    
    def validate_phone_number(self,value):
        if not value or not value.strip():
            raise ValidationError('Phone number is required.')
        try:
            parsed_phone_number = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed_phone_number):
                raise ValidationError('Enter a valid phone number.')
        except phonenumbers.NumberParseException:
            raise ValidationError('Enter a valid phone number.')
    
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        self.validate_phone_number(phone_number)
        username = self.cleaned_data.get('username')
        existing_user = Users.objects.exclude(username=username).filter(phone_number=phone_number).first()
        if existing_user:
            raise forms.ValidationError('This phone number is already in use by another user.')
        return phone_number

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if not postal_code or not postal_code.strip():
            raise ValidationError('Postal code is required.')
        # Add additional postal code validation logic if needed
        return postal_code

    


    def save(self, commit=True):
        instance = super(ProfileUpdateForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance
