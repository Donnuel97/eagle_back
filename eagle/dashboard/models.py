from django.db import models
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password

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
    agent_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    phone_nunmber = models.CharField(max_length=11,null=True)

    def __str__(self):
        return self.username
    
    

class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    payment_category = models.IntegerField(default=0)
    phone_nunmber = models.CharField(max_length=11,null=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=255)

    #this function rediects especially for class based views
    def __str__(self):
        return self.name



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
        if self.customer.payment_category != 0:
            self.payment_duration = int(self.amount_paid / self.customer.payment_category)

        self.payment_date = timezone.now()

        if self.payment_duration:
            self.expiry_date = self.payment_date + timezone.timedelta(days=self.payment_duration)

        if self.expiry_date is not None:
            if self.expiry_date < timezone.now():
                self.status = "Expired"
            else:
                self.status = "Active"
        
        if self.customer.payment_category != 0 and self.amount_paid % self.customer.payment_category != 0:
            raise ValidationError("Invalid Entry.")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.username} - {self.amount_paid}"

