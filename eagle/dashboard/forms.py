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

   


class AgentForm(ModelForm):
	class Meta:
		model = Agent
		fields = '__all__'
            
class CustomerForm(ModelForm):
	class Meta:
		model = Customer
		fields = '__all__'
            

