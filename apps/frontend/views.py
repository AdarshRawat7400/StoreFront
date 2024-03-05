from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from rest_framework.views import APIView
from apps.users.auth import oauth
import secrets
from django.db.models import Q

from django.utils import timezone

from apps.core.auth_mixins import CheckRolesMixin
from apps.core.custom_model_fields import Base64Field
from apps.core.utils import generate_random_password
from apps.users.models import Admin, Users
from .forms import CheckoutForm, CouponForm, ProfileUpdateForm, RefundForm
from apps.store.models import Pages, Product, OrderItem, Order, BillingAddress, Coupon , Category, Review
from apps.payments.models import Payment,Refund
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.urls import reverse,reverse_lazy
from django.http import JsonResponse
from django.contrib.auth import authenticate, login,logout
from django.db.models import Max, Min, F, ExpressionWrapper, fields
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string

from django.http import HttpResponse





# Create your views here.
import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


class PaymentView(CheckRolesMixin,TemplateView):
    template_name = "frontend/payment.html"
    allowed_roles = ('customer',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['DISPLAY_COUPON_FORM'] = False
        if 'order' not in context:
            try:
                order = Order.objects.get(customer=self.request.user, ordered=False)
                context['order'] = order
            except Order.DoesNotExist:
                messages.error(self.request, "You do not have an active order")
                context['order'] = None
        return context

    def get(self, *args, **kwargs):
        context = self.get_context_data()
        if context['order'] and context['order'].billing_address:
            return self.render_to_response(context)
        else:
            messages.warning(self.request, "You have not added a billing address")
            return redirect("frontend:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(customer=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                source=token
            )
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "Order was successful")
            return redirect("/")
        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")
        except stripe.error.RateLimitError:
            messages.error(self.request, "RateLimitError")
            return redirect("/")
        except stripe.error.InvalidRequestError:
            messages.error(self.request, "Invalid parameters")
            return redirect("/")
        except stripe.error.AuthenticationError:
            messages.error(self.request, "Not Authentication")
            return redirect("/")
        except stripe.error.APIConnectionError:
            messages.error(self.request, "Network Error")
            return redirect("/")
        except stripe.error.StripeError:
            messages.error(self.request, "Something went wrong")
            return redirect("/")
        except Exception:
            messages.error(self.request, "Serious Error occurred")
            return redirect("/")
        
class HomeView(ListView,CheckRolesMixin):
    allowed_roles = ('customer',)
    template_name = "frontend/index.html"
    queryset = Product.objects.filter(is_active=True)
    context_object_name = 'items'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)        
        if self.request.user.is_authenticated and self.request.user.role in ['admin','superadmin']:
            logout(self.request)

        return context




class OrderSummaryView(CheckRolesMixin, TemplateView):
    template_name = 'frontend/order_summary.html'
    allowed_roles = ('customer',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            order = Order.objects.get(customer=self.request.user, ordered=False)
            context['object'] = order
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")
        
        return context


# class ShopView(ListView):
#     model = Product
#     paginate_by = 6
#     template_name = "frontend/shop.html"



class ShopView(ListView):
    template_name = "frontend/shop.html"
    model = Product
    context_object_name = 'object_list'
    paginate_by = 20  # Number of items to display per page

    def get_queryset(self):
        sid = self.request.GET.get('sid', '')
        items = Product.objects.filter( is_active=True)
        discount_percentage = self.request.GET.get('dp', 20)
        rating = self.request.GET.get('rtg', 3)
        sorting = self.request.GET.get('sorting')

        max_price_limit = Product.objects.filter(is_active=True).aggregate(Max('price'))['price__max']
        min_price_limit = Product.objects.filter(is_active=True).aggregate(Min('price'))['price__min']


        max_price = int(self.request.GET.get('maxp', max_price_limit)) + 1
        min_price = int(self.request.GET.get('minp', min_price_limit)) - 1

        discounted_products = items.annotate(
            discount_percentage=ExpressionWrapper(
                (F('price') - F('discounted_price')) / F('price') * 100,
                output_field=fields.DecimalField()
            ))

        discounted_products = discounted_products.filter(
            is_active=True,
            price__range=[min_price, max_price],
        )

        if sorting:
            if sorting == 'low_to_high':
                discounted_products = discounted_products.order_by('price')
            elif sorting == 'high_to_low':
                discounted_products = discounted_products.order_by('-price')
        else:
            discounted_products = discounted_products.order_by('-created')

        return discounted_products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        discount_percentage = self.request.GET.get('dp', 20)
        rating = self.request.GET.get('rtg', 3)
        sorting = self.request.GET.get('sorting')
        max_price_limit = Product.objects.filter(is_active=True).aggregate(Max('price'))['price__max']
        min_price_limit = Product.objects.filter(is_active=True).aggregate(Min('price'))['price__min']

        context['max_price_limit'] = int(max_price_limit)
        context['min_price_limit'] = int(min_price_limit)
        context['max_price'] = int(self.request.GET.get('maxp', max_price_limit)) + 1
        context['min_price'] = int(self.request.GET.get('minp', min_price_limit)) - 1
        context['rating'] = rating
        context['discount_percentage'] = discount_percentage
        context['sorting'] = sorting
        context['pagination'] = True  # Indicate that pagination is enabled
        
        return context

    def post(self, request, **kwargs):
        items = self.get_queryset()
        page = request.POST.get('page')
        if not page:
            return JsonResponse({'data': None})

        paginator = Paginator(items, self.paginate_by)

        try:
            items = paginator.page(page)
        except EmptyPage:
            return JsonResponse({'data': None})

        # Render each product item using render_to_string
        product_items_html = ""
        for item in items:
            product_items_html += render_to_string('frontend/product_item.html', {'item': item})

        return JsonResponse({'data': product_items_html})  



class ItemDetailView(DetailView):
    model = Product
    template_name = "frontend/product-detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_item = None
        if self.request.user.is_authenticated:
            product = kwargs.get('object')
            order_item = OrderItem.objects.filter(customer=self.request.user,item=product, ordered=False).first()

        # Add additional context data here
        # For example, you can pass related objects or any other data you need
        context['related_items_list'] = Product.objects.filter(category=self.object.category)[:10]
        context['order_item'] = order_item
        # context['special_offer'] = self.object.is_on_sale()

        return context


# class CategoryView(DetailView):
#     model = Category
#     template_name = "category.html"


class CategoryView(ListView):
    template_name = "frontend/category.html"
    model = Product
    context_object_name = 'object_list'
    paginate_by = 10  # Number of items to display per page

    def get_queryset(self):
        search_term = self.request.GET.get('q', '')
        sid = self.request.GET.get('sid', '')
        category = Category.objects.get(slug=self.kwargs['slug'])
        items = Product.objects.filter(category=category, is_active=True)
        discount_percentage = self.request.GET.get('dp', 20)
        rating = self.request.GET.get('rtg', 3)
        sorting = self.request.GET.get('sorting')

        max_price_limit = Product.objects.filter(category=category, is_active=True).aggregate(Max('price'))['price__max']
        min_price_limit = Product.objects.filter(category=category, is_active=True).aggregate(Min('price'))['price__min']

        if search_term:
            items = items.filter(
                Q(name__icontains=search_term) | Q(brand__icontains=search_term) | Q(manufacturer__icontains=search_term)
            )

        max_price = int(self.request.GET.get('maxp', max_price_limit)) + 1
        min_price = int(self.request.GET.get('minp', min_price_limit)) - 1

        discounted_products = items.annotate(
            discount_percentage=ExpressionWrapper(
                (F('price') - F('discounted_price')) / F('price') * 100,
                output_field=fields.DecimalField()
            ))

        discounted_products = discounted_products.filter(
            category=category,
            is_active=True,
            price__range=[min_price, max_price],
        )

        if sid:
            product = Product.objects.filter(id=sid).first()
            if product:
                self.search_term = product.name

        if sorting:
            if sorting == 'low_to_high':
                discounted_products = discounted_products.order_by('price')
            elif sorting == 'high_to_low':
                discounted_products = discounted_products.order_by('-price')
        else:
            discounted_products = discounted_products.order_by('-created')

        return discounted_products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add additional context variables if needed
        search_term = self.request.GET.get('q', '')
        sid = self.request.GET.get('sid', '')
        category = Category.objects.get(slug=self.kwargs['slug'])
        discount_percentage = self.request.GET.get('dp', 20)
        rating = self.request.GET.get('rtg', 3)
        sorting = self.request.GET.get('sorting')
        max_price_limit = Product.objects.filter(category=category, is_active=True).aggregate(Max('price'))['price__max']
        min_price_limit = Product.objects.filter(category=category, is_active=True).aggregate(Min('price'))['price__min']

        context['category_title'] = category
        context['category_description'] = category.description
        context['category_image_data_uri'] = category.image.url
        context['category_slug'] = self.kwargs['slug']
        context['max_price_limit'] = int(max_price_limit)
        context['min_price_limit'] = int(min_price_limit)
        context['max_price'] = int(self.request.GET.get('maxp', max_price_limit)) + 1
        context['min_price'] = int(self.request.GET.get('minp', min_price_limit)) - 1
        context['rating'] = rating
        context['discount_percentage'] = discount_percentage
        context['search_term'] = search_term
        context['sorting'] = sorting
        context['pagination'] = True  # Indicate that pagination is enabled
        

        return context

    def post(self, request, **kwargs):
        items = self.get_queryset()
        page = request.POST.get('page')
        if not page:
            return JsonResponse({'data': None})

        paginator = Paginator(items, self.paginate_by)

        try:
            items = paginator.page(page)
        except EmptyPage:
            return JsonResponse({'data': None})

        # Render each product item using render_to_string
        product_items_html = ""
        for item in items:
            product_items_html += render_to_string('frontend/product_item.html', {'item': item})

        return JsonResponse({'data': product_items_html})  

class CheckoutView(CheckRolesMixin, TemplateView):
    template_name = 'frontend/checkout.html'
    allowed_roles = ('customer',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            order = Order.objects.get(customer=self.request.user, ordered=False)
            form = CheckoutForm()
            context.update({
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            })
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("frontend:checkout")

        return context

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(customer=self.request.user, ordered=False)
            print(self.request.POST)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')

                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    customer=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                    address_type='B'
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                # Add redirect to the selected payment option
                if payment_option == 'S':
                    return redirect('frontend:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('frontend:payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('frontend:checkout')
            messages.error(
                        self.request, "Form Details Not Correct ,Please Check")
            return redirect('frontend:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("frontend:order-summary")



# def home(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "index.html", context)
#
#
# def products(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "product-detail.html", context)
#
#
# def shop(request):
#     context = {
#         'items': Item.objects.all()
#     }
#     return render(request, "shop.html", context)



class AddToCartView(CheckRolesMixin,View):
    allowed_roles=('customer',)
    def get(self, request, slug):
        referer = request.META.get('HTTP_REFERER')
        item = get_object_or_404(Product, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            customer=request.user,
            ordered=False
        )
        order_qs = Order.objects.filter(customer=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "Item qty was updated.")
                return redirect(referer)
            else:
                order.items.add(order_item)
                messages.info(request, "Item was added to your cart.")
                return redirect(referer)
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                customer=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            messages.info(request, "Item was added to your cart.")
        
        return redirect(referer)
    

    def post(self, request, slug):
        item = get_object_or_404(Product, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            customer=request.user,
            ordered=False
        )
        order_qs = Order.objects.filter(customer=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                message = "Item quantity was updated."
            else:
                order.items.add(order_item)
                message = "Item was added to your cart."
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                customer=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            message = "Item was added to your cart."

        data = {'message': message}
        return JsonResponse(data)
    
class RemoveFromCartView(CheckRolesMixin,View):
    allowed_roles = ('customer',)
    def get(self, request, slug):
        referer = request.META.get('HTTP_REFERER')
        item = get_object_or_404(Product, slug=slug)
        order_qs = Order.objects.filter(customer=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # Check if the item is in the order
            order_item_quantity = order.items.filter(item__slug=item.slug, ordered=False).first()

            if order_item_quantity:
                # Remove the entire order_item_quantity
                order_item_quantity.delete()

                messages.info(request, "Item was removed from your cart.")
                return redirect(referer)

            # check if the order item is in the order
            # if order.items.filter(item__slug=item.slug).exists():
            #     order_item = OrderItem.objects.filter(
            #         item=item,
            #         customer=request.user,
            #         ordered=False
            #     ).first()

            #     if order_item:
            #         order.items.remove(order_item)
            #         messages.info(request, "Item was removed from your cart.")
                    # return redirect("frontend:order-summary")
            else:
                messages.info(request, "Item was not in your cart.")
                return redirect("frontend:product", slug=slug)
        else:
            messages.info(request, "You don't have an active order.")
            return redirect("frontend:product", slug=slug)

        return redirect("frontend:product", slug=slug)

class RemoveSingleItemFromCartView(CheckRolesMixin,View):
    allowed_roles = ('customer',)
    def get(self, request, slug, *args, **kwargs):
        referer = request.META.get('HTTP_REFERER')

        item = get_object_or_404(Product, slug=slug)
        order_qs = Order.objects.filter(
            customer=request.user,
            ordered=False
        )

        if order_qs.exists():
            order = order_qs[0]

            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    customer=request.user,
                    ordered=False
                ).first()

                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                else:
                    order.items.remove(order_item)

                messages.info(request, "This item qty was updated.")
                return redirect(referer)

            else:
                messages.info(request, "Item was not in your cart.")
                return redirect("frontend:product", slug=slug)

        else:
            messages.info(request, "You don't have an active order.")
            return redirect("frontend:product", slug=slug)

def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        return None


class AddCouponView(CheckRolesMixin,View):
    allowed_roles = ('customer',)
    def post(self,request, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    customer=self.request.user, ordered=False)
                coupon = get_coupon(self.request, code)
                if not coupon:
                    messages.info(request, "This coupon does not exist")
                    return redirect("frontend:checkout")
                order.coupon =coupon
                
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("frontend:checkout")

            except ObjectDoesNotExist:
                messages.info(request, "You do not have an active order")
                return redirect("frontend:checkout")


class RequestRefundView(CheckRolesMixin,TemplateView):
    template_name = 'frontend/request_refund.html'
    allowed_roles = ('customer',)

    
    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            form = RefundForm()
            context['form'] = form
            
        except Exception:
            pass

        return context


    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received")
                return redirect("frontend:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist")
                return redirect("frontend:request-refund")




class ProfileEditView(CheckRolesMixin, TemplateView):
    allowed_roles = ("customer")
    template_name = 'frontend/profile.html'  # Update with your actual template name
    model = Users  # Update with your actual user profile model if needed
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('frontend:profile')  # Replace 'profile' with the actual URL name for the user's profile page

    def post(self, request, *args, **kwargs):
        form = ProfileUpdateForm(request.POST, instance=request.user)  # Pass instance for updating existing user
        msg = None
        success = False

        if form.is_valid():
            user = form.save(commit=False)
            if not user.admin:
                admin = Admin.objects.first()
                user.role = 'customer'
                user.admin = admin

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





class UpdateProfilePic(CheckRolesMixin, View):
    http_method_names = ("post",)
    allowed_roles = ("customer",)

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


class FooterPagesView(TemplateView):
    template_name = 'frontend/footer_with_content.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category = self.kwargs.get('category')
        slug = self.kwargs.get('slug')

        # Fetch the specific page based on category and slug
        page = Pages.objects.filter(category=category, slug=slug, is_active=True).first()

        # Add the page object to the context
        context['page'] = page
        return context
    


    
class Auth0LoginAPIView(APIView):
    def get(self, request):

        return oauth.auth0.authorize_redirect(
            request, request.build_absolute_uri(reverse("frontend:auth0-callback"))
        )
    

class Auth0SignupAPIView(APIView):
    def get(self, request):

        random_state = secrets.token_urlsafe(16)

        # Replace 'SOCIAL_AUTH_AUTH0_DOMAIN', 'SOCIAL_AUTH_AUTH0_CLIENT_ID', etc. with your actual settings keys
        auth0_signup_url = (
            f"https://{settings.SOCIAL_AUTH_AUTH0_DOMAIN}/authorize?"
            f"response_type=code&"
            f"client_id={settings.SOCIAL_AUTH_AUTH0_CLIENT_ID}&"
            f"redirect_uri={request.build_absolute_uri(reverse('frontend:auth0-callback'))}&"
            f"scope={'%20'.join(settings.SOCIAL_AUTH_AUTH0_SCOPE)}&"
            f"state={random_state}&"
            f"screen_hint=signup"
        )

        return redirect(auth0_signup_url)

        # Redirect the user to the Auth0 signup URL
        return redirect(auth0_signup_url)
    

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
            return redirect('frontend:home')

        # Handle the case where authentication fails
        return redirect('frontend:login')  # Redirect to the login page or handle accordingly


class LogoutView(View,CheckRolesMixin):
    allowed_roles = ('customer')
    def get(self, request):
        
        redirect_to =  "frontend:home"
        logout(request)
        return HttpResponseRedirect(reverse_lazy(redirect_to))
    


    
class ProductSearchAjaxView(View):
    http_method_names = ("post",)

    def post(self, request, *args, **kwargs):
        term = request.POST.get("term")
        if term:
            products = Product.objects.filter(
                Q(name__icontains=term) | Q(brand__icontains=term) | Q(manufacturer__icontains=term)
            )[:10] 
            results = [
                {
                    "value": product.id,
                     "product_name": f'{product.name}',
                     "category_name" : f'{product.category.name}',
                     "url": reverse('frontend:category', kwargs={'slug': product.category.slug}) + f'?q={term}&sid={product.id}'
                } for product in products
            ]
        else:
            results =[]
        return JsonResponse(results, safe=False)


class ReviewsAjaxView(View):
    def get(self, request, *args, **kwargs):

        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        product_id = request.GET.get('product_id')
        reviews = self.get_paginated_reviews(page, per_page,product_id)
        total_reviews,total_pages = self.get_total_pages(per_page,product_id)
        response_data = {
            'reviews': reviews,
            'total_pages': total_pages,
            'total_reviews' : total_reviews,
        }

        return JsonResponse(response_data)

    def post(self, request, *args, **kwargs):
        user = request.user  # Assuming you have a logged-in user
        product_id = int(request.POST.get('product_id'))  # Adjust based on your form data
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')

        # Assuming you have a method to create a new review in your model
        review = Review.objects.create(user=user, product_id=product_id, rating=rating, comment=comment)

        response_data = {
            'user': str(review.user),
            'rating': review.rating,
            'comment': review.comment,
        }

        return JsonResponse(response_data)

    def get_paginated_reviews(self, page, per_page,product_id):
        reviews_query = Review.objects.filter(product__id=product_id).order_by('-id')
        paginator = Paginator(reviews_query, per_page)
        
        try:
            reviews = paginator.page(page)
        except EmptyPage:
            reviews = paginator.page(paginator.num_pages)

        serialized_reviews = self.serialize_reviews(reviews)
        return serialized_reviews

    def get_total_pages(self, per_page,product_id):
        total_reviews = Review.objects.filter(product__id=product_id).count()
        return (total_reviews,(total_reviews + per_page - 1) // per_page)

    def serialize_reviews(self, reviews):
        serialized_reviews = []
        for review in reviews:
            serialized_reviews.append({
                'user': str(review.user),
                'rating': review.rating,
                'comment': review.comment,
            })
        return serialized_reviews