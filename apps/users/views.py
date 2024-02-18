# api/views.py

from apps.core.auth_mixins import CheckRolesMixin
from apps.core.custom_model_fields import Base64Field
from apps.users.forms import LoginForm
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
# api/views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseBadRequest
from django.views import View
from django.views.generic import CreateView
from django.views.generic.base import TemplateView

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse,reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout

from apps.users.models import Admin, Customer, Users
from apps.core.utils import convert_uploaded_file_to_webp, generate_random_password
from apps.users.noconflict import makecls
from .forms import AdminCreationForm, LoginForm, ProfileUpdateForm, SignUpForm
from apps.users.auth import oauth
from urllib.parse import urlencode, quote_plus
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib import messages

from django.http import JsonResponse

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q



# def login_view(request):
#     form = LoginForm(request.POST or None)

#     msg = None

#     if request.method == "POST":

#         if form.is_valid():
#             username = form.cleaned_data.get("username")
#             password = form.cleaned_data.get("password")
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect("/")
#             else:
#                 msg = 'Invalid credentials'
#         else:
#             msg = 'Error validating the form'

#     return render(request, "accounts/login.html", {"form": form, "msg": msg})

class Auth0LoginAPIView(APIView):
    def get(self, request):

        return oauth.auth0.authorize_redirect(
            request, request.build_absolute_uri(reverse("admin:auth0-callback"))
        )
    
    
class Auth0CallbackAPIView(APIView):
    def get(self, request):

        token = oauth.auth0.authorize_access_token(request)
        # Assuming 'token' is an instance of OAuth2Token
        request.session["user"] = token
        user_info = token.get('userinfo', {})
        random_password = generate_random_password()
        admin =  Admin.objects.first()

        user_data = {
            'username': user_info.get('sub'),
            'email': user_info.get('email'),
            'full_name': user_info.get('name'),
            'dob': user_info.get('birthdate'),
            'state': user_info.get('locale'),
            'complete_address': user_info.get('address'),
            'phone_number': user_info.get('phone_number'),
            'balance': 0.00,
            'role': 'customer',
            'is_active': True,
            'password': random_password,
            "admin" : admin # Use the random password generator
            # Add other fields as needed
        }

        # Try to get the user based on the Auth0 user_id
        user = Users.objects.filter(username=user_info.get('sub')).first()
        if user:
            # User already exists, update the user's data if needed
            user.email = user_data['email']
            user.full_name = user_data['full_name']
            user.dob = user_data['dob']
            user.state = user_data['state']
            user.complete_address = user_data['complete_address']
            user.phone_number = user_data['phone_number']
            user.set_password(random_password)
            user.save()
        else:
            # User doesn't exist, create a new user
            user = Users(**user_data)
            user.set_password(random_password)
            user.save()

        # Authenticate the user
        auth_user = authenticate(request, username=user.username, password=random_password)

        if auth_user:
            # Log the user in
            login(request, auth_user)

            # Redirect to the desired URL after login (replace 'your_redirect_url' with your URL)
            return redirect('admin:home')

        # Handle the case where authentication fails
        return redirect('admin:login')  # Redirect to the login page or handle accordingly





class LoginView(TemplateView):
    template_name = "backend/accounts/login.html"
    view_initkwargs = None  # Add this line


    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        msg = "Success Logged In Successfully"

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.role != 'customer':
                    msg = "User not Authorized (Customer Login Only)"
                    messages.error(request, msg)
                    return render(request, self.template_name, {"form": form, "msg": msg})

                login(request, user)
                messages.success(request, msg)
                return redirect("admin:home")
            else:
                msg = 'Invalid credentials'
                messages.error(request, msg)
        else:
            msg = 'Error validating the form'
            messages.error(request, msg)


        return render(request, self.template_name, {"form": form, "msg": msg})

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, self.template_name, {"form": form, "msg": None})
  




class LogoutView(View,CheckRolesMixin):
    allowed_roles = ('superadmin','admin','customer')
    def get(self, request):
        
        redirect_to =  "admin:login" if request.user.role == 'customer' else "admin:login"
        logout(request)
        return HttpResponseRedirect(reverse_lazy(redirect_to))


class RegisterView(TemplateView):
    template_name = "backend/accounts/register.html"

    def handle_no_permission(self):
        return HttpResponseRedirect(settings.LOGIN_URL)

    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        msg = None
        success = False

        if form.is_valid():
            user = form.save(commit=False) 
            admin = Admin.objects.first()
            user.role = 'customer'
            user.admin = admin

            user.save()
            # username = form.cleaned_data.get("username")
            # password = form.cleaned_data.get("password1")
            # auth_user = authenticate(request, username=username, password=password)

            # Log the user in
            # login(request, auth_user)
            messages.success(request, 'User created successfully. Please log in.')
            success = True
            return redirect("admin:login")

        else:
            msg = 'Form is not valid'

            messages.error(request, msg)

        return render(request, self.template_name, {"form": form, "msg": msg, "success": success})

    def get(self, request, *args, **kwargs):
        form = SignUpForm()
        return render(request, self.template_name, {"form": form, "msg": None})







class AdminstratorLoginView(TemplateView):
    template_name = "backend/accounts/administrator_login.html"

    def handle_no_permission(self):
        return HttpResponseRedirect(settings.LOGIN_URL)


    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        msg = "Logged In Successfully"

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.role in ['admin','superadmin']:
                    messages.success(request, msg)
                    login(request, user)
                    return redirect("admin:home")
                msg = "Superadmin/Login Login Only"
                messages.error(request, msg)
                return redirect("admin:login")

            else:
                msg = 'Invalid credentials'
                messages.error(request, msg)
        else:
            msg = 'Error validating the form'
            messages.error(request, msg)

        return render(request, self.template_name, {"form": form, "msg": msg})

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ['admin','superadmin','customer']:
            if request.user.role == 'customer':
                logout(request)
            else:
                return redirect('admin:home')
        
        form = LoginForm()
        return render(request, self.template_name, {"form": form, "msg": None})
  

class HomeView(CheckRolesMixin, TemplateView):
    allowed_roles = ("customer", "admin", "superadmin")
    template_name = 'backend/home/index.html'

    # def handle_no_permission(self):
    #     return HttpResponseRedirect(settings.LOGIN_URL)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'index'
        return context


class ProfileEditView(CheckRolesMixin, TemplateView):
    allowed_roles = ("admin")
    template_name = 'backend/home/profile.html'  # Update with your actual template name
    model = Customer  # Update with your actual user profile model if needed
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('users:profile')  # Replace 'profile' with the actual URL name for the user's profile page

    def post(self, request, *args, **kwargs):
        form = ProfileUpdateForm(request.POST, instance=request.user)  # Pass instance for updating existing user
        msg = None
        success = False

        if form.is_valid():
            user = form.save(commit=False)
            # if not user.admin:
            #     admin = Admin.objects.first()
            #     user.role = 'customer'
            #     user.admin = admin

            user.save()

            messages.success(request, 'Profile updated successfully.')
            success = True
            return redirect(self.success_url)

        else:
            msg = 'Form is not valid'
            messages.error(request, msg)

        return render(request, self.template_name, {"form": form, "msg": msg, "success": success})

    def get(self, request, *args, **kwargs):
        form = ProfileUpdateForm(instance=request.user)  # Pass instance for pre-populating existing user data
        return render(request, self.template_name, {"form": form,'user':request.user, "msg": None})


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('backend/home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('backend/home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('backend/home/page-500.html')
        return HttpResponse(html_template.render(context, request))





class AdminListView(CheckRolesMixin, View):
    template_name = "backend/accounts/admins.html"
    allowed_roles = ["superadmin"]

    @staticmethod
    def get_queryset(user_name):
        queryset = Admin.objects.all().order_by("-created")
        if user_name:
            queryset = queryset.filter(username_lower__contains=user_name)

        return queryset

    def handle_no_permission(self):
        return HttpResponseRedirect(settings.LOGIN_URL)

    def get(self, request, *args, **kwargs):
        user_name = request.GET.get("user_name", "").lower()
        queryset = self.get_queryset(user_name)

        admin_creation_form = AdminCreationForm()  # Create an instance of the form

        if self.request.user.role in ("superadmin",):
            context = {"admins": queryset, "username": user_name, "admin_form": admin_creation_form}
            return render(request, self.template_name, context)

        return HttpResponseRedirect(settings.LOGIN_URL)
    
    def post(self, request, *args, **kwargs):
        user_name = request.GET.get("user_name", "").lower()
        queryset = self.get_queryset(user_name)

        admin_creation_form = AdminCreationForm(request.POST)

        if admin_creation_form.is_valid():
            admin_creation_form.save()
            messages.success(request, 'Admin created successfully.')
            return redirect('admin:admins')  # Update with the actual URL name for your admin list view
        else:
            messages.error(request, 'Error creating admin. Please check the form.')

        context = {"admins": queryset, "username": user_name, "admin_form": admin_creation_form}
        return render(request, self.template_name, context)


class UpdateProfilePic(CheckRolesMixin, View):
    http_method_names = ("post",)
    allowed_roles = ("admin",)

    def post(self, request, *args, **kwargs):
        try:
            customer = Users.objects.get(id=request.user.id)
            profile_pic = request.FILES.get("profile_picture")
            if profile_pic:
                customer.profile = profile_pic
                customer.save()

                # messages.success(request, "Profile picture updated successfully.")
                return JsonResponse({'success': True, 'profile': customer.profile.url})
            else:
                return JsonResponse(
                    {"success": False, "errors": {"profile_picture": ["Please select a valid image."]}},
                    status=400,
                )
        except Exception as e:
            # Handle exceptions (e.g., database errors)
            messages.error(request, f"Error updating profile picture: {str(e)}")
            return JsonResponse({"success": False, "errors": {"profile_picture": ["Internal server error."]}}, status=500)


# class LogoutAPIView(APIView):
#     def get(self, request):
#         request.session.clear()

#         return redirect(
#             f"https://{settings.SOCIAL_AUTH_AUTH0_DOMAIN}/v2/logout?"
#             + urlencode(
#                 {
#                     "returnTo": request.build_absolute_uri(reverse("index")),
#                     "client_id": settings.SOCIAL_AUTH_AUTH0_KEY,
#                 },
#                 quote_via=quote_plus,
#             ),
#         )
        


class CustomersTemplateView(CheckRolesMixin,TemplateView):
    template_name = "backend/home/customers.html"
    allowed_roles = ("superadmin","admin")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your context variables for rendering the template
        return context

    
class CustomersDataView(CheckRolesMixin,BaseDatatableView,TemplateView):
    model = Customer
    template_name = "backend/home/customers.html"

    columns = ["created","id",'username','email',"phone_number","country","state","postal_code","balance"]
    order_columns = ['id', 'username', 'email','country','state']
    allowed_roles = ("superadmin", "admin")

    def filter_queryset(self, qs):
        qs = qs.filter(admin__id=self.request.user.id) if self.request.user.role == "admin" else qs
        sSearch = self.request.GET.get('search[value]', None)
        if sSearch:
            qs = qs.filter(Q(username__istartswith=sSearch) | Q(email__istartswith=sSearch))
        return qs
    


