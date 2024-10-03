# views.py
from .decorators import agent_login_required,customer_login_required,login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm,AgentForm, CustomerForm, PaymentsForm,CustomerFormEdit,AgentEditForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password, check_password
from django.views.generic import ListView,  DetailView, TemplateView, DeleteView
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import datetime
import logging
from django.core.mail import send_mail

# Create a logger
logger = logging.getLogger(__name__)

def test(request):
    agent_name = request.session.get('agent_name', None)
    return render(request, 'dashboard/admin2/register_client.html')

@csrf_exempt
def fetch_customer_data(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        try:
            customer = get_object_or_404(Customer, customer_id=customer_id)
        except Customer.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Customer not found.'})

        if customer.status == 0:
            return JsonResponse({'status': 'error', 'message': 'Customer account is suspended.'})

        return JsonResponse({
            'customer': {
                'username': customer.username,
                'email': customer.email,
                'phone_number': customer.phone_number,
                'payment_category': customer.payment_category
            },
            'status': 'success'
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@csrf_exempt
def submit_payment(request):
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer_id')
            amount_paid = request.POST.get('amount_paid')
            description = request.POST.get('description')
            received_by_username = request.POST.get('received_by')  # Assuming you're passing the agent's username

            # Convert the numeric fields to appropriate types
            try:
                amount_paid = float(amount_paid)  # Convert amount to float
            except ValueError:
                return JsonResponse({'status': 'Invalid amount paid value'}, status=400)

            logger.debug(f"Received data: customer_id={customer_id}, amount_paid={amount_paid}, description={description}, received_by={received_by_username}")

            # Fetch the customer
            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                return JsonResponse({'status': 'Customer does not exist'}, status=404)

            # Fetch the Agent using the `username`
            try:
                agent = Agent.objects.get(username=received_by_username)  # Use `username` to get the agent
            except Agent.DoesNotExist:
                return JsonResponse({'status': 'Agent does not exist'}, status=404)

            # Get the customer's payment category
            payment_category = customer.payment_category
            if payment_category <= 0:
                return JsonResponse({'status': 'Invalid payment category for customer'}, status=400)

            # Check if the amount_paid is divisible by the payment_category
            if amount_paid % payment_category != 0:
                return JsonResponse({'status': 'Amount paid is not divisible by payment category'}, status=400)

            # Calculate the payment duration (daily basis)
            payment_duration = int(amount_paid // payment_category)  # Division to calculate the duration in days

            # Create the payment record
            payment = Payments.objects.create(
                customer=customer,
                amount_paid=amount_paid,
                payment_duration=payment_duration,  # Save the calculated payment duration
                description=description,
                received_by=agent  # Pass the agent instance here
            )

            logger.info(f"Payment created successfully for customer {customer_id}.")
            return JsonResponse({'status': 'Payment successful'})

        except Exception as e:
            logger.error(f"An error occurred while processing the payment: {e}")
            return JsonResponse({'status': str(e)}, status=500)

    return JsonResponse({'status': 'Invalid request'}, status=400)


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

# 2. Customer register view
@login_required
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
    return render(request, 'dashboard/admin2/register_client.html', context)

# 3. Agent register view
@login_required
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
    return render(request, 'dashboard/admin2/register_agent.html', context)


# All Login views
# 1. Admin login view
def login_admin(request):
    error_message = ''  # Initialize error_message with an empty string

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Admin.objects.get(username=username)
        except Admin.DoesNotExist:
            # Display a generic error message
            messages.error(request, 'Invalid username or password')
            return redirect('login_admin')  # Redirect back to the login page

        # Use check_password to compare hashed passwords
        if check_password(password, user.password):
            request.session['username'] = user.username
            # Passwords match, redirect to home
            return redirect('home')  # Assuming 'home' is a valid URL pattern
        else:
            # Set error_message for invalid password
            error_message = "Invalid username or password"
            return redirect('login_admin')

    # Pass error_message as context to the template
    return render(request, 'registration/login.html', {'error_message': error_message})

# 2. Agent login view
def login_agent(request):
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')

        try:
            user = Agent.objects.get(agent_id=agent_id)
            agent_name = user.username  # Fetch agent name
        except Agent.DoesNotExist:
            return render(request, 'registration/agent_login.html', {'error': 'Agent does not exist'})

        # Check if the agent is suspended
        if user.status == 0:
            return render(request, 'registration/agent_login.html', {'error': 'Your account is suspended. Please contact support.'})

        # Store agent_id and agent_name in session if the agent is active
        request.session['agent_id'] = user.agent_id
        request.session['agent_name'] = agent_name  # Store agent name in session
        return redirect('payment_start')  # Redirect after successful login

    return render(request, 'registration/agent_login.html')




# 3. client login/payment starting view
@agent_login_required
def payment_start(request):
    agent_name = request.session.get('agent_name', None)
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        try:
            user = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return HttpResponse('Customer does not exist')

        request.session['customer_id'] = user.customer_id
        return redirect('payment', user_id=user.customer_id)
    
    return render(request, 'dashboard/agent2/agent_dash.html', {'agent_name': agent_name})



# Payment History view
# 1
def client_payment_history(request, user_id):
    user = get_object_or_404(Customer, customer_id=user_id)
    user_payments = Payments.objects.filter(customer__customer_id=user_id)
    return render(request, 'dashboard/agent/history.html', {'user': user, 'user_payments': user_payments})

def admin_payment_history(request, user_id):
    user = get_object_or_404(Customer, customer_id=user_id)
    user_payments = Payments.objects.filter(customer__customer_id=user_id)
    return render(request, 'dashboard/admin2/payment_history.html', {'user': user,'user_payments': user_payments})

    

    
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

            # Redirect to another page upon successful payment
            return redirect(reverse('payment_start'))  # Replace 'success_page' with the name of your success page URL pattern
        else:
            error_message = "Form is not valid"
    else:
        form = PaymentsForm()

    return render(request, 'dashboard/agent/form.html', {'user': user, 'form': form, 'success_message': success_message, 'error_message': error_message, 'agent_name': agent_name})

@method_decorator(login_required, name='dispatch')
class HomeView(TemplateView):
    template_name = 'dashboard/admin2/dashboard.html'
    
    def get_queryset(self):
        # You can customize the queryset here if needed
        return Customer.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate total amount paid
        total_amount_paid = Payments.objects.aggregate(total=Sum('amount_paid'))['total']
        if total_amount_paid is None:
            total_amount_paid = 0
        context['total_amount_paid'] = total_amount_paid
        
        # Other context data
        total_agents = Agent.objects.count()
        total_customer = Customer.objects.count()
        context['total_agents'] = total_agents
        context['total_customer'] = total_customer
        
        return context

@method_decorator(login_required, name='dispatch')
class Agentlist(ListView):
    model = Agent
    template_name = 'dashboard/admin2/agent_list.html'
    context_object_name = 'agent_list'  

    def get_queryset(self):
        return Agent.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_agents = Agent.objects.count()
        total_customers = Customer.objects.count()
        
        context['total_agents'] = total_agents
        context['total_customers'] = total_customers
       
        return context

class ToggleAgentStatusView(View):
    def post(self, request, *args, **kwargs):
        agent_id = request.POST.get('agent_id')
        agent = get_object_or_404(Agent, agent_id=agent_id)

        # Toggle status
        if agent.status == 1:
            agent.status = 0  # Suspend
        else:
            agent.status = 1  # Activate

        agent.save()
        return JsonResponse({'success': True, 'new_status': agent.status})


class EditAgentView(View):
    def post(self, request, *args, **kwargs):
        agent_id = request.POST.get('agent_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        agent = get_object_or_404(Agent, agent_id=agent_id)

        try:
            agent.username = username
            agent.email = email
            agent.phone_number = phone_number
            agent.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@method_decorator(login_required, name='dispatch')
class AgentEditView(UpdateView):
    model = Agent
    form_class = AgentEditForm
    template_name = 'dashboard/admin/agent_edit.html'
    success_url = reverse_lazy('agent_list')

    def form_valid(self, form):
        messages.success(self.request, 'Agent details updated successfully.')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')  
class CustomerList(ListView):
    model = Customer
    template_name = 'dashboard/admin2/client_list.html'
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


@csrf_exempt
def toggle_customer_status(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        new_status = int(request.POST.get('status'))
        activation_expiry = request.POST.get('activation_expiry')  # Get the selected expiry date

        try:
            customer = Customer.objects.get(customer_id=customer_id)
            
            if new_status == 1:
                if activation_expiry:
                    # Parse the date selected by the admin
                    activation_expiry_date = datetime.strptime(activation_expiry, '%Y-%m-%d')
                    customer.activation_expiry = activation_expiry_date
                else:
                    # Default expiry date to 1 year if no date is provided
                    customer.activation_expiry = timezone.now() + timedelta(days=365)
                
                customer.status = 1
            else:
                # Suspend the customer
                customer.status = 0
                customer.activation_expiry = None  # Clear expiry when suspended

            customer.save()

            return JsonResponse({'success': True, 'new_status': customer.status, 'expiry': customer.activation_expiry})
        except Customer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Customer not found'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

def edit_customer(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        payment_category = request.POST.get('payment_category')

        # Get the customer object
        customer = get_object_or_404(Customer, customer_id=customer_id)

        # Update customer details
        customer.username = username
        customer.email = email
        customer.phone_number = phone_number
        customer.payment_category = payment_category
        customer.save()

        # Return a success response
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


class CustomerDelete(DeleteView):
    model = Customer
    success_url = reverse_lazy('customer-list') 

@method_decorator(login_required, name='dispatch')
class CustomerEditView(UpdateView):
    model = Customer
    form_class = CustomerFormEdit
    template_name = 'dashboard/admin/customer_edit.html'
    success_url = reverse_lazy('customer_list')

    def form_valid(self, form):
        messages.success(self.request, 'Customer details updated successfully.')
        return super().form_valid(form)

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'dashboard/admin/confirm_delete.html'
    success_url = reverse_lazy('customer_list')

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
    return redirect('login_admin')  # Redirect to the login page after logout\



def get_site_settings(request):
    settings = get_object_or_404(SiteSettings)
    return JsonResponse({
        'logo_header_color': settings.logo_header_color,
        'navbar_color': settings.navbar_color,
        'sidebar_color': settings.sidebar_color,
    })

def save_site_settings(request):
    if request.method == 'POST':
        logo_header_color = request.POST.get('logo_header_color')
        navbar_color = request.POST.get('navbar_color')
        sidebar_color = request.POST.get('sidebar_color')

        settings = get_object_or_404(SiteSettings)
        settings.logo_header_color = logo_header_color
        settings.navbar_color = navbar_color
        settings.sidebar_color = sidebar_color
        settings.save()

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)