# forms.py
from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from .models import Admin,Payments,Agent,Customer

class UserRegistrationForm(forms.ModelForm):
    password_confirmation = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Admin
        fields = ['username', 'email', 'password']

    def clean_password_confirmation(self):
        password = self.cleaned_data.get('password')
        password_confirmation = self.cleaned_data.get('password_confirmation')

        if password and password_confirmation and password != password_confirmation:
            raise ValidationError("Passwords do not match.")

        return password_confirmation


class UserLoginForm(forms.Form):
   class Meta:
        model = Admin
        fields = ['username', 'password']




class PaymentsForm(forms.ModelForm):
    class Meta:
        model = Payments
        fields = ['amount_paid']

   



class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['agent_id', 'username', 'email', 'phone_number']
        # If you want to customize labels or widgets, you can do it here
        labels = {
            'agent_id': 'Agent ID',
            'username': 'Username',
            'email': 'Email',
            'phone_number': 'Phone Number',
           
        }
        widgets = {
            'agent_id': forms.TextInput(attrs={'placeholder': 'Enter agent_id'}),
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
            
        }

           


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_id', 'username', 'email', 'phone_number', 'payment_category']
        # If you want to customize labels or widgets, you can do it here
        labels = {
            'customer_id': 'Customer ID',
            'username': 'Username',
            'email': 'Email',
            'phone_number': 'Phone Number',
            'payment_category': 'Payment Category',
        }
        widgets = {
            'customer_id': forms.TextInput(attrs={'placeholder': 'Enter customer_id'}),
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter  phone number'}),
            'payment_category': forms.TextInput(attrs={'placeholder': 'Enter payment category'}),
        }

class CustomerFormEdit(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['username', 'email','phone_number', 'payment_category'] 
        labels = {
            'username': 'Username',
            'email': 'Email',
            'phone_number': 'Phone Number',
            'payment_category': 'Payment Category',
        }
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Edit email'}),
            'payment_category': forms.TextInput(attrs={'placeholder': 'Edit payment category'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Edit  phone number'}),
        }


class AgentEditForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['username', 'email', 'phone_number']
        # If you want to customize labels or widgets, you can do it here
        labels = {
            
            'username': 'Username',
            'email': 'Email',
            'phone_number': 'Phone Number',
           
        }
        widgets = {
            
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
            
        }
