# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path,re_path
from apps.users.views import *

app_name='users'

urlpatterns = [
    # path('login/', LoginView.as_view(), name="login"),
    path('login/', AdminstratorLoginView.as_view(), name="login"),
    # path('auth0-login/', Auth0LoginAPIView.as_view(), name='auth0-login'),
    # path('auth0-callback/', Auth0CallbackAPIView.as_view(), name='auth0-callback'),
    # path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name="register"),
    path('', HomeView.as_view(), name='home'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('admins/', AdminListView.as_view(), name='admins'),
    path('profile/', ProfileEditView.as_view(), name='profile'),
    path('update-profile-pic/', UpdateProfilePic.as_view(), name='update-profile-pic'),
    path('customers-data/', CustomersDataView.as_view(), name='customers-data'),
    path('customers/', CustomersTemplateView.as_view(), name='customers'),






    re_path(r'^.*\.*', pages, name='pages'),

]
