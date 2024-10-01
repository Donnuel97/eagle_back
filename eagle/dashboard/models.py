from django.db import models
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from datetime import timedelta

class Admin(models.Model):
    username = models.CharField(max_length=30, unique=True, default='admin')
    email = models.EmailField(unique=True, default='admin')
    password = models.CharField(max_length=128, default='july1234')  # Use a secure method like bcrypt
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    phone_nunmber = models.CharField(max_length=11,null=True)

    def save(self, *args, **kwargs):
        # Hash the password before saving to the database
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class Agent(models.Model):
    STATUS_CHOICES = (
        (1, 'Active'),
        (0, 'Suspended'),
    )
    
    agent_id = models.CharField(primary_key=True, max_length=50, unique=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    phone_number = models.CharField(max_length=11, null=True, unique=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)  # Default to active

    def __str__(self):
        return self.username

class Customer(models.Model):
    STATUS_CHOICES = [
        (0, 'Suspended'),
        (1, 'Active'),
    ]

    customer_id = models.CharField(primary_key=True, max_length=50, unique=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    payment_category = models.IntegerField(default=0)
    phone_number = models.CharField(max_length=11, null=True, unique=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    activation_expiry = models.DateTimeField(null=True, blank=True)  # Field for timer

    def __str__(self):
        return self.username

    def is_timer_active(self):
        """Returns whether the customer is active and the timer has not expired."""
        if self.status == 1 and self.activation_expiry:
            return timezone.now() <= self.activation_expiry
        return False

    def activate_with_timer(self, duration_days=365):
        """Activate customer and set a timer for the given duration in days."""
        self.status = 1
        self.activation_expiry = timezone.now() + timedelta(days=duration_days)
        self.save()

    
    

class Category(models.Model):
    name = models.CharField(max_length=255)

    #this function rediects especially for class based views
    def __str__(self):
        return self.name


class Test(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='test')
    amount_paid = models.IntegerField(default=0)
    payment_duration = models.IntegerField(default=0)
    description = models.CharField(max_length=200, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True, null=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)  

    def __str__(self):
        return f"{self.customer.username} - {self.amount_paid} - {self.payment_date}"

class Payments(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.IntegerField(default=0)
    payment_duration = models.IntegerField(default=0)
    description = models.CharField(max_length=200, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True, null=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)  

    # New field to reference the agent who receives the payment
    received_by = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_payments')

    def save(self, *args, **kwargs):
        # Ensure payment_category is an integer if it's not null or zero
        if self.customer.payment_category and self.customer.payment_category != 0:
            self.payment_duration = int(self.amount_paid / int(self.customer.payment_category))

        self.payment_date = timezone.now()

        # Calculate expiry date based on previous payment if available
        previous_payment = self.customer.payments.order_by('-payment_date').first()
        if previous_payment:
            self.expiry_date = previous_payment.expiry_date + timezone.timedelta(days=self.payment_duration)
        else:
            self.expiry_date = self.payment_date + timezone.timedelta(days=self.payment_duration)

        if self.expiry_date is not None:
            if self.expiry_date < timezone.now():
                self.status = "Expired"
            else:
                self.status = "Active"
        
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.customer.username} - {self.amount_paid} - {self.payment_date}"


class SiteSettings(models.Model):
    logo_header_color = models.CharField(max_length=20, default='dark')
    navbar_color = models.CharField(max_length=20, default='white')
    sidebar_color = models.CharField(max_length=20, default='dark')

    def __str__(self):
        return "Site Settings"