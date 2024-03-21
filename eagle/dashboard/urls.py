# urls.py
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views
from .views import *

urlpatterns = [
  
    path('', login_agent, name='login_agent'),
    path('payment', payment_start, name='payment_start'),
    path('home/', views.HomeView.as_view(), name="home"),
    path('payment form/<str:user_id>/', payment, name='payment'),
  
    path('agents/', views.Agentlist.as_view(), name="agent_list"),
    path('customers/', views.CustomerList.as_view(), name="customer_list"),
    path('register agent/', register_agent, name='register_agent'),
    path('register customer/', register_customer, name='register_customer'),
    path('customer/edit/<str:pk>/', CustomerEditView.as_view(), name='customer_edit'),
    path('agent/edit/<str:pk>/', AgentEditView.as_view(), name='agent_edit'),
    #path('customer/<int:pk>/delete/', views.CustomerDelete.as_view(), name='customer_delete'),
    #path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('delete-customer/<str:pk>/', CustomerDelete.as_view(), name='delete-customer'),
    path('logout/', views.admin_logout, name='logout'),
    path('agent_logout/', views.agent_logout, name='agent_logout'), 
    path('register_admin/', RegisterUserView.as_view(), name='register_user'),
    path('payment-history/<str:user_id>/', views.client_payment_history, name='client_payment_history'),
     path('history/<str:user_id>/', views.admin_payment_history, name='admin_payment_history'),
    path('eagle_admin', login_admin, name='login_admin'),
    # Add other URLs as needed
]


