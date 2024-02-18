# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.users.models import Admin, Customer, Users
import re
import phonenumbers
from django.core.exceptions import ValidationError
from datetime import datetime




class FieldValidators:
    @staticmethod
    def validate_email(value):
        if not value or not value.strip():
            raise ValidationError('Email is required.')
        # Add additional email validation logic if needed
        return value

    @staticmethod
    def validate_username(value):
        if not value or not value.strip():
            raise ValidationError('Username is required.')
        # Add additional username validation logic if needed
        return value

    @staticmethod
    def validate_phone_number(value):
        if not value or not value.strip():
            raise ValidationError('Phone number is required.')
        try:
            parsed_phone_number = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed_phone_number):
                raise ValidationError('Enter a valid phone number.')
        except phonenumbers.NumberParseException:
            raise ValidationError('Enter a valid phone number.')

        if Users.objects.filter(phone_number=value).exists():
            raise ValidationError('This phone number is already in use.')

        return value




class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                # "placeholder": "Username",
                "class": "form-control",
                "autocomplete": "off"  # Disable autocomplete

            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                # "placeholder": "Password",
                "class": "form-control",
                "autocomplete": "off"  # Disable autocomplete

            }
        ))
    



class SignUpForm(UserCreationForm):
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
        validators=[FieldValidators.validate_email]
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                # "placeholder": "Phone Number",
                "class": "form-control"
            }
        ),
        validators=[FieldValidators.validate_phone_number]
    )
    
    dob = forms.DateField(widget=forms.DateInput(attrs={
    'type': 'date',
    'class': 'form-control datetimepicker-input',
    'max': datetime.now().date(),
    'label_suffix': ''  # Hide the label
}))
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                # "placeholder": "Address",
                "class": "form-control",
                "required": "false"
            }
        )
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


    class Meta:
        model = Users
        fields = ('username', 'email', 'phone_number', 'dob', 'address', 'password1', 'password2')



class AdminCreationForm(UserCreationForm):


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
        validators=[FieldValidators.validate_email]
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                # "placeholder": "Phone Number",
                "class": "form-control"
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
    
    class Meta:
        model = Admin
        fields = ['username', 'email', 'password1', 'password2', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'admin'
        if commit:
            user.save()
        return user
    


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



