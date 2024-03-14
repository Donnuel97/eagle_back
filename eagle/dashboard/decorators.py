from django.http import HttpResponse
from functools import wraps

def agent_login_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Check if agent is logged in
        if 'agent_id' not in request.session:
            return HttpResponse('You need to log in as an agent.')

        # If logged in, execute the original view
        return view_func(request, *args, **kwargs)

    return wrapped_view

def customer_login_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Check if customer is logged in
        if 'customer_id' not in request.session:
            return HttpResponse('You need to log in as a customer.')

        # If logged in, execute the original view
        return view_func(request, *args, **kwargs)

    return wrapped_view

from django.shortcuts import redirect

def login_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if 'username' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login_admin')  # Redirect to your login page
    return wrapped_view
