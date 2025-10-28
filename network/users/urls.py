"""
URL configuration for network project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from home.admin import seller_site

from rest_framework.routers import DefaultRouter
from users.views import RegistrationView,ProfileView,ContactUpdateView,UserAuthenticateView
router = DefaultRouter()
router.register(r'register', RegistrationView, basename='register')
router.register(r'contact_update', ContactUpdateView, basename='contact_update')


#router.register(r'profile', ProfileView, basename='ProfileView')


router.register(r'login',UserAuthenticateView,basename='login')

profile_router = DefaultRouter()
profile_router.register(r'', ProfileView, basename='profile') 


urlpatterns = [
    path('auth/', include(router.urls)),
    path('profile/', include(profile_router.urls)),

    # path('profile/', include(profile_router.urls)),
    # path('login/', include(login_router.urls)),


    #path('register/email/', EmailRegistrationAPI.as_view(), name='email_register'),
    
    
]
