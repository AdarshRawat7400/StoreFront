from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone

from apps.core.auth_mixins import CheckRolesMixin
from apps.core.custom_model_fields import Base64Field
from apps.users.models import Admin, Users
from .forms import CheckoutForm, CouponForm, ProfileUpdateForm, RefundForm
from apps.store.models import Pages, Product, OrderItem, Order, BillingAddress, Coupon , Category
from apps.payments.models import Payment,Refund
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.urls import reverse,reverse_lazy
from django.http import JsonResponse
from django.contrib.auth import authenticate, login,logout



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


class ShopView(ListView):
    model = Product
    paginate_by = 6
    template_name = "frontend/shop.html"


class ItemDetailView(DetailView):
    model = Product
    template_name = "frontend/product-detail.html"


# class CategoryView(DetailView):
#     model = Category
#     template_name = "category.html"

class CategoryView(TemplateView):

    template_name = "frontend/category.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(slug=self.kwargs['slug'])
        item = Product.objects.filter(category=category, is_active=True)
        context['object_list'] = item
        context['category_title'] = category
        context['category_description'] = category.description
        context['category_image_data_uri'] = category.image
        return context

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
                return redirect("frontend:order-summary")
            else:
                order.items.add(order_item)
                messages.info(request, "Item was added to your cart.")
                return redirect("frontend:order-summary")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                customer=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            messages.info(request, "Item was added to your cart.")
        
        return redirect("frontend:order-summary")
    

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
        item = get_object_or_404(Product, slug=slug)
        order_qs = Order.objects.filter(customer=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                ).first()

                if order_item:
                    order.items.remove(order_item)
                    messages.info(request, "Item was removed from your cart.")
                    return redirect("frontend:order-summary")
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
                return redirect("frontend:order-summary")

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
                # Convert the file to base64 and store it in the Base64Field
                base64_data = Base64Field().to_base64(profile_pic)
                customer.profile_pic = base64_data
                customer.save()

                # messages.success(request, "Profile picture updated successfully.")
                return JsonResponse({'success': True, 'base64_image': customer.profile_pic})
            else:
                return JsonResponse(
                    {"success": False, "errors": {"profile_picture": ["Please select a valid image."]}},
                    status=400,
                )
        except Exception as e:
            # Handle exceptions (e.g., database errors)
            messages.error(request, f"Error updating profile picture: {str(e)}")
            return JsonResponse({"success": False, "errors": {"profile_picture": ["Internal server error."]}}, status=500)




class LogoutView(View,CheckRolesMixin):
    allowed_roles = ('superadmin','admin','customer')
    def get(self, request):
        
        redirect_to =  "frontend:home" if request.user.role == 'customer' else "admin:login"
        logout(request)
        return HttpResponseRedirect(reverse_lazy(redirect_to))






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