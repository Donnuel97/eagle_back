# views.py
from .decorators import agent_login_required,customer_login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from .models import *
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm,AgentForm, CustomerForm, PaymentsForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password, check_password
from django.views.generic import ListView,  DetailView, TemplateView
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.sessions.models import Session


# Register views:
# 1. Admin register view
class RegisterUserView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Check if passwords match before saving
            password = form.cleaned_data['password']
            password_confirmation = form.cleaned_data['password_confirmation']
            if password != password_confirmation:
                # Handle password mismatch error (e.g., add to form errors)
                form.add_error('password_confirmation', 'Passwords do not match.')
            else:
                # Passwords match, save the user
                admin = Admin(username=form.cleaned_data['username'],
                              email=form.cleaned_data['email'],
                              password=password)
                admin.save()
                # You can add login logic here if needed
                return redirect('home')  # Redirect to the home page after registration
        return render(request, 'registration/register.html', {'form': form})

# 3. Customer register view
def register_customer(request):
    form = CustomerForm()

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            # Set success message
            messages.success(request, 'Customer registered successfully!')
            # Redirect to the same page after successful form submission
            return redirect('register_customer')

    context = {'form': form}
    return render(request, 'dashboard/admin/register_customer.html', context)

# 3. Agent register view
def register_agent(request):
    form = AgentForm()

    if request.method == 'POST':
        form = AgentForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Customer registered successfully!')
            # Redirect to the same page after successful form submission
            return redirect('register_agent')

    context = {'form': form}
    return render(request, 'dashboard/admin/register_agent.html', context)

       
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Admin.objects.get(username=username)
        except Admin.DoesNotExist:
            return HttpResponse('Invalid username or password')

        # Use check_password to compare hashed passwords
        if check_password(password, user.password):
            request.session['username'] = user.username
            # Passwords match, redirect to home
            return redirect('home')
        else:
            # Passwords do not match
            return HttpResponse('Invalid username or password')

    return render(request, 'registration/login.html')



def login_agent(request):
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')

        try:
            user = Agent.objects.get(agent_id=agent_id)
        except Agent.DoesNotExist:
            return HttpResponse('Agent does not exist')

        # If the agent is found, store agent_id in session
        if user is not None:
            request.session['agent_id'] = user.agent_id
            return redirect('payment_start')
        else:
            return HttpResponse('Invalid ID')

    return render(request, 'registration/agent_login.html')

@agent_login_required
def payment_start(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')

        try:
            user = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return HttpResponse('Customer does not exist')

        if user:
            request.session['customer_id'] = user.customer_id
            # User exists, redirect to agent with user details
            return redirect('payment', user_id=user.customer_id)
        else:
            return HttpResponse('Invalid id')

    return render(request, 'dashboard/agent/payment_form.html')


def client_payment_history(request, user_id):
    user = get_object_or_404(Customer, customer_id=user_id)
    user_payments = Payments.objects.filter(customer__customer_id=user_id)
    return render(request, 'dashboard/agent/history.html', {'user': user, 'user_payments': user_payments})

def admin_payment_history(request, user_id):
    user = get_object_or_404(Customer, customer_id=user_id)
    user_payments = Payments.objects.filter(customer__customer_id=user_id)
    return render(request, 'dashboard/admin/payment_history.html', {'user': user,'user_payments': user_payments})

    

    
@customer_login_required
def payment(request, user_id):
    user = get_object_or_404(Customer, customer_id=user_id)
    success_message = None
    error_message = None

    # Retrieve agent_id and agent_name from session
    agent_id = None
    agent_name = None
    if 'agent_id' in request.session:
        agent_id = request.session['agent_id']
        try:
            agent = Agent.objects.get(agent_id=agent_id)
            agent_name = agent.username
        except Agent.DoesNotExist:
            pass  # Handle the case where agent_id does not correspond to any existing agent

    if request.method == 'POST':
        form = PaymentsForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.customer = user
            payment.received_by_id = agent_id  # Set the received_by field to agent_id

            # Additional validation
            if user.payment_category != 0 and payment.amount_paid % user.payment_category != 0:
                error_message = "Invalid amount entered, try again."
                return render(request, 'dashboard/agent/form.html', {'user': user, 'form': form, 'error_message': error_message, 'agent_name': agent_name})

            payment.save()
            success_message = 'Payment successful!'
            form = PaymentsForm()  # Reinitialize the form with an empty instance
        else:
            error_message = "Form is not valid"
    else:
        form = PaymentsForm()

    return render(request, 'dashboard/agent/form.html', {'user': user, 'form': form, 'success_message': success_message, 'error_message': error_message, 'agent_name': agent_name})

class HomeView(TemplateView):
    template_name = 'dashboard/admin/index.html'
    
    def get_queryset(self):
        # You can customize the queryset here if needed
        return Customer.objects.all()
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_agents = Agent.objects.count()
        total_customer = Customer.objects.count()
        context['total_agents'] = total_agents
        context['total_customer'] = total_customer
        return context



class Agentlist(ListView):
    model = Agent
    template_name = 'dashboard/admin/team.html'
    context_object_name = 'agent_list'  # Specify the context variable name for the queryset

    def get_queryset(self):
        # You can customize the queryset here if needed
        return Agent.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_agents = Agent.objects.count()
        total_customers = Customer.objects.count()
        
        # Fetch notifications (you need to implement this based on your notification mechanism)
        notifications = Payments.objects.filter(...)  # Adjust this filter based on your requirements
        
        context['total_agents'] = total_agents
        context['total_customers'] = total_customers
        context['notifications'] = notifications  # Add notifications to the context
        return context
    
class Customerlist(ListView):
    model = Customer
    template_name = 'dashboard/admin/customer_list.html'
    context_object_name = 'customer_list'  # Specify the context variable name for the queryset

    def get_queryset(self):
        # You can customize the queryset here if needed
        return Customer.objects.all()
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_agents = Agent.objects.count()
        total_customer = Customer.objects.count()
        context['total_agents'] = total_agents
        context['total_customer'] = total_customer
        return context
    
def agent_logout(request):
    if 'agent_id' in request.session:
        session_key = request.session.session_key
        request.session.flush()  # Clear the session data
        Session.objects.filter(session_key=session_key).delete()  # Delete the session from the database
    return redirect('/')  # Redirect to the login page after logout

def customer_logout(request):
    if 'customer_id' in request.session:
        session_key = request.session.session_key
        request.session.flush()  # Clear the session data
        Session.objects.filter(session_key=session_key).delete()  # Delete the session from the database
    return redirect('login')  # Redirect to the login page after logout\

def admin_logout(request):
    if 'username' in request.session:
        session_key = request.session.session_key
        request.session.flush()  # Clear the session data
        Session.objects.filter(session_key=session_key).delete()  # Delete the session from the database
    return redirect('login')  # Redirect to the login page after logout\
